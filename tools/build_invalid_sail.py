"""Build and run observable M-mode trap tests for exceptional encodings."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from build_advanced import elf_segments, symbols
from build_basic_sail import CONFIG, CONFIG64, CONFIG_Z, GCC, OBJDUMP, ROOT, SAIL, target_encoding
from riscv_test_runner.core.package import TRAP_FAILURE_CODES, initial_memory, outcome

CASES = [("ecall", "rv32i_zicsr", 11),
         ("ebreak", "rv32i_zicsr", 3),
         ("c.ebreak", "rv32ic_zicsr", 3),
         ("illegal32", "rv32i_zicsr", 2),
         ("illegal16", "rv32ic_zicsr", 2),
         ("illegal_csr", "rv32i_zicsr", 2),
         ("u_mode_mret", "rv32i_zicsr", 2),
         ("u_mode_machine_csr", "rv32i_zicsr", 2),
         ("misaligned_load", "rv32i_zicsr", 4),
         ("misaligned_store", "rv32i_zicsr", 6),
         ("fp_disabled_fadd", "rv32if_zicsr", 2),
         ("fp_disabled_fadd_d", "rv32ifd_zicsr", 2),
         ("readonly_csr_write", "rv32i_zicsr", 2),
         ("amo_misaligned_word", "rv32ia_zicsr", 7),
         ("rv64_illegal32", "rv64i_zicsr", 2),
         ("rv64_fp_disabled_fadd_s", "rv64if_zicsr", 2),
         ("rv64_fp_disabled_fadd_d", "rv64ifd_zicsr", 2),
         ("rv64_amo_misaligned_double", "rv64ia_zicsr", 7),
         ("vector_disabled_vset", "rv32im_zicsr_zve32x_zvl128b", 2)]

CASE_GROUPS = {"illegal16": "RV32C", "fp_disabled_fadd": "RV32F",
               "fp_disabled_fadd_d": "RV32D", "readonly_csr_write": "RV32Zicsr",
               "amo_misaligned_word": "RV32A", "rv64_illegal32": "RV64I",
               "rv64_fp_disabled_fadd_s": "RV64F", "rv64_fp_disabled_fadd_d": "RV64D",
               "rv64_amo_misaligned_double": "RV64A",
               "vector_disabled_vset": "RV32Zve32x"}

LEGACY_REPLACEMENTS = {
    "illegal32": "tests/RV32I/invalid/src/000-invalid1.s",
    "illegal16": "tests/RV32C/invalid/src/000-invalid1.s",
    "fp_disabled_fadd": "tests/RV32F/invalid/src/000-invalid1.s",
}

ALLOW_MISALIGNED_CONFIG = ROOT / "tools/config/allow-misaligned.json"


def source(target: str, cause: int) -> str:
    instruction = {"illegal32": ".word 0xffffffff", "illegal16": ".hword 0x0000",
                   "illegal_csr": "csrr t5, 0xfff",
                   "u_mode_mret": "mret", "u_mode_machine_csr": "csrr t5, mscratch",
                   "misaligned_load": "lw t5, 1(t4)",
                   "misaligned_store": "sw t5, 1(t4)",
                   "fp_disabled_fadd": "fadd.s ft2, ft0, ft1",
                   "fp_disabled_fadd_d": "fadd.d ft2, ft0, ft1",
                   "readonly_csr_write": "csrrw zero, marchid, t5",
                   "amo_misaligned_word": "amoadd.w t5, t6, (t4)",
                   "rv64_illegal32": ".word 0xffffffff",
                   "rv64_fp_disabled_fadd_s": "fadd.s ft2, ft0, ft1",
                   "rv64_fp_disabled_fadd_d": "fadd.d ft2, ft0, ft1",
                   "rv64_amo_misaligned_double": "amoadd.d t5, t6, (t4)",
                   "vector_disabled_vset": "vsetivli t0, 4, e32, m1, ta, ma"}.get(target, target)
    setup = ("li t1, -1\ncsrw pmpaddr0, t1\nli t1, 0x1f\n"
             "csrw pmpcfg0, t1\nla t0, trigger\ncsrw mepc, t0\nli t1, 0x1800\n"
             "csrc mstatus, t1\nmret\n" if target.startswith("u_mode_") else "")
    if target.startswith("misaligned_"):
        setup = "la t4, misaligned_operand\nli t5, 0x12345678\n"
    if target.startswith("amo_misaligned_") or target.startswith("rv64_amo_misaligned_"):
        setup = "la t4, misaligned_operand\naddi t4, t4, 1\nli t6, 7\n"
    if target == "readonly_csr_write":
        setup = "li t5, 1\n"
    data = ('.section .data\n.balign 4\nmisaligned_operand: .word 0xabcdef01, 0x23456789\n'
            if target.startswith(("misaligned_", "amo_misaligned_")) else
            '.section .data\n.balign 8\nmisaligned_operand: .dword 0xabcdef0123456789, 0x23456789abcdef01\n'
            if target.startswith("rv64_amo_misaligned_") else "")
    return f'''# Expected M-mode trap for {target}; mcause={cause}; mepc=trigger.
.section .text
.global _start
_start:
la t0, trap_handler
csrw mtvec, t0
{setup}
trigger:
{instruction}
j missing_trap
.balign 4
trap_handler:
csrr t1, mcause
li t2, {cause}
bne t1, t2, wrong_cause
csrr t1, mepc
la t2, trigger
bne t1, t2, wrong_mepc
li t1, 1
j report
missing_trap:
li t1, 3
j report
wrong_cause:
li t1, 5
j report
wrong_mepc:
li t1, 7
report:
la t2, tohost
sw t1, 0(t2)
sw zero, 4(t2)
1: j 1b
.section .tohost,"aw",@progbits
.balign 8
.global tohost
tohost: .dword 0
.global fromhost
fromhost: .dword 0
{data}
'''


def build(output: Path = ROOT / "build/invalid-sail") -> dict:
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for target, march, cause in CASES:
        group = CASE_GROUPS.get(target, "RV32I")
        src = ROOT / "tests" / group / "invalid/package_src" / f"{target}.S"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text(source(target, cause))
        elf = output / f"{target}.elf"
        subprocess.run([GCC, "-nostdlib", "-static", f"-march={march}",
                        "-mabi=lp64" if march.startswith("rv64") else "-mabi=ilp32",
                        "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)],
                       check=True, capture_output=True, text=True)
        disasm = subprocess.check_output([OBJDUMP, "-M", "no-aliases", "-d", str(elf)], text=True)
        expected_mnemonic = ("csrrs" if target in ("illegal_csr", "u_mode_machine_csr") else
                             "csrrw" if target == "readonly_csr_write" else
                             "fadd.s" if target in ("fp_disabled_fadd", "rv64_fp_disabled_fadd_s") else
                             "fadd.d" if target in ("fp_disabled_fadd_d", "rv64_fp_disabled_fadd_d") else
                             "amoadd.w" if target == "amo_misaligned_word" else
                             "amoadd.d" if target == "rv64_amo_misaligned_double" else
                             "vsetivli" if target == "vector_disabled_vset" else
                             "mret" if target == "u_mode_mret" else
                             "lw" if target == "misaligned_load" else
                             "sw" if target == "misaligned_store" else target)
        if target not in ("illegal32", "illegal16", "rv64_illegal32") and not re.search(r"\s" + re.escape(expected_mnemonic) + r"\s", disasm):
            raise RuntimeError(f"{target} absent from disassembly")
        if target == "illegal_csr" and "0xfff" not in disasm:
            raise RuntimeError("reserved CSR address absent from disassembly")
        if target == "u_mode_machine_csr" and "mscratch" not in disasm:
            raise RuntimeError("machine CSR address absent from disassembly")
        if target == "c.ebreak" and target_encoding(disasm, target) != "9002":
            raise RuntimeError("c.ebreak does not have its 16-bit encoding")
        if target.startswith("misaligned_") and not re.search(
                r"\s" + expected_mnemonic + r"\s+t5,1\(t4\)", disasm):
            raise RuntimeError("misaligned trigger operand absent from disassembly")
        config = (CONFIG_Z if target.startswith("u_mode_") or target == "vector_disabled_vset"
                  else CONFIG64 if march.startswith("rv64") else CONFIG)
        run = subprocess.run([str(SAIL), "--config", str(config), str(elf)],
                             capture_output=True, text=True, timeout=10)
        if run.returncode or "SUCCESS" not in run.stdout:
            raise RuntimeError(f"trap test failed {target}: {run.stdout} {run.stderr}")
        no_trap_rejected = None
        if target.startswith("misaligned_"):
            negative = subprocess.run([str(SAIL), "--config", str(config),
                                       "--config-override", str(ALLOW_MISALIGNED_CONFIG), str(elf)],
                                      capture_output=True, text=True, timeout=10)
            no_trap_rejected = negative.returncode != 0 and "FAILURE: 1 " in negative.stdout
            if not no_trap_rejected:
                raise RuntimeError(f"allow-misaligned negative case did not fail: {target}")
        entry, segments = elf_segments(elf)
        syms = symbols(elf)
        if target in ("illegal32", "illegal16", "rv64_illegal32"):
            trigger = syms["trigger"]
            width = 2 if target == "illegal16" else 4
            raw = next((bytes.fromhex(seg["hex"])[trigger - seg["address"]:trigger - seg["address"] + width]
                        for seg in segments if seg["address"] <= trigger < seg["address"] + seg["file_size"]), b"")
            if raw != (b"\x00\x00" if target == "illegal16" else b"\xff\xff\xff\xff"):
                raise RuntimeError("illegal instruction encoding absent from ELF")
        package = {"schema_version": 1, "test_source": "invalid", "test_id": f"trap-{target}",
                   "source_path": str(src.relative_to(ROOT)),
                   "isa": march, "required_privilege": "M", "expected_trap_cause": cause,
                   "trigger_privilege": "U" if target.startswith("u_mode_") else "M",
                   "expected_mepc": syms["trigger"], "entry": entry, "segments": segments,
                   "oracle": {"type": "trap_selfcheck_tohost", "address": syms["tohost"], "pass_value": 1,
                              "failure_rule": "odd value greater than 1",
                              "trap_failure_codes": TRAP_FAILURE_CODES},
                   "completion": {"type": "tohost_write", "max_cycles": 10000},
                   "reference_config": str(config.relative_to(ROOT)),
                   "misalignment_policy": "AlignmentException" if "misaligned" in target else None,
                   "reference_model": "Sail 0.13.1", "reference_validated": True,
                   "hardware_execution": "pending"}
        if target in LEGACY_REPLACEMENTS:
            package["replaces_legacy_placeholder"] = LEGACY_REPLACEMENTS[target]
        memory = initial_memory(package, supported_isa={march})
        if outcome(package, memory, stopped=False) != "INCONCLUSIVE":
            raise RuntimeError(f"invalid initial trap status: {target}")
        memory[syms["tohost"]] = 1
        if outcome(package, memory, stopped=True) != "PASS":
            raise RuntimeError(f"host trap status failure: {target}")
        for value, expected in ((3, "EXPECTED_TRAP_MISSING"), (5, "UNEXPECTED_TRAP"),
                                (7, "ARCHITECTURAL_MISMATCH")):
            memory[syms["tohost"]] = value
            if outcome(package, memory, stopped=True) != expected:
                raise RuntimeError(f"host trap failure classification failed: {target}/{value}")
        (output / f"{target}.json").write_text(json.dumps(package, indent=2) + "\n")
        results.append({"instruction": target, "mcause": cause, "mepc_verified": True,
                        "replaces_legacy_placeholder": LEGACY_REPLACEMENTS.get(target),
                        "allow_misaligned_negative_rejected": no_trap_rejected,
                        "compiled": True, "sail_validated": True, "host_mock_validated": True})
    report = {"cases": len(results), "sail_validated": len(results),
              "trap_failure_codes": TRAP_FAILURE_CODES, "results": results}
    (ROOT / "reports/invalid-sail-summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    result = build()
    print(f"Expected traps: {result['sail_validated']}/{result['cases']} Sail validated")
