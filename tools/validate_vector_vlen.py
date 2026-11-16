"""Replay every built vector package at the minimum declared VLEN of 128 bits."""
from __future__ import annotations

import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from build_basic_sail import CONFIG_Z, CONFIG_Z64, ROOT, SAIL
from extension_profiles import VECTOR_OPCODE_FORMS

OVERRIDE = ROOT / "tools/config/vector-vlen128.json"
OUTPUT = ROOT / "reports/vector-vlen128-summary.json"
PROFILE_LEVELS = {"Zve32x": ("Integer", 5), "Zve32f": ("Float_single", 5),
                  "Zve64x": ("Integer", 6), "Zve64f": ("Float_single", 6),
                  "Zve64d": ("Float_double", 6)}
OPTIONAL_VECTOR_EXTENSIONS = ("Zvabd", "Zvfbfmin", "Zvfbfwma", "Zvfh", "Zvfhmin",
                              "Zvbb", "Zvbc", "Zvkb", "Zvkg", "Zvkned", "Zvknha",
                              "Zvknhb", "Zvksed", "Zvksh", "Zvkt")


def profile_override(extension: str) -> dict:
    level, elen_exp = PROFILE_LEVELS[extension]
    return {"extensions": {"V": {"support_level": level, "vlen_exp": 7,
                                  "elen_exp": elen_exp, "max_index_eew_exp": elen_exp},
                           **{name: {"supported": False} for name in OPTIONAL_VECTOR_EXTENSIONS}}}


def selected_cases(root: Path = ROOT) -> tuple[list[dict], list[dict]]:
    basic_report = json.loads((root / "reports/basic-sail-summary.json").read_text())
    advanced_report = json.loads((root / "reports/advanced-sail-summary.json").read_text())
    basic = [row for row in basic_report["results"]
             if row["group"].startswith(("RV32Zve", "RV64Zve"))]
    advanced = [row for row in advanced_report["results"] if row["category"] == "vector"]
    basic_ids = [(row["group"], row["instruction"]) for row in basic]
    advanced_ids = [row["id"] for row in advanced]
    if len(basic_ids) != len(set(basic_ids)) or len(basic_ids) != len(VECTOR_OPCODE_FORMS):
        raise ValueError("basic vector report does not cover the pinned opcode catalog exactly once")
    if len(advanced_ids) != len(set(advanced_ids)) or not advanced_ids:
        raise ValueError("advanced vector report contains duplicate or no scenarios")
    for row in basic:
        if not row.get("sail_validated"):
            raise ValueError(f"basic vector case lacks original Sail validation: {row['group']}/{row['instruction']}")
    for row in advanced:
        if not row.get("sail_validated"):
            raise ValueError(f"advanced vector case lacks original Sail validation: {row['id']}")
    return basic, advanced


def validate(root: Path = ROOT, output: Path = OUTPUT) -> dict:
    if not SAIL.is_file() or not CONFIG_Z.is_file() or not CONFIG_Z64.is_file():
        raise RuntimeError("Sail 0.13.1 and the ACT 4.1 RV32/RV64 max configurations are required")
    override = json.loads((root / "tools/config/vector-vlen128.json").read_text())
    if override != {"extensions": {"V": {"vlen_exp": 7}}}:
        raise ValueError("vector override must set only VLEN to 128 bits")
    basic, advanced = selected_cases(root)
    results = []
    with tempfile.TemporaryDirectory(prefix="processorci-zve-") as temp:
        overrides = {}
        for extension in PROFILE_LEVELS:
            path = Path(temp) / f"{extension}.json"
            path.write_text(json.dumps(profile_override(extension)))
            overrides[extension] = path
        for kind, rows in (("basic", basic), ("advanced", advanced)):
            for row in rows:
                ident = f"{row['group']}-{row['instruction']}" if kind == "basic" else row["id"]
                elf = root / (row["elf"] if kind == "basic" else f"build/advanced-sail/{ident}.elf")
                package_path = root / (row["package"] if kind == "basic" else f"build/advanced-sail/{ident}.json")
                package = json.loads(package_path.read_text())
                extension = package["vector_profile"]["extension"]
                if package["vector_profile"]["minimum_vlen_bits"] != 128 or extension not in overrides:
                    raise ValueError(f"case has an unsupported vector profile or VLEN: {ident}")
                config = CONFIG_Z64 if package["isa"].startswith("rv64") else CONFIG_Z
                for mode, override_path in (("full_v", root / "tools/config/vector-vlen128.json"),
                                            ("named_zve", overrides[extension])):
                    run = subprocess.run([str(SAIL), "--config", str(config),
                                          "--config-override", str(override_path), str(elf)],
                                         capture_output=True, text=True, timeout=30)
                    if run.returncode != 0 or "SUCCESS" not in run.stdout:
                        raise RuntimeError(f"Sail {mode} VLEN128 rejected {ident}: "
                                           f"{(run.stdout + run.stderr)[-1500:]}")
                results.append({"source": kind, "id": ident, "group": row.get("group"),
                                "extension": extension, "elf": str(elf.relative_to(root)),
                                "full_v_validated": True, "named_zve_validated": True})
    groups = Counter(row["group"] for row in results if row["source"] == "basic")
    report = {"reference_model": "Sail 0.13.1", "vlen_bits": 128,
              "named_zve_levels": {name: {"support_level": level, "elen_bits": 2 ** elen_exp}
                                   for name, (level, elen_exp) in PROFILE_LEVELS.items()},
              "optional_vector_extensions_disabled": list(OPTIONAL_VECTOR_EXTENSIONS),
              "base_configs": [str(CONFIG_Z.relative_to(root)), str(CONFIG_Z64.relative_to(root))],
              "override": str(OVERRIDE.relative_to(root)),
              "basic_cases": len(basic), "advanced_scenarios": len(advanced),
              "full_v_validated": len(results), "named_zve_validated": len(results),
              "basic_groups": dict(sorted(groups.items())),
              "hardware_validated": 0, "results": results}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    result = validate()
    print(f"Vector VLEN128: {result['named_zve_validated']}/{result['basic_cases'] + result['advanced_scenarios']} passed full V and named Zve Sail profiles")
