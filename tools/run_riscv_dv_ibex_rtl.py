"""Replay saved riscv-dv packages on Ibex plus Controller RTL.

Stages a simulation-only copy of the existing Ibex wrapper with shared RAM
and byte enables. The adjacent RV-Bench checkout is read-only.
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
from riscv_test_runner.core.package import flat_memory_fit, initial_memory, outcome
from riscv_test_runner.riscv_dv import verify_saved_package


CORE = RV_BENCH / "cores/ibex"
WRAPPER = RV_BENCH / "overlay/ibex/wrappers/ibex.sv"
CONTROLLER = RV_BENCH / "tools/controller"
CORE_REVISION = "19592a1fc7ba7e85427906cd4d86b8356b91a45d"
CORE_ISA = "rv32imc_zicsr_zifencei"
STATUS = re.compile(r"IBEX_CONTROLLER_STATUS ([0-9a-fA-F]{8}) CYCLE (\d+)")


def stage_wrapper(work: Path) -> Path:
    text = WRAPPER.read_text()
    replacements = (
        ("`define ENABLE_SECOND_MEMORY", "`define ENABLE_SECOND_MEMORY\n`define ENABLE_BYTE_SELECT"),
        ("    .MEMORY_SIZE        (`MEMORY_SIZE)",
         "    .MEMORY_SIZE        (`MEMORY_SIZE),\n    .SHARED_MEMORY      (1)"),
        ("    .core_we_i          (core_we),",
         "    .core_we_i          (core_we),\n    .core_sel_i         (core_sel),"),
        ("    .data_mem_we_i      (data_mem_we),",
         "    .data_mem_we_i      (data_mem_we),\n    .data_mem_sel_i     (data_mem_sel),"),
        ("    .instr_gnt_i            (_core_ack),",
         "    .instr_gnt_i            (core_ack),"),
        ("    .data_gnt_i             (_data_mem_ack),",
         "    .data_gnt_i             (data_mem_ack),"),
        ("    .rst_ni                 (~rst_core),",
         "    .rst_ni                 (rst_n),"),
        ("    .scan_rst_ni            (~rst_core)",
         "    .scan_rst_ni            (rst_n)"),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise RuntimeError(f"Ibex wrapper changed; review staging marker: {old}")
        text = text.replace(old, new, 1)
    staged = work / "ibex_processorci_top.sv"
    staged.write_text(text)
    return staged


def compile_rtl(work: Path) -> tuple[Path, str]:
    revision = subprocess.check_output(["git", "-C", str(CORE), "rev-parse", "HEAD"],
                                       text=True).strip()
    if revision != CORE_REVISION:
        raise RuntimeError(f"Ibex source revision {revision} differs from tested {CORE_REVISION}")
    (work / "processor_ci_defines.vh").write_text("\n".join((
        "`define CLOCK_FREQ 1000000", "`define BIT_RATE 100000",
        "`define PAYLOAD_BITS 8", "`define BUFFER_SIZE 8",
        "`define PULSE_CONTROL_BITS 24", "`define BUS_WIDTH 32",
        "`define WORD_SIZE_BY 4", "`define ID 32'h1",
        "`define RESET_CLK_CYCLES 20", '`define MEMORY_FILE "memory.hex"',
        "`define MEMORY_SIZE 524288", "",
    )))
    wrapper = stage_wrapper(work)
    config = json.loads((RV_BENCH / "config/cores/ibex.json").read_text())
    core_files = [CORE / name for name in config["files"]]
    controller_rtl = CONTROLLER / "rtl"
    controller_files = [controller_rtl / name for name in (
        "controller.sv", "interpreter.sv", "memory.sv", "clk_divider.sv", "timer.sv", "fifo.sv")]
    uart = CONTROLLER / "modules/UART/rtl"
    communication = ROOT.parent / "processor_ci_communication"
    sources = [*core_files, *controller_files,
               communication / "protocol/hardware/modules/uart.sv",
               uart / "uart_rx.v", uart / "uart_tx.v", wrapper,
               ROOT / "validation_tests/rtl/riscv_dv_ibex_controller_tb.sv"]
    includes = [work, CORE, *(CORE / name for name in config["include_dirs"])]
    obj = work / "obj"
    cmd = ["verilator", "--binary", "--timing", "-j", "4", "-Wno-fatal",
           "-DPIPELINED_WISHBONE", "-DENABLE_SECOND_MEMORY", "-DENABLE_BYTE_SELECT",
           "--top-module", "riscv_dv_ibex_controller_tb",
           "--Mdir", str(obj), *(f"-I{path}" for path in includes),
           *(item for path in includes[2:] for item in ("-y", str(path))),
           *(str(path) for path in sources)]
    result = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise RuntimeError("Ibex Controller RTL compile failed:\n" +
                           "\n".join(result.stderr.splitlines()[-40:]))
    return obj / "Vriscv_dv_ibex_controller_tb", hashlib.sha256(wrapper.read_bytes()).hexdigest()


def run(manifests: list[Path], output: Path) -> dict:
    if not manifests or not shutil.which("verilator"):
        raise ValueError("one or more manifests and Verilator are required")
    rows = []
    with tempfile.TemporaryDirectory(prefix="riscv-dv-ibex-") as directory:
        work = Path(directory)
        binary, staged_wrapper_sha256 = compile_rtl(work)
        for manifest in manifests:
            package, digest = verify_saved_package(manifest.parent)
            reasons = flat_memory_fit(package, base=0, size=ACT_MEMORY_BYTES,
                                      reset_pc=0x80, supported_isa={CORE_ISA})
            if reasons:
                raise ValueError("package incompatible with Ibex RAM: " + "; ".join(reasons))
            memory = initial_memory(package, supported_isa={CORE_ISA})
            words = (int.from_bytes(bytes(memory.get(address + lane, 0)
                                         for lane in range(4)), "little")
                     for address in range(0, ACT_MEMORY_BYTES, 4))
            (work / "memory.hex").write_text("".join(f"{word:08x}\n" for word in words))
            status = package["oracle"]["address"]
            result = subprocess.run([str(binary), f"+status={status:08x}"], cwd=work,
                                    capture_output=True, text=True, timeout=60)
            match = STATUS.search(result.stdout)
            observed_status = int(match.group(1), 16) if match else None
            observed = dict(memory)
            if observed_status is not None:
                for lane, byte in enumerate(observed_status.to_bytes(4, "little")):
                    observed[status + lane] = byte
            classified = (outcome(package, observed, stopped=True)
                          if observed_status is not None else "INCONCLUSIVE")
            passed = result.returncode == 0 and classified == "PASS"
            rows.append({"test_id": package["test_id"], "package": str(manifest),
                         "manifest_sha256": digest, "isa": package["isa"],
                         "outcome": classified if passed else "RTL_FAILURE",
                         "tohost": observed_status,
                         "cycles": int(match.group(2)) if match else None,
                         "returncode": result.returncode,
                         "stdout_head": "\n".join(result.stdout.splitlines()[:65]),
                         "stdout_tail": "\n".join(result.stdout.splitlines()[-20:]),
                         "stderr_tail": "\n".join(result.stderr.splitlines()[-20:])})
            print(f"{len(rows)}/{len(manifests)} {package['test_id']}: {rows[-1]['outcome']}",
                  flush=True)
    report = {"tool": "riscv-dv", "core": "Ibex", "core_revision": CORE_REVISION,
              "wrapper_sha256": hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
              "staged_wrapper_sha256": staged_wrapper_sha256,
              "wrapper_adaptations": ["shared 512 KiB RAM", "byte enables",
                                      "immediate bus grant with registered response",
                                      "explicit core reset edge"],
              "controller_sha256": hashlib.sha256((CONTROLLER / "rtl/controller.sv").read_bytes()).hexdigest(),
              "memory_bytes": ACT_MEMORY_BYTES, "memory_mode": "shared two-port simulation staging",
              "reset_pc": 0x80, "image_load": "direct simulation preload",
              "controller_rtl_execution": True, "fpga_execution": False,
              "validated": sum(row["outcome"] == "PASS" for row in rows),
              "failed": sum(row["outcome"] != "PASS" for row in rows), "tests": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/riscv-dv-ibex-controller-rtl.json")
    args = parser.parse_args()
    report = run([path.resolve() for path in args.package], args.output.resolve())
    if report["failed"]:
        raise SystemExit(1)
