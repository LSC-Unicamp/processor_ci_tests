"""Convert ACT4 self-checking ELFs to sparse ProcessorCI package metadata.

The ACT4 tohost convention is retained. This module does not claim that an
unadapted FPGA controller can load arbitrary ELF segments or report stop cause.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_advanced import elf_segments, symbols


def classify_tohost(value: int | None, *, stopped: bool, timed_out: bool = False, trapped: bool = False) -> str:
    if timed_out:
        return "TIMEOUT"
    if trapped:
        return "UNEXPECTED_TRAP"
    if not stopped or value is None or value == 0:
        return "INCONCLUSIVE"
    if value == 1:
        return "PASS"
    if value & 1:
        return "SELF_CHECK_FAILURE"
    return "INVALID_TEST"


def convert(elf: Path, *, isa: str, revision: str, max_cycles: int = 100000) -> dict:
    if not isa or not revision or max_cycles <= 0:
        raise ValueError("ISA, ACT4 revision and positive cycle limit are required")
    entry, segments = elf_segments(elf)
    syms = symbols(elf)
    if "tohost" not in syms:
        raise ValueError("ACT4 ELF has no tohost symbol")
    tohost = syms["tohost"]
    if not any(s["address"] <= tohost and tohost + 8 <= s["address"] + s["memory_size"] for s in segments):
        raise ValueError("tohost is not within a LOAD segment")
    return {"schema_version": 1, "test_source": "ACT4", "test_id": elf.stem,
            "isa": isa, "entry": entry, "segments": segments,
            "oracle": {"type": "act4_tohost", "address": tohost, "pass_value": 1, "failure_rule": "odd value greater than 1"},
            "completion": {"type": "tohost_write", "max_cycles": max_cycles},
            "provenance": {"upstream": "https://github.com/riscv/riscv-arch-test", "revision": revision},
            "hardware_execution": "pending"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("elf", type=Path)
    parser.add_argument("--isa", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--max-cycles", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(convert(args.elf, isa=args.isa, revision=args.revision, max_cycles=args.max_cycles), indent=2) + "\n")
