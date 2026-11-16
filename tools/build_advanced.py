"""Build, disassemble, execute and package the explicit advanced corpus offline."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

from advanced_cases import CASES, source, source_group

ROOT = Path(__file__).resolve().parents[1]
PREFIX = os.environ.get("RISCV_TOOL_PREFIX", "riscv32-unknown-elf-")
SOURCES = ROOT / "tests" / "RV32I" / "advanced" / "src" / "scenarios"


def elf_segments(path: Path) -> tuple[int, list[dict]]:
    blob = path.read_bytes()
    if blob[:4] != b"\x7fELF" or blob[5] != 1:
        raise ValueError("not a little-endian ELF")
    bits = blob[4]
    if bits == 1:
        entry = struct.unpack_from("<I", blob, 24)[0]
        phoff = struct.unpack_from("<I", blob, 28)[0]
        phentsize, phnum = struct.unpack_from("<HH", blob, 42)
        fmt = "<IIIIIIII"
    elif bits == 2:
        entry = struct.unpack_from("<Q", blob, 24)[0]
        phoff = struct.unpack_from("<Q", blob, 32)[0]
        phentsize, phnum = struct.unpack_from("<HH", blob, 54)
        fmt = "<IIQQQQQQ"
    else:
        raise ValueError("unsupported ELF class")
    segments = []
    for i in range(phnum):
        fields = struct.unpack_from(fmt, blob, phoff + i * phentsize)
        if bits == 1:
            kind, offset, vaddr, paddr, size, memsize, flags, _ = fields
        else:
            kind, flags, offset, vaddr, paddr, size, memsize, _ = fields
        if kind == 1:
            if offset + size > len(blob) or size > memsize:
                raise ValueError("malformed LOAD segment")
            segments.append({"address": paddr, "virtual_address": vaddr, "file_size": size,
                             "memory_size": memsize, "flags": flags, "hex": blob[offset:offset + size].hex()})
    if not segments or not any(s["address"] <= entry < s["address"] + s["memory_size"] for s in segments):
        raise ValueError("entry outside LOAD segments")
    return entry, segments


def symbols(path: Path) -> dict[str, int]:
    out = subprocess.check_output([PREFIX + "nm", str(path)], text=True)
    return {parts[2]: int(parts[0], 16) for line in out.splitlines() if len(parts := line.split()) == 3 and re.fullmatch(r"[0-9a-fA-F]+", parts[0])}


def build(out: Path, run_reference: bool = True) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)
    results = []
    for case in CASES:
        name, category, march, expected, body = case
        xlen = 64 if march.startswith("rv64") else 32
        group = source_group(case)
        source_dir = ROOT / "tests" / group / "advanced/src/scenarios"
        source_dir.mkdir(parents=True, exist_ok=True)
        src = source_dir / f"{name}.S"
        src.write_text(source(case))
        elf = out / f"{name}.elf"
        command = [PREFIX + "gcc", "-nostdlib", "-static", "-Wl,-Ttext=0x0", "-Wl,--no-relax", "-Wl,--build-id=none", f"-march={march}", "-mabi=lp64" if xlen == 64 else "-mabi=ilp32", str(src), "-o", str(elf)]
        row = {"id": name, "category": category, "source": str(src.relative_to(ROOT)), "march": march,
               "expected_a0": expected & ((1 << xlen) - 1), "initial_state": "initialized in source",
               "completion": "status_word_then_ecall", "reference_model": f"qemu-riscv{xlen} user mode"}
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            disasm = subprocess.check_output([PREFIX + "objdump", "-M", "no-aliases", "-d", str(elf)], text=True)
            targets = [m for m in re.findall(r"^\s*(?:[a-z][a-z0-9.]*)", body, re.M) if m.strip() not in {"li", "la", "j"}]
            missing = [m for m in targets if not re.search(r"\s" + re.escape(m.strip()) + r"\s", disasm)]
            if missing:
                raise ValueError(f"target instruction absent from disassembly: {missing}")
            entry, segments = elf_segments(elf)
            syms = symbols(elf)
            row.update({"entry": entry, "completion_address": syms["completion"], "status_address": syms["result_status"],
                        "status_pass": 1, "status_fail": 2, "segments": segments, "compiled": True,
                        "disassembly_verified": True})
            if run_reference:
                proc = subprocess.run([f"qemu-riscv{xlen}", str(elf)], capture_output=True, timeout=5)
                row["reference_validated"] = proc.returncode == 0
                if proc.returncode:
                    row["error"] = f"QEMU exit {proc.returncode}: {proc.stderr.decode(errors='replace')}"
            else:
                row["reference_validated"] = False
                row["error"] = "QEMU unavailable"
            (out / f"{name}.json").write_text(json.dumps(row, indent=2) + "\n")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as exc:
            row["compiled"] = False
            row["reference_validated"] = False
            row["error"] = str(exc.stderr if isinstance(exc, subprocess.CalledProcessError) else exc)
        results.append(row)
    sail_report = ROOT / "reports/advanced-sail-summary.json"
    sail_validated = json.loads(sail_report.read_text())["sail_validated"] if sail_report.exists() else 0
    report = {"cases": len(results), "compiled": sum(r["compiled"] for r in results),
              "qemu_validated": sum(r["reference_validated"] for r in results),
              "spike_sail_validated": sail_validated, "hardware_validated": 0,
              "results": [{k: v for k, v in r.items() if k != "segments"} for r in results]}
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "advanced")
    args = parser.parse_args()
    if not shutil.which("qemu-riscv32"):
        raise SystemExit("qemu-riscv32 required for offline execution")
    report = build(args.output)
    print(f"{report['compiled']}/{report['cases']} compiled; {report['qemu_validated']} QEMU validated")
    for row in report["results"]:
        if "error" in row:
            print(row["id"], row["error"])
    raise SystemExit(0 if report["qemu_validated"] == report["cases"] else 1)
