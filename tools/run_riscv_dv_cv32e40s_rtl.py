"""Replay saved riscv-dv packages on CV32E40S plus Controller RTL.

The runner reuses the existing ACT CV32E40S simulation harness, but loads
riscv-dv packages directly. It does not alter the core or RV-Bench checkout.
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

from run_act4_cv32e40s_controller_rtl import (ACT_MEMORY_BYTES, CONTROLLER,
                                               CORE, ROOT, WRAPPER, compile_rtl)

sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import flat_memory_fit, initial_memory, outcome
from riscv_test_runner.riscv_dv import symbol, verify_saved_package


CORE_ISA = "rv32imc_zicsr_zifencei"
PASS_LINE = re.compile(r"ACT_CONTROLLER_STATUS ([0-9a-fA-F]{8}) CYCLE (\d+)")


def package_image(manifest: Path) -> tuple[dict, dict[int, int], str]:
    package, digest = verify_saved_package(manifest.parent)
    if package["entry"] != 0:
        raise ValueError("CV32E40S wrapper resets at PC zero")
    reasons = flat_memory_fit(package, base=0, size=ACT_MEMORY_BYTES,
                              reset_pc=0, supported_isa={CORE_ISA})
    if reasons:
        raise ValueError("package incompatible with CV32E40S RAM: " + "; ".join(reasons))
    memory = initial_memory(package, supported_isa={CORE_ISA})
    return package, memory, digest


def corrupt_first_register_expectation(manifest: Path, memory: dict[int, int]) -> int:
    """Flip one bit in the first integer comparison's immediate, in memory only."""
    elf = manifest.parent / "program.elf"
    pc = symbol(elf, "riscv32-unknown-elf-nm", "test_done")
    instruction = int.from_bytes(bytes(memory[pc + lane] for lane in range(4)), "little")
    # The selected RV32I package starts checks with ADDI rd, x0, immediate.
    if instruction & 0x7f != 0x13 or (instruction >> 15) & 0x1f != 0:
        raise ValueError("first register expectation is not ADDI from x0")
    if (instruction >> 7) & 0x1f == 0:
        raise ValueError("first register expectation writes x0")
    changed = instruction ^ (1 << 20)
    for lane, byte in enumerate(changed.to_bytes(4, "little")):
        memory[pc + lane] = byte
    return pc


def run(manifests: list[Path], output: Path, *, inject_register_mismatch: bool = False,
        serial_full_load: bool = False) -> dict:
    if not manifests:
        raise ValueError("at least one manifest is required")
    if inject_register_mismatch and len(manifests) != 1:
        raise ValueError("register mismatch probe requires one package")
    if inject_register_mismatch and serial_full_load:
        raise ValueError("register mismatch probe requires direct simulation preload")
    if not shutil.which("verilator"):
        raise RuntimeError("Verilator is required")
    rows = []
    with tempfile.TemporaryDirectory(prefix="riscv-dv-cv32e40s-") as directory:
        work = Path(directory)
        binary = compile_rtl(work, serial=serial_full_load,
                             serial_load=serial_full_load)
        for manifest in manifests:
            package, memory, digest = package_image(manifest)
            mutation_pc = None
            expected_status = 1
            if inject_register_mismatch:
                if not package["isa"].startswith("rv32i_"):
                    raise ValueError("register mismatch probe requires an RV32I package")
                mutation_pc = corrupt_first_register_expectation(manifest, memory)
                expected_status = 3
            words = (int.from_bytes(bytes(memory.get(address + lane, 0)
                                         for lane in range(4)), "little")
                     for address in range(0, ACT_MEMORY_BYTES, 4))
            (work / "memory.hex").write_text("".join(f"{word:08x}\n" for word in words))
            if serial_full_load:
                segments = package["segments"]
                if len(segments) > 64 or any(s["address"] % 4 for s in segments):
                    raise ValueError("UART segment loader needs at most 64 word-start-aligned segments")
                shutil.copyfile(work / "memory.hex", work / "host_image.hex")
                (work / "ranges.hex").write_text("".join(
                    f"{segment['address']:08x}\n{(segment['memory_size'] + 3) // 4:08x}\n"
                    for segment in segments))
            status = package["oracle"]["address"]
            run_args = [str(binary), f"+status={status:08x}",
                        f"+expected={expected_status:08x}"]
            if serial_full_load:
                run_args += ["+serial_load", f"+segment_count={len(segments)}"]
            result = subprocess.run(run_args, cwd=work, capture_output=True,
                                    text=True, timeout=180 if serial_full_load else 60)
            pattern = (re.compile(r"ACT_SERIAL_STATUS ([0-9a-fA-F]{8}) DIAGNOSTIC_BYTES (\d+)")
                       if serial_full_load else PASS_LINE)
            match = pattern.search(result.stdout)
            passed = (result.returncode == 0 and match is not None
                      and int(match.group(1), 16) == expected_status)
            observed_status = int(match.group(1), 16) if match else None
            observed = dict(memory)
            if observed_status is not None:
                for lane, byte in enumerate(observed_status.to_bytes(4, "little")):
                    observed[status + lane] = byte
            classified = (outcome(package, observed, stopped=True)
                          if observed_status is not None else "INCONCLUSIVE")
            expected_outcome = "SELF_CHECK_FAILURE" if inject_register_mismatch else "PASS"
            passed = passed and classified == expected_outcome
            rows.append({
                "test_id": package["test_id"],
                "package": str(manifest),
                "manifest_sha256": digest,
                "isa": package["isa"],
                "outcome": classified if passed else "RTL_FAILURE",
                "expected_outcome": expected_outcome,
                "mutation_pc": mutation_pc,
                "tohost": observed_status,
                "cycles": int(match.group(2)) if match and not serial_full_load else None,
                "diagnostic_bytes": int(match.group(2)) if match and serial_full_load else None,
                "returncode": result.returncode,
                "stdout_tail": "\n".join(result.stdout.splitlines()[-25:]),
                "stderr_tail": "\n".join(result.stderr.splitlines()[-25:]),
            })
            print(f"{len(rows)}/{len(manifests)} {package['test_id']}: {rows[-1]['outcome']}",
                  flush=True)
    report = {
        "tool": "riscv-dv",
        "core": "CV32E40S",
        "core_revision": subprocess.check_output(["git", "-C", str(CORE),
                                                  "rev-parse", "HEAD"], text=True).strip(),
        "wrapper_sha256": hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
        "controller_sha256": hashlib.sha256((CONTROLLER / "rtl/controller.sv").read_bytes()).hexdigest(),
        "memory_bytes": ACT_MEMORY_BYTES,
        "memory_mode": "shared two-port",
        "image_load": "UART sparse segment upload" if serial_full_load else "direct simulation preload",
        "controller_rtl_execution": True,
        "serial_execution": serial_full_load,
        "fpga_execution": False,
        "validated": sum(row["outcome"] == row["expected_outcome"] for row in rows),
        "failed": sum(row["outcome"] != row["expected_outcome"] for row in rows),
        "tests": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, action="append", required=True,
                        help="saved riscv-dv manifest.json; repeat for multiple packages")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/riscv-dv-cv32e40s-controller-rtl.json")
    parser.add_argument("--inject-register-mismatch", action="store_true",
                        help="flip one expected GPR immediate in the simulation image")
    parser.add_argument("--serial-full-load", action="store_true",
                        help="upload saved segments and execute over Controller UART")
    args = parser.parse_args()
    report = run([path.resolve() for path in args.package], args.output.resolve(),
                 inject_register_mismatch=args.inject_register_mismatch,
                 serial_full_load=args.serial_full_load)
    if report["failed"]:
        raise SystemExit(1)
