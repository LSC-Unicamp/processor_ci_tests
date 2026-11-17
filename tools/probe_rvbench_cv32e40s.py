"""Probe ACT prerequisites using RV-Bench's pinned CV32E40S and wrapper."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT.parent / "RV-Bench"
CORE = BENCH / "cores/cv32e40s"
WRAPPER = BENCH / "overlay/cv32e40s/wrappers/cv32e40s.sv"
CONFIG = BENCH / "config/cores/cv32e40s.json"
INTERNAL = BENCH / "tools/wrappers/internal"

PROGRAM = r"""
    .section .text
    .globl _start
    .option norvc
_start:
    li s0, 0
    csrr s1, mstatus
    csrr t0, misa
    li t1, 0x40901104
    bne t0, t1, fail
    csrr t0, mvendorid
    li t1, 0x602
    bne t0, t1, fail
    csrr t0, marchid
    li t1, 0x15
    bne t0, t1, fail
    csrr t0, mimpid
    bnez t0, fail
    csrr t0, mhartid
    bnez t0, fail
    la t0, trap_handler
    csrw mtvec, t0
    csrr t1, mtvec
    bne t0, t1, fail
    ori t1, t0, 3
    csrw mtvec, t1
    csrr t2, mtvec
    bne t2, t0, fail
    csrw mtvec, t0
    li t6, 1
    sw t6, 64(zero)
    ecall
    li t0, 1
    bne s0, t0, fail
    li t0, 7
    li t1, 6
    mul t2, t0, t1
    li t3, 42
    bne t2, t3, fail
    div t2, t3, t1
    bne t2, t0, fail
    li t0, 1
    .option rvc
    c.addi t0, 2
    .option norvc
    li t1, 3
    bne t0, t1, fail
    li t0, 0x12345678
    li t1, 129
    sw t0, 0(t1)
    lw t2, 0(t1)
    bne t0, t2, fail
    li t6, 2
    sw t6, 64(zero)
    li s0, 2
    la t0, user_code
    csrw mepc, t0
    li t0, 0x1800
    csrc mstatus, t0
    mret
user_code:
    # With zero PMP regions, U-mode instruction fetch must be denied.
    j fail
machine_resume:
    li t6, 3
    sw t6, 64(zero)
    li t0, 3
    bne s0, t0, fail
pass:
    sw s1, 72(zero)
    li t1, 5
    sw t1, 60(zero)
1:  j 1b
fail:
    li t1, 3
    sw t1, 60(zero)
2:  j 2b
    .balign 128
trap_handler:
    csrr t1, mcause
    sw t1, 68(zero)
    li t2, 11
    beq t1, t2, trap_m_ecall
    li t2, 1
    beq t1, t2, trap_u_fetch_denied
    j fail
trap_m_ecall:
    csrr t1, mtval
    bnez t1, fail
    csrr t1, mepc
    addi t1, t1, 4
    csrw mepc, t1
    li s0, 1
    mret
trap_u_fetch_denied:
    li t2, 2
    bne s0, t2, fail
    csrr t1, mepc
    la t2, user_code
    bne t1, t2, fail
    la t1, machine_resume
    csrw mepc, t1
    li t1, 0x1800
    csrs mstatus, t1
    li s0, 3
    mret
"""


def run() -> dict:
    config = json.loads(CONFIG.read_text())
    for executable in ("riscv64-elf-gcc", "riscv64-elf-objcopy", "verilator", "make", "git"):
        if not shutil.which(executable):
            raise RuntimeError(f"missing {executable}")
    revision = subprocess.check_output(["git", "-C", str(CORE), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(["git", "-C", str(CORE), "status", "--porcelain"], text=True).strip():
        raise RuntimeError("CV32E40S checkout is modified")
    with tempfile.TemporaryDirectory(prefix="act4-cv32e40s-") as tmp:
        work = Path(tmp)
        (work / "probe.S").write_text(PROGRAM)
        subprocess.run(["riscv64-elf-gcc", "-nostdlib", "-nostartfiles", "-static",
                        "-Wl,--build-id=none", "-Wl,-Ttext=0", "-Wl,--no-relax",
                        "-Wl,-e,_start", "-march=rv32imc_zicsr", "-mabi=ilp32",
                        str(work / "probe.S"), "-o", str(work / "probe.elf")],
                       check=True, capture_output=True, text=True)
        subprocess.run(["riscv64-elf-objcopy", "-O", "binary", str(work / "probe.elf"),
                        str(work / "probe.bin")], check=True, capture_output=True, text=True)
        binary = (work / "probe.bin").read_bytes()
        if len(binary) > 4096:
            raise RuntimeError("probe exceeds wrapper validation instruction memory")
        padded = binary + bytes((-len(binary)) % 4)
        internal = work / "internal"
        shutil.copytree(INTERNAL, internal)
        (internal / "memory.hex").write_text("".join(
            f"{int.from_bytes(padded[i:i+4], 'little'):08x}\n"
            for i in range(0, len(padded), 4)))

        # Load RV-Bench's own wrapper simulator in an isolated build with a
        # private instruction image; no RV-Bench source or shared image changes.
        package = types.ModuleType("core")
        package.__path__ = [str(BENCH / "tools/wrappers/core")]
        package.BUILD_DIR = str(work / "build")
        package.INTERNAL_DIR = str(internal)
        sys.modules["core"] = package
        sys.path.insert(0, str(BENCH / "tools/wrappers"))
        from core.hdl_process import validate_wrapper_simulation

        files = [str(CORE / name) for name in (config.get("sim_files") or config["files"])]
        include = [f"-I{CORE}"] + [f"-I{CORE / name}" for name in config["include_dirs"]]
        result = validate_wrapper_simulation(
            "cv32e40s", files, include, wrapper_path=WRAPPER, config_path=CONFIG,
            second_memory=True, build_dir=work / "build", simulation_cycles=1200,
            trace_all_writes=True, timeout=240)
        mstatus_write = re.search(r"WRITE:0x00000048,0x([0-9A-Fa-f]{8})", result["stdout_tail"])
        if result["status"] == "pass" and mstatus_write is None:
            raise RuntimeError("probe did not record the initial mstatus value")
        report = {
            "core": "cv32e40s", "source_revision": revision,
            "wrapper": str(WRAPPER.relative_to(BENCH)),
            "wrapper_sha256": hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
            "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "program": "machine ISA/IDs and mtvec WARL, MRET to U-mode fetch denial, mul/div, c.addi, misaligned SW/LW",
            "checks": ["machine_isa_and_ids", "mtvec_reserved_mode_preserves_previous", "machine_ecall_trap_return",
                       "rv32m_mul_div", "compressed_c_addi", "misaligned_word_store_load",
                       "u_mode_fetch_fault_with_zero_pmp"],
            "initial_mstatus_observed": (int(mstatus_write.group(1), 16) if mstatus_write else None),
            "status_address": 60, "pass_value": 5, "fail_value": 3,
            "result": {key: result[key] for key in ("status", "stage", "reason", "stdout_tail", "stderr_tail")},
        }
        if result["status"] != "pass":
            raise RuntimeError(json.dumps(report, indent=2))
        return report


if __name__ == "__main__":
    report = run()
    output = ROOT / "reports/act4-cv32e40s-rvbench-probe.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{report['core']}: {report['result']['status']} ({report['result']['reason']})")
