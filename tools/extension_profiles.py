"""Pinned Z-extension instruction-form inventory.

Zve32x includes every RV32 form in the pinned V 1.0 opcode catalog that is
legal with EEW/SEW no greater than 32 and without vector floating point.
"""
from __future__ import annotations

import re
from pathlib import Path


VECTOR_OPCODE_FORMS = tuple(line.strip() for line in
                            Path(__file__).with_name("vector_opcode_candidates.txt").read_text().splitlines()
                            if line.strip() and not line.startswith("#"))


def vector_family(mnemonic: str) -> str:
    """Group V opcode forms for reporting; these are not Zve subset labels."""
    if mnemonic != "vfirst.m" and mnemonic.startswith(("vf", "vmf")):
        return "floating_point"
    if mnemonic.startswith("vset"):
        return "configuration"
    if re.match(r"^(vl[1248]re|vle|vlm\.|vloxei|vlse|vluxei|vs[1248]r\.|vse[0-9]|vsm\.|vsoxei|vsse|vsuxei)", mnemonic):
        return "memory"
    return "integer_mask_fixed_point_permutation"


def zve32x_applicable(mnemonic: str) -> bool:
    """V 1.0 Zve32x supports integer forms and memory EEW 8/16/32."""
    if vector_family(mnemonic) == "floating_point":
        return False
    if vector_family(mnemonic) == "memory" and "64" in mnemonic:
        return False
    if mnemonic in {"vsext.vf8", "vzext.vf8"}:
        return False  # Source EEW would be below 8 unless SEW is at least 64.
    return True


_ZVE64F_ONLY = {
    "vfncvt.f.x.w", "vfncvt.f.xu.w",
    "vfwcvt.x.f.v", "vfwcvt.xu.f.v",
    "vfwcvt.rtz.x.f.v", "vfwcvt.rtz.xu.f.v",
}


def minimum_vector_profile(mnemonic: str) -> tuple[str, int]:
    """Return the minimum Zve subset and XLEN for a legal form of this opcode."""
    if zve32x_applicable(mnemonic):
        return "Zve32x", 32
    if mnemonic in _ZVE64F_ONLY:
        return "Zve64f", 32
    if vector_family(mnemonic) == "floating_point":
        if mnemonic.startswith(("vfw", "vfncvt")):
            return "Zve64d", 32
        return "Zve32f", 32
    if mnemonic in {"vloxei64.v", "vluxei64.v", "vsoxei64.v", "vsuxei64.v"}:
        return "Zve64x", 64
    return "Zve64x", 32

RATIFIED_Z_INVENTORY = {
    "RV32Zba": "sh1add sh2add sh3add".split(),
    "RV32Zbb": "andn orn xnor clz ctz cpop min minu max maxu sext.b sext.h zext.h rol ror rori orc.b rev8".split(),
    "RV32Zbc": "clmul clmulh clmulr".split(),
    "RV32Zbs": "bclr bclri bext bexti binv binvi bset bseti".split(),
    "RV32Zbkb": "pack packh brev8 zip unzip".split(),
    "RV32Zve32x": [m for m in VECTOR_OPCODE_FORMS if zve32x_applicable(m)],
    "RV32Zve32f": [m for m in VECTOR_OPCODE_FORMS if minimum_vector_profile(m) == ("Zve32f", 32)],
    "RV32Zve64x": [m for m in VECTOR_OPCODE_FORMS if minimum_vector_profile(m) == ("Zve64x", 32)],
    "RV32Zve64f": [m for m in VECTOR_OPCODE_FORMS if minimum_vector_profile(m) == ("Zve64f", 32)],
    "RV32Zve64d": [m for m in VECTOR_OPCODE_FORMS if minimum_vector_profile(m) == ("Zve64d", 32)],
    "RV64Zve64x": [m for m in VECTOR_OPCODE_FORMS if minimum_vector_profile(m) == ("Zve64x", 64)],
}

SCOPE = {group: ("full RV32 Zve32x opcode forms; parameter combinations sampled by individual cases"
                  if group == "RV32Zve32x" else
                  "RV32 opcode forms first enabled by Zve64x; four RV64-only indexed-memory forms excluded"
                  if group == "RV32Zve64x" else
                  "RV32 FP32 opcode forms first enabled by Zve32f; parameter combinations sampled"
                  if group == "RV32Zve32f" else
                  "RV32 FP32-to-EEW64 forms first enabled by Zve64f; parameter combinations sampled"
                  if group == "RV32Zve64f" else
                  "RV32 FP64 forms first enabled by Zve64d; parameter combinations sampled"
                  if group == "RV32Zve64d" else
                  "four RV64-only indexed EEW64 memory forms; parameter combinations sampled"
                  if group == "RV64Zve64x" else
                  "unique RV32 Zbkb forms; overlapping Zbb forms counted under Zbb"
                  if group == "RV32Zbkb" else "full RV32 mnemonic set for this extension")
         for group in RATIFIED_Z_INVENTORY}

