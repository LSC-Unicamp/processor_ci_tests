"""Check the legacy timer self-check and the ProcessorCI timer RTL unit.

The timer MMIO address is outside Sail's configured devices. This proves the
program image and reference structure plus the timer counter behavior, not a
complete core/controller execution of the program.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from isa_audit import ROOT, legacy_hex
from validate_legacy_advanced_sail import PREFIX, _binary_words

SOURCE = ROOT / "tests/RV32I/advanced/src/040-timer.s"
IMAGE = ROOT / "tests/RV32I/advanced/memory/040-timer.hex"
REFERENCE = ROOT / "tests/RV32I/advanced/reference/040-timer.hex"
CONTROLLER = ROOT.parent / "processor_ci_controller/rtl/controller.sv"
TIMER = ROOT.parent / "processor_ci_controller/rtl/timer.sv"
TESTBENCH = ROOT / "validation_tests/rtl/timer_counter_probe_tb.sv"
OUTPUT = ROOT / "reports/isa-audit/legacy_advanced_timer.json"


def validate(output: Path = OUTPUT, *, write_assets: bool = False) -> dict:
    source = SOURCE.read_text()
    if (source.count("lw t1, 0(t0)") != 1 or source.count("lw t2, 0(t0)") != 1 or
            "li t0, -4" not in source or "sub t3, t2, t1" not in source or
            "sltu t4, zero, t3" not in source or "sw t4, 60(zero)" not in source):
        raise ValueError("timer source no longer checks two reads from 0xfffffffc")
    rtl_available = CONTROLLER.is_file() and TIMER.is_file() and shutil.which("iverilog") and shutil.which("vvp")
    if rtl_available and "(&core_addr_i[31:2]) ? timer_data_out" not in CONTROLLER.read_text():
        raise ValueError("controller no longer selects timer data at 0xfffffffc")
    with tempfile.TemporaryDirectory(prefix="processorci-legacy-timer-") as temporary:
        temp = Path(temporary)
        obj, elf, binary, simulation = (temp / name for name in
                                        ("timer.o", "timer.elf", "timer.bin", "timer.vvp"))
        subprocess.run([PREFIX + "as", "-march=rv32i", str(SOURCE), "-o", str(obj)],
                       check=True, capture_output=True, text=True)
        subprocess.run([PREFIX + "ld", "-m", "elf32lriscv", "-Ttext=0", str(obj), "-o", str(elf)],
                       check=True, capture_output=True, text=True)
        subprocess.run([PREFIX + "objcopy", "-O", "binary", str(elf), str(binary)],
                       check=True, capture_output=True, text=True)
        words = _binary_words(binary.read_bytes())
        if len(words) > 16:
            raise ValueError("timer program exceeds legacy 64-byte loader window")
        image_status, image_words = legacy_hex(IMAGE)
        if write_assets and (image_status != "words" or image_words != words):
            IMAGE.write_text("".join(f"{word:08x}\n" for word in words))
            image_status, image_words = legacy_hex(IMAGE)
        if image_status != "words" or image_words != words:
            raise ValueError("timer image differs from source")
        reference_status, reference_words = legacy_hex(REFERENCE)
        if write_assets and reference_status != "words":
            REFERENCE.write_text("00000001\n")
            reference_status, reference_words = legacy_hex(REFERENCE)
        if reference_status != "words" or reference_words != [1]:
            raise ValueError("timer self-check requires reference word 1")
        if rtl_available:
            subprocess.run(["iverilog", "-g2012", "-s", "timer_counter_probe_tb", "-o", str(simulation),
                            str(TIMER), str(TESTBENCH)], check=True, capture_output=True, text=True)
            run = subprocess.run(["vvp", str(simulation)], check=True, capture_output=True, text=True)
            if "TIMER_COUNTER_PROBE_PASS" not in run.stdout:
                raise RuntimeError("timer RTL unit probe did not pass")
    report = {"source": str(SOURCE.relative_to(ROOT)),
              "image": str(IMAGE.relative_to(ROOT)),
              "reference": str(REFERENCE.relative_to(ROOT)),
              "source_image_matches": True, "reference_word": "00000001",
              "controller_timer_address": "0xfffffffc" if rtl_available else "unverified",
              "timer_rtl_unit_validated": bool(rtl_available),
              "core_execution": "pending", "reason": "no matched core/controller execution of timer program"}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-assets", action="store_true")
    args = parser.parse_args()
    result = validate(write_assets=args.write_assets)
    print(f"Legacy timer: image/reference matched; RTL unit validated; core execution {result['core_execution']}")
