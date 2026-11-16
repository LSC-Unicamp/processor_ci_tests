"""Validate legacy RV32M and RV32I control-flow advanced tests at address zero.

The reference word is the first write to address 60. Arithmetic expectations
come from an independent RV32 calculation, then Sail must observe the same word.
The memory-mapped timer test is handled separately because Sail has no matching
ProcessorCI timer device at 0xfffffffc.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from isa_audit import ROOT, legacy_hex
from validate_legacy_basic_sail import CONFIG, PREFIX, SAIL, address_zero_config, observe

OUTPUT = ROOT / "reports/isa-audit/legacy_advanced_sail.json"
MASK = 0xffffffff
CORRECTED_ZERO_STORES = {"044-div", "045-div", "048-div", "054-divu", "055-divu", "058-divu",
                         "064-rem", "065-rem", "068-rem", "074-remu", "075-remu", "078-remu"}
CONTROL_FLOW_EXPECTED = {"012-jal": 15, "013-jalr": 7}
OPERAND = re.compile(r"^\s*li\s+(a[12]),\s*(-?(?:0x[0-9a-fA-F]+|\d+))", re.M)
OPERATION = re.compile(r"^\s*(mul|mulh|mulhsu|mulhu|div|divu|rem|remu)\s+a3,\s*a1,\s*a2", re.M)


def _signed(value: int) -> int:
    value &= MASK
    return value - (1 << 32) if value & (1 << 31) else value


def arithmetic_expected(source: str) -> tuple[str, int]:
    operands = {register: int(value, 0) for register, value in OPERAND.findall(source)}
    match = OPERATION.search(source)
    if set(operands) != {"a1", "a2"} or not match or source.count("sw a3, 60(zero)") != 1:
        raise ValueError("legacy M case lacks the two operands, target operation, or observable result store")
    op = match[1]
    a, b = operands["a1"] & MASK, operands["a2"] & MASK
    sa, sb = _signed(a), _signed(b)
    if op == "mul":
        result = a * b
    elif op == "mulh":
        result = (sa * sb) >> 32
    elif op == "mulhsu":
        result = (sa * b) >> 32
    elif op == "mulhu":
        result = (a * b) >> 32
    elif op in {"div", "rem"}:
        quotient = -1 if b == 0 else -(1 << 31) if sa == -(1 << 31) and sb == -1 else (
            (abs(sa) // abs(sb)) * (-1 if (sa < 0) != (sb < 0) else 1))
        result = quotient if op == "div" else sa if b == 0 else sa - quotient * sb
    elif op == "divu":
        result = MASK if b == 0 else a // b
    else:
        result = a if b == 0 else a % b
    return op, result & MASK


def _binary_words(binary: bytes) -> list[int]:
    return [int.from_bytes(binary[i:i + 4].ljust(4, b"\0"), "little")
            for i in range(0, len(binary), 4)]


def _cases(root: Path) -> list[tuple[str, Path, str]]:
    cases = [("RV32M", path, "rv32im")
             for path in sorted((root / "tests/RV32M/advanced/src").glob("*.s"))]
    cases += [("RV32I", root / f"tests/RV32I/advanced/src/{stem}.s", "rv32i")
              for stem in CONTROL_FLOW_EXPECTED]
    if len(cases) != 82 or any(not path.is_file() for _, path, _ in cases):
        raise ValueError("expected 80 RV32M and two RV32I control-flow legacy cases")
    return cases


def validate(root: Path = ROOT, output: Path = OUTPUT, *, write_assets: bool = False) -> dict:
    if not SAIL.is_file() or not CONFIG.is_file():
        raise RuntimeError("Sail 0.13.1 and ACT 4.1 rv32-max config are required")
    results = []
    with tempfile.TemporaryDirectory(prefix="processorci-legacy-advanced-") as temporary:
        temp = Path(temporary)
        config = temp / "legacy-rv32.json"
        config.write_text(address_zero_config())
        for group, source, march in _cases(root):
            base = source.parent.parent
            image = base / "memory" / f"{source.stem}.hex"
            reference = base / "reference" / f"{source.stem}.hex"
            text = source.read_text()
            operation, expected = (arithmetic_expected(text) if group == "RV32M"
                                   else (source.stem.split("-", 1)[1], CONTROL_FLOW_EXPECTED[source.stem]))
            obj, elf, binary = (temp / name for name in ("test.o", "test.elf", "test.bin"))
            subprocess.run([PREFIX + "as", f"-march={march}", str(source), "-o", str(obj)],
                           check=True, capture_output=True, text=True)
            subprocess.run([PREFIX + "ld", "-m", "elf32lriscv", "-Ttext=0", str(obj), "-o", str(elf)],
                           check=True, capture_output=True, text=True)
            subprocess.run([PREFIX + "objcopy", "-O", "binary", str(elf), str(binary)],
                           check=True, capture_output=True, text=True)
            compiled_words = _binary_words(binary.read_bytes())
            if len(compiled_words) > 16:
                raise ValueError(f"legacy program exceeds 64-byte loader window: {source}")
            image_status, image_words = legacy_hex(image)
            image_matches = image_status == "words" and image_words == compiled_words
            if not image_matches:
                if not write_assets or source.stem not in CORRECTED_ZERO_STORES:
                    raise ValueError(f"legacy image differs from source: {source}")
                image.write_text("".join(f"{word:08x}\n" for word in compiled_words))
                image_matches = True
            run = subprocess.run([str(SAIL), "--config", str(config), "--inst-limit", "100",
                                  "--trace-mem", str(elf)], capture_output=True, text=True, timeout=10)
            stopped, memory = observe(binary.read_bytes(), run.stdout)
            if not stopped:
                raise RuntimeError(f"no first write to address 60: {source}; {(run.stdout + run.stderr)[-300:]}")
            observed = int.from_bytes(bytes(memory.get(60 + offset, 0) for offset in range(4)), "little")
            if observed != expected:
                raise ValueError(f"independent oracle disagrees with Sail for {source}: {expected:#x} != {observed:#x}")
            ref_status, ref_words = legacy_hex(reference)
            if write_assets and ref_status != "words":
                reference.write_text(f"{expected:08x}\n")
                ref_status, ref_words = legacy_hex(reference)
            if ref_status != "words" or ref_words != [expected]:
                raise ValueError(f"missing or wrong numeric reference for {source}")
            results.append({"group": group, "source": str(source.relative_to(root)),
                            "operation": operation, "expected_word": f"{expected:08x}",
                            "observed_word": f"{observed:08x}",
                            "source_image_matches": image_matches,
                            "fits_64_byte_loader": True,
                            "independent_oracle_matches_sail": True,
                            "reference_matches": True})
    report = {"reference_model": "Sail 0.13.1 rv32-max, 64 KiB address-zero RAM",
              "stop_rule": "first write intersecting byte address 60",
              "independent_oracle": "RV32 integer arithmetic or reviewed control-flow expected value",
              "cases": len(results), "validated": len(results), "results": results,
              "timer_case": {"source": "tests/RV32I/advanced/src/040-timer.s",
                             "status": "hardware_mmio_pending",
                             "reason": "Sail lacks ProcessorCI's 0xfffffffc timer device"}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-assets", action="store_true",
                        help="write numeric references and refresh corrected divide-by-zero images")
    args = parser.parse_args()
    report = validate(write_assets=args.write_assets)
    print(f"Legacy advanced Sail: {report['validated']}/{report['cases']} independently checked")
