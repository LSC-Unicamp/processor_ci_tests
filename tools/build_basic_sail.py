"""Build the dedicated basic tranche and independently execute it in Sail."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from basic_cases import CASES, source
from build_advanced import elf_segments, symbols
from vector_cases import CASE_PROFILES as ZVE32X_PROFILES
from vector_higher_cases import CASE_PROFILES as HIGHER_VECTOR_PROFILES
from vector_fp_cases import CASE_PROFILES as VECTOR_FP_PROFILES

CASE_PROFILES = {**ZVE32X_PROFILES, **HIGHER_VECTOR_PROFILES, **VECTOR_FP_PROFILES}

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import initial_memory, outcome
SAIL = Path(os.environ.get("SAIL_RISCV_SIM", Path.home() / ".local/processorci-sail-0.13.1/bin/sail_riscv_sim"))
CONFIG = ROOT / "third_party_repositories/riscv-arch-test/config/sail/sail-RVI20U32/sail.json"
CONFIG64 = ROOT / "third_party_repositories/riscv-arch-test/config/sail/sail-RVI20U64/sail.json"
CONFIG_Z = ROOT / "third_party_repositories/riscv-arch-test/config/sail/sail-rv32-max/sail.json"
CONFIG_Z64 = ROOT / "third_party_repositories/riscv-arch-test/config/sail/sail-rv64-max/sail.json"
GCC = os.environ.get("BASIC_RISCV_GCC", "riscv64-elf-gcc")
OBJDUMP = GCC.removesuffix("gcc") + "objdump"
DISASSEMBLED_INSTRUCTION = re.compile(
    r"^\s*[0-9a-f]+:\s+([0-9a-f]+)\s+([a-z][a-z0-9.]*)\s*(.*)$", re.I)


def target_encoding(disassembly: str, target: str) -> str:
    """Return an actual target opcode with the required 16- or 32-bit width."""
    mnemonic = "c.addi" if target == "c.nop" else target
    digits = 4 if target.startswith("c.") else 8
    for line in disassembly.splitlines():
        match = DISASSEMBLED_INSTRUCTION.match(line)
        if not match or match[2] != mnemonic or len(match[1]) != digits:
            continue
        if target == "c.nop" and not (match[1] == "0001" and match[3].startswith("zero,0")):
            continue
        return match[1]
    raise RuntimeError(f"{target} has no {digits * 4}-bit opcode in ELF disassembly")


def build(output: Path = ROOT / "build/basic-sail") -> dict:
    if not (SAIL.is_file() and CONFIG.is_file() and shutil.which(GCC) and shutil.which(OBJDUMP)):
        raise RuntimeError("Sail 0.13.1, its ACT 4.1 config and RISC-V GCC/binutils are required")
    output.mkdir(parents=True, exist_ok=True)
    def display(path: Path) -> str:
        return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    results = []
    for group, target, march, expected, body in CASES:
        xlen = 64 if group.startswith("RV64") else 32
        config = (CONFIG_Z64 if group.startswith("RV64Zve") else CONFIG_Z
                  if group.startswith(("RV32Zb", "RV32Zve")) else
                  CONFIG64 if xlen == 64 else CONFIG)
        src = ROOT / "tests" / group / "basic" / "package_src" / f"{target}.S"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text(source((group, target, march, expected, body)))
        elf = output / f"{group}-{target}.elf"
        subprocess.run([GCC, "-nostdlib", "-static", f"-march={march}", "-mabi=lp64" if xlen == 64 else "-mabi=ilp32",
                        "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)],
                       check=True, capture_output=True, text=True)
        disasm = subprocess.check_output([OBJDUMP, "-M", "no-aliases", "-d", str(elf)], text=True)
        opcode_hex = target_encoding(disasm, target)
        width_bits = len(opcode_hex) * 4
        run = subprocess.run([str(SAIL), "--config", str(config), str(elf)],
                             capture_output=True, text=True, timeout=10)
        if run.returncode != 0 or "SUCCESS" not in run.stdout:
            raise RuntimeError(f"Sail rejected {group}/{target}: {run.stdout} {run.stderr}")
        entry, segments = elf_segments(elf)
        status = symbols(elf)["tohost"]
        package = {"schema_version": 1, "test_source": "basic", "test_id": f"{group}-{target}",
                   "isa": march, "target_instruction": target, "instruction_bits": width_bits,
                   "target_opcode_hex": opcode_hex, "entry": entry, "segments": segments,
                   "oracle": {"type": "selfcheck_tohost", "address": status, "pass_value": 1,
                              "failure_rule": "odd value greater than 1"},
                   "completion": {"type": "tohost_write", "max_cycles": 200000 if
                                  re.match(r"(?:vl|vs|vmv)[1248](?:re|r)", target) else 10000},
                   "expected_a0": expected & ((1 << xlen) - 1), "reference_model": "Sail 0.13.1",
                   "required_privilege": "M" if group == "RV32Zicsr" or group.startswith(("RV32Zve", "RV64Zve")) else None,
                   "reference_validated": True, "hardware_execution": "pending"}
        if group.startswith(("RV32Zve", "RV64Zve")):
            package["vector_profile"] = CASE_PROFILES.get(target, {
                "extension": group.removeprefix("RV32"), "minimum_vlen_bits": 128,
                "sew_bits": 32, "lmul": "m1", "vl": 4,
                "reference_vlen_bits": 1024})
        memory = initial_memory(package, supported_isa={march})
        if outcome(package, memory, stopped=False) != "INCONCLUSIVE":
            raise RuntimeError(f"uninitialized package status for {target}")
        memory[status] = 1
        if outcome(package, memory, stopped=True) != "PASS":
            raise RuntimeError(f"host package status failure for {target}")
        (output / f"{group}-{target}.json").write_text(json.dumps(package, indent=2) + "\n")
        results.append({"group": group, "instruction": target, "source": str(src.relative_to(ROOT)),
                        "elf": display(elf), "package": display(output / f'{group}-{target}.json'),
                        "compiled": True, "disassembly_verified": True,
                        "instruction_bits": width_bits, "target_opcode_hex": opcode_hex,
                        "sail_validated": True,
                        "host_mock_validated": True})
    report = {"tests": len(results), "compiled": len(results), "sail_validated": len(results),
              "host_mock_validated": len(results), "hardware_validated": 0, "results": results}
    if output.resolve() == (ROOT / "build/basic-sail").resolve():
        destination = ROOT / "reports/basic-sail-summary.json"
        destination.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    result = build()
    print(f"Basic Sail: {result['sail_validated']}/{result['tests']} independently executed")
