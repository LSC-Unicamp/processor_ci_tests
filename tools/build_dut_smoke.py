"""Build one small address-zero RV32I package for picorv32 serial bring-up."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from basic_cases import CASES, source
from build_advanced import elf_segments, symbols
from build_basic_sail import CONFIG, GCC, OBJDUMP, ROOT, SAIL
from validate_legacy_basic_sail import address_zero_config
from riscv_test_runner.core.package import flat_memory_fit, initial_memory, outcome

LINKER = ROOT / "tools/linker/dut-smoke-8k.ld"


def build(output: Path = ROOT / "build/dut-smoke") -> dict:
    output.mkdir(parents=True, exist_ok=True)
    case = next(case for case in CASES if case[0] == "RV32I" and case[1] == "addi")
    group, target, march, expected, _ = case
    assembly = output / "picorv32-addi.S"
    assembly.write_text(source(case))
    config = output / "sail-rv32i-zero.json"
    config.write_text(address_zero_config(CONFIG))
    elf = output / "picorv32-addi.elf"
    subprocess.run([GCC, "-nostdlib", "-static", "-Wl,--build-id=none",
                    f"-Wl,-T,{LINKER}", "-Wl,--no-relax", f"-march={march}", "-mabi=ilp32",
                    str(assembly), "-o", str(elf)], check=True, capture_output=True, text=True)
    disasm = subprocess.check_output([OBJDUMP, "-M", "no-aliases", "-d", str(elf)], text=True)
    if not re.search(r"\saddi\s", disasm):
        raise RuntimeError("smoke ELF lacks addi")
    sail = subprocess.run([str(SAIL), "--config", str(config), str(elf)],
                          capture_output=True, text=True, timeout=10)
    if sail.returncode or "SUCCESS" not in sail.stdout:
        raise RuntimeError(f"smoke Sail execution failed: {sail.stdout} {sail.stderr}")
    entry, segments = elf_segments(elf)
    status = symbols(elf)["tohost"]
    package = {"schema_version": 1, "test_source": "basic", "test_id": "picorv32-addi-smoke",
               "isa": march, "target_instruction": target, "entry": entry,
               "segments": segments,
               "oracle": {"type": "selfcheck_tohost", "address": status, "pass_value": 1,
                          "failure_rule": "odd value greater than 1"},
               "completion": {"type": "tohost_write", "max_cycles": 10000},
               "expected_a0": expected, "reference_model": "Sail 0.13.1 RVI20U32 with address-zero RAM",
               "reference_validated": True, "hardware_execution": "pending"}
    reasons = flat_memory_fit(package, base=0, size=8192, reset_pc=0, supported_isa={"rv32i"})
    if reasons:
        raise RuntimeError("smoke package does not fit: " + "; ".join(reasons))
    memory = initial_memory(package, supported_isa={"rv32i"})
    if outcome(package, memory, stopped=False) != "INCONCLUSIVE":
        raise RuntimeError("smoke package initialized with nonzero tohost")
    memory[status] = 1
    if outcome(package, memory, stopped=True) != "PASS":
        raise RuntimeError("smoke package host oracle failed")
    manifest = output / "picorv32-addi.json"
    manifest.write_text(json.dumps(package, indent=2) + "\n")
    report = {"core_candidate": "picorv32", "board_candidate": "digilent_nexys4_ddr",
              "package": str(manifest.relative_to(ROOT)) if manifest.is_relative_to(ROOT) else str(manifest),
              "isa": march, "entry": entry, "tohost": status,
              "load_file_bytes": sum(segment["file_size"] for segment in segments),
              "load_memory_bytes": sum(segment["memory_size"] for segment in segments),
              "memory_limit_bytes": 8192, "sail_validated": True,
              "host_package_validated": True, "static_board_fit": True,
              "hardware_validated": False}
    (ROOT / "reports/dut-smoke-summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    result = build()
    print(f"DUT smoke: Sail PASS, {result['load_memory_bytes']}/8192 LOAD bytes, tohost={result['tohost']:#x}")
