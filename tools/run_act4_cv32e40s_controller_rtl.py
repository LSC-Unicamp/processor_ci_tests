"""Replay ACT 4.1 packages through the RV-Bench wrapper and real Controller RTL.

The memory image is preloaded for execution testing. Serial transfer is a
separate gate; this run includes the shared RAM, controller bus mux, core, and
write-qualified completion circuit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from build_act4_cv32e40s import ACT_MEMORY_BYTES, ROOT, RV_BENCH
sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import initial_memory

CONTROLLER = RV_BENCH / "tools/controller"
COMMUNICATION = ROOT.parent / "processor_ci_communication"
WRAPPER = RV_BENCH / "overlay/cv32e40s/wrappers/cv32e40s.sv"
CORE = RV_BENCH / "cores/cv32e40s"


def compile_rtl(work: Path, *, serial: bool = False, serial_load: bool = False) -> Path:
    defines = work / "processor_ci_defines.vh"
    defines.write_text("\n".join((
        "`define CLOCK_FREQ 1000000", "`define BIT_RATE 100000",
        "`define PAYLOAD_BITS 8", "`define BUFFER_SIZE 8",
        "`define PULSE_CONTROL_BITS 24", "`define BUS_WIDTH 32",
        "`define WORD_SIZE_BY 4", "`define ID 32'h1",
        "`define RESET_CLK_CYCLES 20",
        '`define MEMORY_FILE ""' if serial_load else '`define MEMORY_FILE "memory.hex"',
        "`define MEMORY_SIZE 524288", "",
    )))
    config = json.loads((RV_BENCH / "config/cores/cv32e40s.json").read_text())
    core_files = [CORE / name for name in (config.get("sim_files") or config["files"])]
    rtl = CONTROLLER / "rtl"
    controller_files = [rtl / name for name in (
        "controller.sv", "interpreter.sv", "memory.sv", "clk_divider.sv", "timer.sv", "fifo.sv")]
    uart = RV_BENCH / "tools/controller/modules/UART/rtl"
    sources = [*core_files, *controller_files,
               COMMUNICATION / "protocol/hardware/modules/uart.sv",
               uart / "uart_rx.v", uart / "uart_tx.v", WRAPPER,
               ROOT / "validation_tests/rtl/act4_cv32e40s_serial_tb.sv" if serial else
               ROOT / "validation_tests/rtl/act4_cv32e40s_controller_tb.sv"]
    includes = [work, CORE, *(CORE / name for name in config["include_dirs"])]
    obj = work / "obj"
    top = "act4_cv32e40s_serial_tb" if serial else "act4_cv32e40s_controller_tb"
    cmd = ["verilator", "--binary", "--timing", "-j", "4", "-Wno-fatal",
           "-DENABLE_SECOND_MEMORY", "-DENABLE_BYTE_SELECT",
           "--top-module", top, "--Mdir", str(obj),
           *(f"-I{path}" for path in includes), *(str(path) for path in sources)]
    result = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise RuntimeError("Controller/core RTL compile failed:\n" + "\n".join(result.stderr.splitlines()[-30:]))
    return obj / f"V{top}"


def package_memory(package_path: Path, *, inject_addi_failure: bool,
                   inject_illegal: bool = False) -> tuple[dict, dict[int, int], int]:
    package = json.loads(package_path.read_text())
    if package["test_source"] != "ACT4" or package["entry"] != 0:
        raise ValueError("expected reset-zero ACT package")
    memory = initial_memory(package, supported_isa={"rv32i", "rv32im"})
    expected = 1
    if inject_addi_failure or inject_illegal:
        if package["test_id"] != "I-addi-00":
            raise ValueError("directed faults apply only to I-addi-00")
        address = 0x88
        if int.from_bytes(bytes(memory[address + i] for i in range(4)), "little") != 0x2FC00413:
            raise RuntimeError("ACT ADDI check encoding changed")
        replacement = 0 if inject_illegal else 0x2FD00413
        for i, byte in enumerate(replacement.to_bytes(4, "little")):
            memory[address + i] = byte
        expected = 3
    if max(memory) >= ACT_MEMORY_BYTES:
        raise ValueError("ACT image exceeds 512 KiB")
    return package, memory, expected


def run(package_paths: list[Path], output: Path, *, inject_addi_failure: bool = False,
        inject_illegal: bool = False, serial: bool = False, serial_load: bool = False,
        expect_timeout: bool = False) -> dict:
    if not shutil.which("verilator"):
        raise RuntimeError("Verilator is required")
    rows = []
    with tempfile.TemporaryDirectory(prefix="act4-controller-") as directory:
        work = Path(directory)
        binary = compile_rtl(work, serial=serial, serial_load=serial_load)
        for package_path in package_paths:
            package, memory, expected = package_memory(package_path,
                                                       inject_addi_failure=inject_addi_failure,
                                                       inject_illegal=inject_illegal)
            words = (int.from_bytes(bytes(memory.get(address + i, 0) for i in range(4)), "little")
                     for address in range(0, ACT_MEMORY_BYTES, 4))
            (work / "memory.hex").write_text("".join(f"{word:08x}\n" for word in words))
            if serial_load:
                shutil.copyfile(work / "memory.hex", work / "host_image.hex")
                segments = package["segments"]
                if any(segment["address"] % 4 or segment["memory_size"] % 4 for segment in segments):
                    raise ValueError("UART segment loader needs word-aligned ACT segments")
                (work / "ranges.hex").write_text("".join(
                    f"{segment['address']:08x}\n{segment['memory_size'] // 4:08x}\n" for segment in segments))
            status = package["oracle"]["address"]
            run_args = [str(binary), f"+status={status:08x}", f"+expected={expected:08x}"]
            if serial_load:
                run_args += ["+serial_load", f"+segment_count={len(segments)}"]
            if expect_timeout:
                run_args.append("+expect_timeout")
            result = subprocess.run(run_args, cwd=work, capture_output=True, text=True,
                                    timeout=180 if serial_load else 60)
            pattern = (r"ACT_SERIAL_TIMEOUT ([0-9a-fA-F]{8}) DIAGNOSTIC_BYTES (\d+)" if expect_timeout else
                       r"ACT_SERIAL_STATUS ([0-9a-fA-F]{8}) DIAGNOSTIC_BYTES (\d+)" if serial else
                       r"ACT_CONTROLLER_STATUS ([0-9a-fA-F]{8}) CYCLE (\d+)")
            match = re.search(pattern, result.stdout)
            if result.returncode or not match or int(match.group(1), 16) != expected:
                raise RuntimeError(f"{package['test_id']} controller RTL failed:\n"
                                   + "\n".join((result.stdout + result.stderr).splitlines()[-20:]))
            diagnostic_text = None
            if serial and expected == 3:
                diagnostic_match = re.search(r"ACT_SERIAL_DIAGNOSTICS_BEGIN\n(.*?)\nACT_SERIAL_DIAGNOSTICS_END",
                                             result.stdout, re.S)
                if not diagnostic_match:
                    raise RuntimeError("ACT failure diagnostics were not read through UART")
                diagnostic_text = diagnostic_match.group(1)
            trap_diagnostics = None
            if diagnostic_text and "TRAP FAILURE DIAGNOSTICS" in diagnostic_text:
                cause = re.search(r"XCAUSE:\s+0x([0-9a-fA-F]+)", diagnostic_text)
                epc = re.search(r"XEPC:\s+0x([0-9a-fA-F]+)", diagnostic_text)
                trap_diagnostics = {"cause": int(cause.group(1), 16) if cause else None,
                                    "epc": int(epc.group(1), 16) if epc else None}
            observed_outcome = ("TIMEOUT" if expect_timeout else "UNEXPECTED_TRAP" if trap_diagnostics else
                                "PASS" if expected == 1 else "SELF_CHECK_FAILURE")
            rows.append({"test_id": package["test_id"], "status": expected,
                         "outcome": observed_outcome,
                         "oracle_outcome": "PASS" if expected == 1 else "SELF_CHECK_FAILURE",
                         "cycles": None if serial else int(match.group(2)),
                         "diagnostic_bytes": int(match.group(2)) if serial else None,
                         "diagnostic_text": diagnostic_text,
                         "trap_diagnostics": trap_diagnostics,
                         "package_sha256": hashlib.sha256(package_path.read_bytes()).hexdigest()})
            if len(package_paths) > 1:
                print(f"{len(rows)}/{len(package_paths)} {package['test_id']}: {observed_outcome}", flush=True)
    report = {"core": "RV-Bench CV32E40S", "act_release": "4.1.0",
              "memory_bytes": ACT_MEMORY_BYTES, "memory_mode": "shared two-port",
              "image_load": "UART sparse segment upload" if serial_load else "direct simulation preload",
              "serial_execution": serial, "serial_load_verified": serial_load,
              "controller_rtl_execution": True, "fpga_execution": False,
              "wrapper_sha256": hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
              "controller_sha256": hashlib.sha256((CONTROLLER / "rtl/controller.sv").read_bytes()).hexdigest(),
              "tests": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--inject-addi-failure", action="store_true")
    parser.add_argument("--inject-illegal", action="store_true",
                        help="replace the first checked ADDI with an illegal instruction")
    parser.add_argument("--serial", action="store_true", help="issue execution command over the real UART")
    parser.add_argument("--serial-full-load", action="store_true",
                        help="upload every ELF segment over UART before execution")
    parser.add_argument("--expect-timeout", action="store_true",
                        help="set an unreachable completion address and require timeout")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/act4-cv32e40s-controller-rtl.json")
    args = parser.parse_args()
    if args.serial_full_load:
        args.serial = True
    if args.inject_addi_failure and args.inject_illegal:
        parser.error("choose one injected fault")
    if args.expect_timeout and (args.inject_addi_failure or args.inject_illegal):
        parser.error("timeout probe cannot also inject an instruction fault")
    if args.expect_timeout:
        args.serial = True
    if args.all and args.package or (args.inject_addi_failure or args.inject_illegal) and args.all:
        parser.error("choose --all or --package; induced fault requires one package")
    paths = ([ROOT / "build/act4-cv32e40s/packages/I-addi-00.json"] if not args.package and not args.all else
             sorted((ROOT / "build/act4-cv32e40s/packages").glob("*.json")) if args.all else args.package)
    output = args.output
    if args.serial and output == ROOT / "reports/act4-cv32e40s-controller-rtl.json":
        output = ROOT / ("reports/act4-cv32e40s-controller-serial-timeout.json" if args.expect_timeout else
                         "reports/act4-cv32e40s-controller-serial-full-load.json" if args.serial_full_load else
                         "reports/act4-cv32e40s-controller-serial.json")
    report = run([path.resolve() for path in paths], output.resolve(),
                 inject_addi_failure=args.inject_addi_failure, serial=args.serial,
                 inject_illegal=args.inject_illegal,
                 serial_load=args.serial_full_load, expect_timeout=args.expect_timeout)
    print(f"ACT controller RTL: {len(report['tests'])} cases completed")
