"""Replay legacy RV32 basic sources at address zero under Sail 0.13.1.

The legacy runner stops on a bus write to address 60 and compares reference
words at the preceding addresses. We reproduce that first-write observation,
without treating a comment-only reference or an instruction-limit exit as PASS.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from isa_audit import ROOT, legacy_basic_assets, legacy_hex

SAIL = Path(os.environ.get("SAIL_RISCV_SIM", Path.home() / ".local/processorci-sail-0.13.1/bin/sail_riscv_sim"))
CONFIG = ROOT / "third_party_repositories/riscv-arch-test/config/sail/sail-rv32-max/sail.json"
PREFIX = os.environ.get("RISCV_TOOL_PREFIX", "riscv32-unknown-elf-")
MARCH = {"RV32I": "rv32i", "RV32M": "rv32im", "RV32A": "rv32ia", "RV32C": "rv32ic"}
WRITE = re.compile(r"mem\[([BHW]),0x([0-9a-fA-F]+)\] <- 0x([0-9a-fA-F]+)")


def address_zero_config(config_path: Path = CONFIG) -> str:
    """Give Sail a 64 KiB RAM at zero; retain its separately mapped MMIO."""
    config = config_path.read_text()
    start = config.index("      // ROM\n")
    mmio_start = config.index("      // MMIO\n", start)
    ram_start = config.index("      // RAM\n", mmio_start)
    end = config.index("\n    ]", ram_start)
    rom = config[start:mmio_start].replace('"value": "0x1000"', '"value": "0x10000"', 1)
    ram = config[ram_start:end]
    if ram.count('"value": "0x80000000"') != 2:
        raise ValueError("Sail max memory layout changed")
    ram = ram.replace('"value": "0x80000000"', '"value": "0x0"', 1)
    ram = ram.replace('"value": "0x80000000"', '"value": "0x10000"', 1)
    return config[:start] + ram + ",\n" + rom + config[mmio_start:ram_start].rstrip().rstrip(",") + config[end:]


def observe(binary: bytes, trace: str) -> tuple[bool, dict[int, int]]:
    memory = {offset: byte for offset, byte in enumerate(binary)}
    for line in trace.splitlines():
        match = WRITE.search(line)
        if not match:
            continue
        width = {"B": 1, "H": 2, "W": 4}[match[1]]
        address = int(match[2], 16)
        value = int(match[3], 16)
        for offset in range(width):
            memory[address + offset] = (value >> (8 * offset)) & 0xff
        if address <= 60 < address + width:
            return True, memory
    return False, memory


def validate(output: Path = ROOT / "reports/isa-audit/legacy_basic_sail.json") -> dict:
    if not SAIL.is_file() or not CONFIG.is_file():
        raise RuntimeError("Sail 0.13.1 and ACT 4.1 rv32-max config are required")
    results = []
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        config = temp / "legacy-rv32.json"
        config.write_text(address_zero_config())
        for asset in legacy_basic_assets(ROOT):
            row = {"source": asset["source"], "group": asset["group"],
                   "reference_status": asset["reference_status"],
                   "model_status": "not_run", "expected_words": [], "observed_words": []}
            if not asset["source_has_instructions"] or asset["group"] not in MARCH:
                results.append(row)
                continue
            source = ROOT / asset["source"]
            obj, elf, raw = (temp / name for name in ("test.o", "test.elf", "test.bin"))
            try:
                subprocess.run([PREFIX + "as", f"-march={MARCH[asset['group']]}", str(source),
                                "-o", str(obj)], check=True, capture_output=True, text=True)
                subprocess.run([PREFIX + "ld", "-m", "elf32lriscv", "-Ttext=0", str(obj), "-o", str(elf)],
                               check=True, capture_output=True, text=True)
                subprocess.run([PREFIX + "objcopy", "-O", "binary", str(elf), str(raw)],
                               check=True, capture_output=True, text=True)
                run = subprocess.run([str(SAIL), "--config", str(config), "--inst-limit", "100",
                                      "--trace-mem", str(elf)], capture_output=True, text=True, timeout=10)
            except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
                row["model_status"] = "build_or_run_error"
                row["detail"] = str(exc)[:300]
                results.append(row)
                continue
            stopped, memory = observe(raw.read_bytes(), run.stdout)
            if not stopped:
                row["model_status"] = "sail_error" if run.returncode else "no_completion_write"
                if run.returncode:
                    row["detail"] = (run.stdout + run.stderr)[-300:]
                results.append(row)
                continue
            status, expected = legacy_hex(ROOT / asset["reference"])
            row["expected_words"] = [f"{value:08x}" for value in expected]
            if status != "words":
                row["model_status"] = "reference_placeholder"
                row["observed_words"] = [f"{int.from_bytes(bytes(memory.get(60 + i, 0) for i in range(4)), 'little'):08x}"]
                results.append(row)
                continue
            addresses = range(60 - 4 * (len(expected) - 1), 61, 4)
            observed = [int.from_bytes(bytes(memory.get(address + i, 0) for i in range(4)), "little")
                        for address in addresses]
            row["observed_words"] = [f"{value:08x}" for value in observed]
            row["model_status"] = "match" if observed == expected else "mismatch"
            results.append(row)
    counts = dict(Counter(row["model_status"] for row in results))
    report = {"reference_model": "Sail 0.13.1 rv32-max, 64 KiB address-zero RAM",
              "stop_rule": "first write intersecting byte address 60", "instruction_limit": 100,
              "counts": counts, "results": results}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    report = validate()
    print(report["counts"])
    unexpected = [row for row in report["results"] if row["model_status"] in
                  {"mismatch", "sail_error", "build_or_run_error"} or
                  (row["model_status"] == "no_completion_write" and
                   row["source"] != "tests/RV32I/basic/src/040-timeout.s")]
    if unexpected:
        raise SystemExit("Legacy Sail replay has unexpected outcomes: " +
                         ", ".join(row["source"] for row in unexpected))
