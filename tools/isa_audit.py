"""Conservative inventory of the legacy directed corpus.

Usage: python3 tools/isa_audit.py [--output reports/isa-audit]
Presence in a filename is never treated as verified instruction coverage.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from extension_profiles import RATIFIED_Z_INVENTORY, SCOPE, minimum_vector_profile, vector_family, zve32x_applicable

ROOT = Path(__file__).resolve().parents[1]
PREFIX = os.environ.get("RISCV_TOOL_PREFIX", "riscv32-unknown-elf-")
SPEC = "https://docs.riscv.org/reference/isa/v20240411/unpriv/unpriv-index.html"
VECTOR_OPCODE_REVISION = "f24ac23ec9fa947011781a09cd6fd25a7c36dc45"
INVENTORY = {
    "RV32I": "lui auipc jal jalr beq bne blt bge bltu bgeu lb lh lw lbu lhu sb sh sw addi slti sltiu xori ori andi slli srli srai add sub sll slt sltu xor srl sra or and fence ecall ebreak".split(),
    "RV64I": "lwu ld sd addiw slliw srliw sraiw addw subw sllw srlw sraw".split(),
    "RV32M": "mul mulh mulhsu mulhu div divu rem remu".split(),
    "RV64M": "mulw divw divuw remw remuw".split(),
    "RV32A": "lr.w sc.w amoswap.w amoadd.w amoxor.w amoand.w amoor.w amomin.w amomax.w amominu.w amomaxu.w".split(),
    "RV64A": "lr.d sc.d amoswap.d amoadd.d amoxor.d amoand.d amoor.d amomin.d amomax.d amominu.d amomaxu.d".split(),
    "RV32Zicsr": "csrrw csrrs csrrc csrrwi csrrsi csrrci".split(),
    "RV32C": "c.addi4spn c.fld c.lw c.flw c.nop c.addi c.jal c.li c.addi16sp c.lui c.srli c.srai c.andi c.sub c.xor c.or c.and c.j c.beqz c.bnez c.slli c.fldsp c.lwsp c.flwsp c.jr c.mv c.ebreak c.jalr c.add c.fsd c.sw c.fsw c.fsdsp c.swsp c.fswsp".split(),
    "RV32F": "flw fsw fmadd.s fmsub.s fnmsub.s fnmadd.s fadd.s fsub.s fmul.s fdiv.s fsqrt.s fsgnj.s fsgnjn.s fsgnjx.s fmin.s fmax.s fcvt.w.s fcvt.wu.s fmv.x.w feq.s flt.s fle.s fclass.s fcvt.s.w fcvt.s.wu fmv.w.x".split(),
    "RV64F": "fcvt.l.s fcvt.lu.s fcvt.s.l fcvt.s.lu".split(),
    "RV32D": "fld fsd fmadd.d fmsub.d fnmsub.d fnmadd.d fadd.d fsub.d fmul.d fdiv.d fsqrt.d fsgnj.d fsgnjn.d fsgnjx.d fmin.d fmax.d fcvt.s.d fcvt.d.s feq.d flt.d fle.d fclass.d fcvt.w.d fcvt.wu.d fcvt.d.w fcvt.d.wu".split(),
    "RV64D": "fcvt.l.d fcvt.lu.d fmv.x.d fcvt.d.l fcvt.d.lu fmv.d.x".split(),
}
INVENTORY.update(RATIFIED_Z_INVENTORY)


MARCH = {"RV32I": "rv32i", "RV32M": "rv32im", "RV32A": "rv32ia",
         "RV32C": "rv32ic", "RV32Zicsr": "rv32i_zicsr"}


def legacy_hex(path: Path) -> tuple[str, list[int]]:
    """Classify legacy word files without treating comments as test data."""
    if not path.is_file():
        return "missing", []
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if not lines or all(line.startswith(("#", "//", ";")) for line in lines):
        return "placeholder", []
    if any(not re.fullmatch(r"[0-9a-fA-F]{1,8}", line) for line in lines):
        return "malformed", []
    return "words", [int(line, 16) for line in lines]


def legacy_basic_assets(root: Path = ROOT) -> list[dict]:
    """Report every old basic source and its parseable memory and reference data."""
    rows = []
    for source in sorted((root / "tests").glob("RV*/basic/src/*.s")):
        base = source.parent.parent
        memory = base / "memory" / (source.stem + ".hex")
        reference = base / "reference" / (source.stem + ".hex")
        instructions = [line.split("#", 1)[0].strip() for line in source.read_text(errors="replace").splitlines()]
        substantive = any(re.match(r"[A-Za-z][A-Za-z0-9.]*\s", line) for line in instructions)
        memory_status, memory_words = legacy_hex(memory)
        reference_status, reference_words = legacy_hex(reference)
        if not substantive:
            issue = "source has no instruction body"
        elif memory_status != "words":
            issue = f"memory image {memory_status}"
        elif reference_status != "words":
            issue = f"reference {reference_status}"
        else:
            issue = "reference words have no independent execution evidence"
        rows.append({"group": source.parents[2].name,
                     "source": str(source.relative_to(root)),
                     "memory": str(memory.relative_to(root)),
                     "reference": str(reference.relative_to(root)),
                     "source_has_instructions": substantive,
                     "memory_status": memory_status, "memory_words": len(memory_words),
                     "reference_status": reference_status, "reference_words": len(reference_words),
                     "issue": issue})
    return rows


def validate_legacy(source: Path, mnemonic: str, march: str, memory: Path | None) -> tuple[bool, bool, bool, str]:
    with tempfile.TemporaryDirectory() as temp:
        obj, elf, binary = (Path(temp) / name for name in ("test.o", "test.elf", "test.bin"))
        try:
            subprocess.run([PREFIX + "as", f"-march={march}", str(source), "-o", str(obj)],
                           check=True, capture_output=True, text=True)
            subprocess.run([PREFIX + "ld", "-m", "elf32lriscv", "-Ttext=0", str(obj), "-o", str(elf)],
                           check=True, capture_output=True, text=True)
            disasm = subprocess.check_output([PREFIX + "objdump", "-M", "no-aliases", "-d", str(elf)], text=True)
            verified = bool(re.search(r"\s" + re.escape(mnemonic) + r"\s", disasm))
            subprocess.run([PREFIX + "objcopy", "-O", "binary", str(elf), str(binary)],
                           check=True, capture_output=True)
            data = binary.read_bytes()
            words = [f"{int.from_bytes(data[i:i+4].ljust(4, b'\0'), 'little'):08x}" for i in range(0, len(data), 4)]
            listed = memory.read_text().strip().lower().splitlines() if memory and memory.exists() else []
            return True, verified, bool(words and words == listed), ""
        except (subprocess.CalledProcessError, OSError) as exc:
            reason = (exc.stderr if isinstance(exc, subprocess.CalledProcessError) else str(exc))
            return False, False, False, str(reason).strip()[:300]


def scan_categories(root: Path) -> list[dict]:
    result = []
    for group in sorted((root / "tests").glob("RV*")):
        for category in ("basic", "advanced", "invalid"):
            base = group / category
            for source in sorted((base / "src").glob("*.s")):
                instructions = [line.split("#", 1)[0].strip() for line in source.read_text(errors="replace").splitlines()]
                has_instruction = any(re.match(r"[A-Za-z][A-Za-z0-9.]*\s", line) for line in instructions)
                result.append({"group": group.name, "category": category,
                               "source": str(source.relative_to(root)), "has_instruction": has_instruction,
                               "memory_nonempty": bool((base / "memory" / (source.stem + ".hex")).exists() and (base / "memory" / (source.stem + ".hex")).read_text().strip()),
                               "reference_nonempty": bool((base / "reference" / (source.stem + ".hex")).exists() and (base / "reference" / (source.stem + ".hex")).read_text().strip())})
    return result


def scan(root: Path = ROOT, compile_sources: bool = False) -> tuple[list[dict], list[str]]:
    configs = json.loads((root / "config.json").read_text())
    basic_report_path = root / "reports" / "basic-sail-summary.json"
    validated = ({(r["group"], r["instruction"]): r for r in json.loads(basic_report_path.read_text())["results"]}
                 if basic_report_path.exists() else {})
    trap_report_path = root / "reports" / "invalid-sail-summary.json"
    trapped = ({r["instruction"]: r for r in json.loads(trap_report_path.read_text())["results"]}
               if trap_report_path.exists() else {})
    legacy_sail_path = root / "reports" / "isa-audit" / "legacy_basic_sail.json"
    legacy_sail = ({r["source"]: r for r in json.loads(legacy_sail_path.read_text())["results"]}
                   if legacy_sail_path.exists() else {})
    rows, problems = [], []
    configured = configs["test_directories"]
    additional = [{"name": group} for group in RATIFIED_Z_INVENTORY if group not in {c["name"] for c in configured}]
    for conf in configured + additional:
        group = conf["name"]
        base = root / "tests" / group / "basic"
        sources = sorted((base / "src").glob("*.s"))
        by_name = {}
        for source in sources:
            stem = source.stem
            mnemonic = re.sub(r"^\d+-", "", stem).lower()
            mnemonic = re.sub(r"^(c)(?!\.)", r"c.", mnemonic) if group.endswith("C") else mnemonic
            content = source.read_text(errors="replace")
            substantive = [line.strip() for line in content.splitlines() if line.strip() and not line.lstrip().startswith(('#', '//', ';'))]
            target_present = bool(substantive and any(re.search(r"\b" + re.escape(mnemonic) + r"\b", line, re.I) for line in substantive))
            if not target_present:
                problems.append(f"{source.relative_to(root)}: no identifiable target instruction in source")
            by_name.setdefault(mnemonic, []).append((source, target_present))
            for kind in ("memory", "reference"):
                asset = base / kind / (stem + ".hex")
                if not asset.exists() or not asset.read_text().strip():
                    problems.append(f"{asset.relative_to(root)}: missing or empty")
        for mnemonic in INVENTORY.get(group, []):
            matches = by_name.get(mnemonic, [])
            source = matches[0][0] if matches else None
            memory = base / "memory" / (source.stem + ".hex") if source else None
            reference = base / "reference" / (source.stem + ".hex") if source else None
            dependencies = {"I": ["I"], "M": ["I", "M"], "A": ["I", "A"],
                            "C": ["I", "C"], "F": ["I", "F", "Zicsr"],
                            "D": ["I", "F", "D", "Zicsr"], "Zicsr": ["I", "Zicsr"]}
            suffix = group[4:]
            requirements = dependencies.get(suffix, ["I", suffix]).copy()
            if group == "RV32C" and mnemonic in {"c.flw", "c.fsw", "c.flwsp", "c.fswsp"}:
                requirements += ["F", "Zicsr"]
            if group == "RV32C" and mnemonic in {"c.fld", "c.fsd", "c.fldsp", "c.fsdsp"}:
                requirements += ["F", "D", "Zicsr"]
            if group.startswith(("RV32Zve", "RV64Zve")):
                requirements = ["I", "M", "Zicsr", group[4:], "Zvl128b"]
                if group.endswith(("f", "d")):
                    requirements.append("F")
                if group.endswith("d"):
                    requirements.append("D")
            row = {
                "group": group, "instruction": mnemonic,
                "coverage_scope": SCOPE.get(group, "defined core instruction group"),
                "applicable": "conditional" if (group == "RV32C" and len(requirements) > 2) or mnemonic in {"ecall", "ebreak", "c.ebreak"} else "yes",
                "required_isa": ",".join(requirements),
                "source_present": bool(source and matches[0][1]),
                "source": str(source.relative_to(root)) if source else "",
                "reference_source": "",
                "reference_model_profile": "",
                "exception_source": "",
                "exception_validated": False,
                "memory_present": bool(memory and memory.is_file() and memory.read_text().strip()),
                "reference_present": bool(reference and legacy_hex(reference)[0] == "words"),
                "legacy_reference_status": legacy_hex(reference)[0] if reference else "missing",
                "legacy_reference_words": len(legacy_hex(reference)[1]) if reference else 0,
                "legacy_compiled": False, "legacy_disassembly_verified": False,
                "legacy_image_matches_source": False,
                "legacy_reference_validated": bool(source and legacy_sail.get(str(source.relative_to(root)), {}).get("model_status") == "match"),
                "legacy_issue": ("legacy source missing" if source is None else
                                 "legacy source has no identifiable target instruction" if not matches[0][1] else
                                 "legacy source build not audited for this ISA group" if group not in MARCH else
                                 "legacy source build not requested"),
                "compiled": False, "disassembly_verified": False,
                "instruction_bits": 0, "target_opcode_hex": "",
                "reference_validated": False, "package_generated": False,
                "host_mock_validated": False, "hardware_execution": "pending",
                "blocker": "legacy artifact has no reproducible ELF/reference validation" if source else "dedicated source missing",
            }
            if compile_sources and row["source_present"] and group in MARCH:
                compiled, verified, image_matches, reason = validate_legacy(source, mnemonic, MARCH[group], memory)
                row["legacy_compiled"] = compiled
                row["legacy_disassembly_verified"] = verified
                row["legacy_image_matches_source"] = image_matches
                row["compiled"] = compiled
                row["disassembly_verified"] = verified
                row["image_matches_source"] = image_matches
                if reason:
                    row["blocker"] = reason
                    row["legacy_issue"] = f"build failed: {reason}"
                    problems.append(f"{source.relative_to(root)}: build failed: {reason}")
                elif not verified:
                    row["blocker"] = "assembled ELF lacks target instruction"
                    row["legacy_issue"] = row["blocker"]
                    problems.append(f"{source.relative_to(root)}: {row['legacy_issue']}")
                elif not image_matches:
                    row["blocker"] = "checked-in memory image differs from source build"
                    row["legacy_issue"] = row["blocker"]
                    problems.append(f"{memory.relative_to(root)}: {row['legacy_issue']}")
                else:
                    row["blocker"] = "no independent reference execution; hardware pending"
                    row["legacy_issue"] = "no independent reference execution of legacy source"
                    if row["legacy_reference_validated"]:
                        row["legacy_issue"] = "legacy reference matched Sail at first completion write"
            else:
                row["image_matches_source"] = False
            evidence = validated.get((group, mnemonic))
            if evidence:
                row["source_present"] = True
                if not row["source"] or not matches[0][1]:
                    row["source"] = evidence["source"]
                row["reference_source"] = evidence["source"]
                row["compiled"] = evidence["compiled"]
                row["disassembly_verified"] = evidence["disassembly_verified"]
                row["instruction_bits"] = evidence["instruction_bits"]
                row["target_opcode_hex"] = evidence["target_opcode_hex"]
                row["reference_validated"] = evidence["sail_validated"]
                row["package_generated"] = True
                row["host_mock_validated"] = evidence["host_mock_validated"]
                row["blocker"] = "hardware execution pending"
                if group in RATIFIED_Z_INVENTORY:
                    row["reference_model_profile"] = ("sail-rv64-max (V 1.0; vector VLEN=1024)"
                                                       if group.startswith("RV64Zve") else
                                                       "sail-rv32-max (B 1.0, V 1.0; vector VLEN=1024)")
            if mnemonic in trapped and group in ("RV32I", "RV32C"):
                row["exception_validated"] = trapped[mnemonic]["sail_validated"]
                row["exception_source"] = f"tests/RV32I/invalid/package_src/{mnemonic}.S"
                row["blocker"] = "expected M-mode trap validated separately; hardware pending"
            rows.append(row)
        if group not in INVENTORY:
            problems.append(f"{group}: extension definition/configuration unresolved; no completeness claim until a precise subset and VLEN/SEW profile are selected")
    return rows, problems


def write_reports(output: Path, root: Path = ROOT, compile_sources: bool = False) -> None:
    rows, problems = scan(root, compile_sources)
    output.mkdir(parents=True, exist_ok=True)
    (output / "instruction_inventory.json").write_text(json.dumps({"specification": SPEC, "rows": rows}, indent=2) + "\n")
    opcode_file = root / "tools/vector_opcode_candidates.txt"
    opcode_forms = sorted({line.strip() for line in opcode_file.read_text().splitlines()
                           if line.strip() and not line.startswith("#")})
    selected_vector = {r["instruction"] for r in rows if r["group"] == "RV32Zve32x" and r["reference_validated"]}
    selected_higher_vector = {r["instruction"] for r in rows if r["group"] == "RV32Zve64x" and r["reference_validated"]}
    selected_fp32_vector = {r["instruction"] for r in rows if r["group"] == "RV32Zve32f" and r["reference_validated"]}
    selected_fp64wide_vector = {r["instruction"] for r in rows if r["group"] == "RV32Zve64f" and r["reference_validated"]}
    selected_fp64_vector = {r["instruction"] for r in rows if r["group"] == "RV32Zve64d" and r["reference_validated"]}
    selected_rv64_vector = {r["instruction"] for r in rows if r["group"] == "RV64Zve64x" and r["reference_validated"]}
    if not selected_vector <= set(opcode_forms):
        raise ValueError("selected Zve32x instruction absent from pinned V opcode catalog")
    applicable_vector = {m for m in opcode_forms if zve32x_applicable(m)}
    if not selected_vector <= applicable_vector:
        raise ValueError("selected Zve32x instruction is outside the Zve32x profile")
    if not selected_higher_vector <= {m for m in opcode_forms if minimum_vector_profile(m) == ("Zve64x", 32)}:
        raise ValueError("selected Zve64x instruction is outside the RV32 Zve64x profile")
    if not selected_fp32_vector <= {m for m in opcode_forms if minimum_vector_profile(m) == ("Zve32f", 32)}:
        raise ValueError("selected Zve32f instruction is outside the RV32 Zve32f profile")
    if not selected_fp64wide_vector <= {m for m in opcode_forms if minimum_vector_profile(m) == ("Zve64f", 32)}:
        raise ValueError("selected Zve64f instruction is outside the RV32 Zve64f profile")
    if not selected_fp64_vector <= {m for m in opcode_forms if minimum_vector_profile(m) == ("Zve64d", 32)}:
        raise ValueError("selected Zve64d instruction is outside the RV32 Zve64d profile")
    if not selected_rv64_vector <= {m for m in opcode_forms if minimum_vector_profile(m) == ("Zve64x", 64)}:
        raise ValueError("selected RV64 Zve64x instruction is outside the RV64-only profile")
    selected_all_vector = (selected_vector | selected_higher_vector | selected_fp32_vector |
                           selected_fp64wide_vector | selected_fp64_vector | selected_rv64_vector)
    family_counts = {family: {"catalog_forms": sum(vector_family(m) == family for m in opcode_forms),
                              "selected_cases": sum(vector_family(m) == family for m in selected_all_vector)}
                     for family in ("configuration", "memory", "integer_mask_fixed_point_permutation", "floating_point")}
    for counts in family_counts.values():
        counts["unselected_forms"] = counts["catalog_forms"] - counts["selected_cases"]
    profile_counts = {profile: sum(minimum_vector_profile(m)[0] == profile for m in opcode_forms)
                      for profile in ("Zve32x", "Zve32f", "Zve64x", "Zve64f", "Zve64d")}
    vector_catalog = {
        "source": f"https://github.com/riscv/riscv-opcodes/blob/{VECTOR_OPCODE_REVISION}/extensions/rv_v",
        "revision": VECTOR_OPCODE_REVISION,
        "all_v_opcode_forms": len(opcode_forms),
        "selected_zve32x_forms": len(selected_vector),
        "selected_rv32_zve64x_forms": len(selected_higher_vector),
        "rv32_zve64x_applicable_forms": sum(minimum_vector_profile(m) == ("Zve64x", 32) for m in opcode_forms),
        "selected_rv32_zve32f_forms": len(selected_fp32_vector),
        "rv32_zve32f_applicable_forms": sum(minimum_vector_profile(m) == ("Zve32f", 32) for m in opcode_forms),
        "selected_rv32_zve64f_forms": len(selected_fp64wide_vector),
        "rv32_zve64f_applicable_forms": sum(minimum_vector_profile(m) == ("Zve64f", 32) for m in opcode_forms),
        "selected_rv32_zve64d_forms": len(selected_fp64_vector),
        "rv32_zve64d_applicable_forms": sum(minimum_vector_profile(m) == ("Zve64d", 32) for m in opcode_forms),
        "selected_rv64_zve64x_forms": len(selected_rv64_vector),
        "rv64_zve64x_only_forms": sum(minimum_vector_profile(m) == ("Zve64x", 64) for m in opcode_forms),
        "all_catalog_selected_forms": len(selected_all_vector),
        "all_catalog_missing_forms": len(opcode_forms) - len(selected_all_vector),
        "rv32_full_v_applicable_forms": sum(minimum_vector_profile(m)[1] == 32 for m in opcode_forms),
        "rv32_full_v_selected_forms": len(selected_all_vector - selected_rv64_vector),
        "rv32_full_v_missing_forms": sum(minimum_vector_profile(m)[1] == 32 for m in opcode_forms) - len(selected_all_vector - selected_rv64_vector),
        "zve32x_applicable_forms": len(applicable_vector),
        "zve32x_missing_forms": len(applicable_vector - selected_vector),
        "outside_zve32x_forms": len(opcode_forms) - len(applicable_vector),
        "scope": "Full V opcode-form catalog; Zve32x excludes floating-point and EEW64 memory encodings",
        "families": family_counts,
        "minimum_profile_counts": profile_counts,
        "rows": [{"mnemonic": mnemonic, "family": vector_family(mnemonic),
                  "zve32x_applicable": mnemonic in applicable_vector,
                  "minimum_vector_profile": minimum_vector_profile(mnemonic)[0],
                  "minimum_xlen": minimum_vector_profile(mnemonic)[1],
                  "status": "selected_zve32x_case" if mnemonic in selected_vector
                  else "selected_rv32_zve64x_case" if mnemonic in selected_higher_vector
                  else "selected_rv32_zve32f_case" if mnemonic in selected_fp32_vector
                  else "selected_rv32_zve64f_case" if mnemonic in selected_fp64wide_vector
                  else "selected_rv32_zve64d_case" if mnemonic in selected_fp64_vector
                  else "selected_rv64_zve64x_case" if mnemonic in selected_rv64_vector
                  else "missing_zve32x_case" if mnemonic in applicable_vector
                  else "outside_zve32x_profile"} for mnemonic in opcode_forms],
    }
    (output / "vector_opcode_candidates.json").write_text(json.dumps(vector_catalog, indent=2) + "\n")
    categories = scan_categories(root)
    (output / "category_assets.json").write_text(json.dumps(categories, indent=2) + "\n")
    legacy_assets = legacy_basic_assets(root)
    (output / "legacy_basic_assets.json").write_text(json.dumps(legacy_assets, indent=2) + "\n")
    legacy_sail_path = root / "reports" / "isa-audit" / "legacy_basic_sail.json"
    legacy_sail = json.loads(legacy_sail_path.read_text())["results"] if legacy_sail_path.exists() else []
    with (output / "basic_coverage.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    trap_report_path = root / "reports/invalid-sail-summary.json"
    replacements = ([{"legacy_placeholder": row["replaces_legacy_placeholder"],
                      "package": f"build/invalid-sail/{row['instruction']}.json",
                      "expected_mcause": row["mcause"]}
                     for row in json.loads(trap_report_path.read_text())["results"]
                     if row.get("replaces_legacy_placeholder")]
                    if trap_report_path.exists() else [])
    (output / "invalid_replacements.json").write_text(json.dumps(replacements, indent=2) + "\n")
    historical_invalid_groups = ("RV32A", "RV32C", "RV32D", "RV32F", "RV32I",
                                 "RV32M", "RV32Zicsr", "RV64A", "RV64D", "RV64F",
                                 "RV64I", "RV64M")
    replacement_by_source = {row["legacy_placeholder"]: row["package"] for row in replacements}
    retired_invalid = []
    for group in historical_invalid_groups:
        for number in range(1, 6):
            stem = f"{number - 1:03d}-invalid{number}"
            source = f"tests/{group}/invalid/src/{stem}.s"
            if (root / source).exists():
                continue
            if any((root / f"tests/{group}/invalid/{folder}/{stem}.hex").exists()
                   for folder in ("memory", "reference")):
                raise ValueError(f"retired invalid placeholder still has an image or reference: {source}")
            retired_invalid.append({"source": source,
                                    "status": "replaced_by_package" if source in replacement_by_source
                                    else "retired_undefined_placeholder",
                                    "package": replacement_by_source.get(source)})
    (output / "legacy_invalid_retired.json").write_text(json.dumps(retired_invalid, indent=2) + "\n")
    replacement_lines = ["# Invalid or unverified legacy assets", "",
                         f"Retired {len(retired_invalid)} generic invalid source/image/reference triples. "
                         f"{len(replacements)} are linked to individual packages; the others specified no instruction or expected trap.", "",
                         "## Replaced placeholders", "",
                         "These comment-only legacy source/image/reference triples were removed after their executable package cases passed Sail.", "",
                         "| Removed legacy source | Executable package | Expected mcause |",
                         "|---|---|---:|"]
    replacement_lines += [f"| `{row['legacy_placeholder']}` | `{row['package']}` | {row['expected_mcause']} |"
                          for row in replacements]
    replacement_lines += ["", "## Remaining issues", ""] + [f"- {p}" for p in problems]
    (output / "invalid_assets.md").write_text("\n".join(replacement_lines) + "\n")
    missing = [r for r in rows if not r["source_present"]]
    (output / "missing_instructions.md").write_text(
        "# Instructions without ordinary basic sources\n\n"
        "Expected-trap encodings have separate executable sources and reference validation.\n\n" +
        "\n".join(f"- {r['group']}: `{r['instruction']}` — " +
                  ("validated in the expected-trap suite" if r["exception_validated"] else "no validated case")
                  for r in missing) + "\n")
    groups = sorted({r["group"] for r in rows})
    lines = ["# Basic ISA audit", "", "Legacy asset presence is separate from Sail-validated package tests. Expected traps are tracked separately.", "", "| Group | Inventory | Source present | Legacy built | Legacy image matches | Legacy reference matches Sail | Package compiled | Sail validated | Expected trap | Missing basic source |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for group in groups:
        selected = [r for r in rows if r["group"] == group]
        present = sum(r["source_present"] for r in selected)
        lines.append(f"| {group} | {len(selected)} | {present} | {sum(r['legacy_compiled'] for r in selected)} | {sum(r['legacy_image_matches_source'] for r in selected)} | {sum(r['legacy_reference_validated'] for r in selected)} | {sum(r['compiled'] for r in selected)} | {sum(r['reference_validated'] for r in selected)} | {sum(r['exception_validated'] for r in selected)} | {len(selected)-present} |")
    lines += ["", "## Legacy basic reference audit", "",
              "Nonempty comment-only hex files are placeholders. Per-source details and Sail replay results are in `legacy_basic_assets.json` and `legacy_basic_sail.json`.", "",
              "| Sources | With instructions | Numeric memory images | Numeric references | Reference placeholders | Sail reference matches |",
              "|---:|---:|---:|---:|---:|---:|",
              f"| {len(legacy_assets)} | {sum(r['source_has_instructions'] for r in legacy_assets)} | "
              f"{sum(r['memory_status'] == 'words' for r in legacy_assets)} | "
              f"{sum(r['reference_status'] == 'words' for r in legacy_assets)} | "
              f"{sum(r['reference_status'] == 'placeholder' for r in legacy_assets)} | "
              f"{sum(r['model_status'] == 'match' for r in legacy_sail)} |",
              "", "| Legacy group | Sources | Instruction bodies | Numeric memory images | Numeric references | Reference placeholders |",
              "|---|---:|---:|---:|---:|---:|"]
    for group in sorted({r["group"] for r in legacy_assets}):
        selected = [r for r in legacy_assets if r["group"] == group]
        lines.append(f"| {group} | {len(selected)} | {sum(r['source_has_instructions'] for r in selected)} | "
                     f"{sum(r['memory_status'] == 'words' for r in selected)} | "
                     f"{sum(r['reference_status'] == 'words' for r in selected)} | "
                     f"{sum(r['reference_status'] == 'placeholder' for r in selected)} |")
    lines += ["", "## All legacy category assets", "", "| Category | Sources | With instructions | Memory files | Reference files |", "|---|---:|---:|---:|---:|"]
    for category in ("basic", "advanced", "invalid"):
        selected = [r for r in categories if r["category"] == category]
        lines.append(f"| {category} | {len(selected)} | {sum(r['has_instruction'] for r in selected)} | {sum(r['memory_nonempty'] for r in selected)} | {sum(r['reference_nonempty'] for r in selected)} |")
    act_report = root / "reports" / "act4-summary.json"
    act_status = (f"ACT 4.1.0: {json.loads(act_report.read_text())['host_mock_validated']} software-target packages host-mock validated."
                  if act_report.exists() else "ACT 4.1.0: no package validation report yet.")
    rv64_act_report = root / "reports" / "act4-rv64-summary.json"
    if rv64_act_report.exists():
        act_status += f" RV64 I sample: {json.loads(rv64_act_report.read_text())['host_mock_validated']} packages host-mock validated."
    imc_act_report = root / "reports" / "act4-rv32imc-summary.json"
    if imc_act_report.exists():
        imc_summary = json.loads(imc_act_report.read_text())
        act_status += f" RV32 I/M/C request: {imc_summary['host_mock_validated']} packages host-mock validated; extension counts {imc_summary['extension_counts']}."
    vector_forms = len(INVENTORY["RV32Zve32x"])
    rv32_untested = sum(r["minimum_xlen"] == 32 and r["status"] == "outside_zve32x_profile"
                        for r in vector_catalog["rows"])
    rv64_only = sum(r["minimum_xlen"] == 64 for r in vector_catalog["rows"])
    lines += ["",
              "The legacy B, P and V profiles were removed. B coverage uses ratified Zba/Zbb/Zbs (B 1.0), optional Zbc and selected unique Zbkb forms.",
              f"RV32Zve32x has {vector_catalog['selected_zve32x_forms']}/{vector_forms} applicable V 1.0 opcode forms Sail-validated at selected legal SEW/VL settings; this does not represent exhaustive vector parameter coverage.",
              f"The pinned V opcode catalog has {len(opcode_forms)} forms; {vector_catalog['rv32_full_v_selected_forms']}/{vector_catalog['rv32_full_v_applicable_forms']} RV32 full-V opcode forms have dedicated Sail-validated cases across five named Zve groups. {rv32_untested} RV32 forms remain untested; {vector_catalog['selected_rv64_zve64x_forms']}/{rv64_only} indexed EEW64 forms were validated under RV64.",
              "P remains outside the configured suite while its specification is a developing draft.",
              "F/D instructions require FP state initialization; C floating instructions depend on F/D.",
              "ECALL, EBREAK and C.EBREAK are validated as expected M-mode traps in the separate invalid suite.",
              "ACT submodule migrated from RISCOF 241b1fe294567751bd3ae6f338b1dbfc40c41a20 to ACT 4.1.0 6e8a45123f14cebfb3df151a0e7b849b4389b33b.",
              act_status, "Hardware validation: pending."]
    (output / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "isa-audit")
    parser.add_argument("--compile", action="store_true", help="Assemble supported RV32 legacy sources and compare images")
    args = parser.parse_args()
    write_reports(args.output, compile_sources=args.compile)
