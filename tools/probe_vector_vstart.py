"""Document the configured nonzero-vstart arithmetic behavior of Sail and QEMU."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from advanced_cases import source
from build_advanced import PREFIX
from build_basic_sail import CONFIG_Z, GCC, ROOT, SAIL
from validate_advanced_sail import sail_source
from validate_vector_vlen import profile_override

CASE = (
    "vector_vstart_arith_resume_probe", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
    "vsetivli t0, 4, e32, m1, tu, mu\nvmv.v.i v1, 2\nvmv.v.i v2, 3\n"
    "vmv.v.i v3, 9\nli t1, 2\ncsrrw zero, vstart, t1\n"
    "vadd.vv v3, v1, v2\ncsrrs t1, vstart, zero\nbne t1, zero, failure\n"
    "la t1, vector32_result\nvse32.v v3, (t1)\n"
    "lw t2, 0(t1)\nli t3, 9\nbne t2, t3, failure\n"
    "lw t2, 4(t1)\nbne t2, t3, failure\n"
    "lw t2, 8(t1)\nli t3, 5\nbne t2, t3, failure\n"
    "lw t2, 12(t1)\nbne t2, t3, failure\nli a0, 1",
)
OVERRIDE = ROOT / "tools/config/vector-vstart-arith-resume.json"
OUTPUT = ROOT / "reports/vector-vstart-summary.json"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, timeout=10)


def probe(output: Path = ROOT / "build/vector-vstart-probe", report_path: Path = OUTPUT) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    def display(path: Path) -> str:
        return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    qemu_source = output / "resume-qemu.S"
    qemu_source.write_text(source(CASE))
    qemu_elf = output / "resume-qemu.elf"
    subprocess.run([PREFIX + "gcc", "-nostdlib", "-static", "-Wl,-Ttext=0x0",
                    "-Wl,--no-relax", "-Wl,--build-id=none", f"-march={CASE[2]}",
                    "-mabi=ilp32", str(qemu_source), "-o", str(qemu_elf)],
                   check=True, capture_output=True, text=True)
    disassembly = subprocess.check_output([PREFIX + "objdump", "-M", "no-aliases",
                                           "-d", str(qemu_elf)], text=True)
    if not re.search(r"\svadd\.vv\s", disassembly):
        raise RuntimeError("vadd.vv absent from arithmetic resume probe ELF")
    qemu = _run(["qemu-riscv32", str(qemu_elf)])
    if qemu.returncode != 0:
        raise RuntimeError(f"QEMU arithmetic resume probe failed: {qemu.stderr[-700:]}")

    sail_source_path = output / "resume-sail.S"
    sail_source_path.write_text(sail_source(CASE))
    sail_elf = output / "resume-sail.elf"
    subprocess.run([GCC, "-nostdlib", "-static", f"-march={CASE[2]}", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(sail_source_path),
                    "-o", str(sail_elf)], check=True, capture_output=True, text=True)
    base = [str(SAIL), "--config", str(CONFIG_Z)]
    strict = _run([*base, str(sail_elf)])
    strict_trapped = strict.returncode != 0 and "possible trap loop detected" in strict.stdout
    if not strict_trapped:
        raise RuntimeError(f"Sail strict-vstart behavior changed: {(strict.stdout + strict.stderr)[-700:]}")
    permissive = _run([*base, "--config-override", str(OVERRIDE), str(sail_elf)])
    if permissive.returncode != 0 or "SUCCESS" not in permissive.stdout:
        raise RuntimeError(f"Sail arithmetic resume override failed: {(permissive.stdout + permissive.stderr)[-700:]}")
    zve_override = profile_override("Zve32x")
    zve_override["extensions"]["V"]["vstart"] = {"zero_required": {"arith": False}}
    named_config = output / "resume-zve32x-vlen128.json"
    named_config.write_text(json.dumps(zve_override, indent=2) + "\n")
    named = _run([*base, "--config-override", str(named_config), str(sail_elf)])
    if named.returncode != 0 or "SUCCESS" not in named.stdout:
        raise RuntimeError(f"Sail Zve32x VLEN128 resume failed: {(named.stdout + named.stderr)[-700:]}")
    result = {"scenario": CASE[0], "isa": CASE[2], "qemu_resumed": True,
              "sail_default_arithmetic_vstart_zero_required": True,
              "sail_default_trap_observed": True,
              "sail_arithmetic_resume_override_validated": True,
              "sail_zve32x_vlen128_resume_validated": True,
              "disassembly_verified": True, "hardware_validated": 0,
              "qualification": "Arithmetic resume requires a capability-specific configuration; the default Sail trap-loop observation is diagnostic, not a passing exception test.",
              "source": display(qemu_source),
              "sail_source": display(sail_source_path),
              "config_override": str(OVERRIDE.relative_to(ROOT))}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    report = probe()
    print(f"Vstart arithmetic probe: QEMU and configured Sail resume passed; strict Sail trap observed")
