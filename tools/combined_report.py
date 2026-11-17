"""Combine executed software reports without merging their coverage metrics."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"required verification report missing: {path}")
    return json.loads(path.read_text())


def generate(root: Path = ROOT) -> dict:
    reports = root / "reports"
    inventory = _read(reports / "isa-audit/instruction_inventory.json")["rows"]
    vector_catalog = _read(reports / "isa-audit/vector_opcode_candidates.json")
    basic = _read(reports / "basic-sail-summary.json")
    traps = _read(reports / "invalid-sail-summary.json")
    advanced_qemu = _read(root / "build/advanced/summary.json")
    advanced_sail = _read(reports / "advanced-sail-summary.json")
    act = _read(reports / "act4-summary.json")
    rv64_act_path = reports / "act4-rv64-summary.json"
    rv64_act = _read(rv64_act_path) if rv64_act_path.is_file() else None
    imc_act_path = reports / "act4-rv32imc-summary.json"
    imc_act = _read(imc_act_path) if imc_act_path.is_file() else None
    dut_path = reports / "act4-cv32e40s-software.json"
    dut = _read(dut_path) if dut_path.is_file() else None
    profile_path = reports / "act4-cv32e40s-profile-audit.json"
    profile_audit = _read(profile_path) if profile_path.is_file() else None
    dut_fit_path = reports / "act4-cv32e40s-fit.json"
    dut_fit = _read(dut_fit_path) if dut_fit_path.is_file() else None
    dut_rtl_paths = [reports / f"act4-cv32e40s-rtl-{name}.json"
                     for name in ("addi", "addi-induced-fail", "mul")]
    dut_rtl = [_read(path) for path in dut_rtl_paths] if all(path.is_file() for path in dut_rtl_paths) else []
    shared_fit_path = reports / "act4-cv32e40s-fit-512k.json"
    shared_fit = _read(shared_fit_path) if shared_fit_path.is_file() else None
    controller_path = reports / "act4-cv32e40s-controller-rtl.json"
    controller_run = _read(controller_path) if controller_path.is_file() else None
    serial_path = reports / "act4-cv32e40s-controller-serial-all.json"
    serial_run = _read(serial_path) if serial_path.is_file() else None
    negative_paths = {
        "self_check_failure": reports / "act4-cv32e40s-controller-serial-full-load-induced-fail.json",
        "unexpected_trap": reports / "act4-cv32e40s-controller-serial-full-load-illegal.json",
        "timeout": reports / "act4-cv32e40s-controller-serial-timeout.json",
    }
    negative_runs = {name: _read(path) for name, path in negative_paths.items() if path.is_file()}

    ordinary = {(r["group"], r["instruction"]) for r in inventory if r["reference_validated"]}
    if any(r["instruction_bits"] != (16 if r["instruction"].startswith("c.") else 32) or
           len(r["target_opcode_hex"]) != r["instruction_bits"] // 4
           for r in inventory if r["reference_validated"]):
        raise ValueError("basic inventory has missing or incorrect target opcode width proof")
    basic_ids = {(r["group"], r["instruction"]) for r in basic["results"] if r["sail_validated"]}
    if ordinary != basic_ids or basic["sail_validated"] != len(basic_ids):
        raise ValueError("basic inventory and Sail report disagree")
    trap_ids = {r["instruction"] for r in traps["results"] if r["sail_validated"]}
    inventory_traps = {r["instruction"] for r in inventory if r["exception_validated"]}
    if not inventory_traps <= trap_ids or traps["sail_validated"] != len(trap_ids):
        raise ValueError("exception inventory and Sail report disagree")
    qemu_ids = {r["id"] for r in advanced_qemu["results"] if r["reference_validated"]}
    sail_ids = {r["id"] for r in advanced_sail["results"] if r["sail_validated"]}
    if (qemu_ids != sail_ids or advanced_qemu["qemu_validated"] != len(qemu_ids) or
            advanced_sail["sail_validated"] != len(sail_ids) or advanced_sail["host_mock_validated"] != len(sail_ids)):
        raise ValueError("advanced QEMU and Sail reports disagree")
    vector_vlen_path = reports / "vector-vlen128-summary.json"
    vector_vlen = _read(vector_vlen_path) if vector_vlen_path.is_file() else None
    vstart_path = reports / "vector-vstart-summary.json"
    vstart_probe = _read(vstart_path) if vstart_path.is_file() else None
    if vector_vlen:
        expected_vector_basic = {f"{g}-{i}" for g, i in basic_ids if g.startswith(("RV32Zve", "RV64Zve"))}
        expected_vector_advanced = {r["id"] for r in advanced_sail["results"] if r["category"] == "vector"}
        observed_vector_basic = {r["id"] for r in vector_vlen["results"] if r["source"] == "basic"}
        observed_vector_advanced = {r["id"] for r in vector_vlen["results"] if r["source"] == "advanced"}
        if (vector_vlen["vlen_bits"] != 128 or
                observed_vector_basic != expected_vector_basic or
                observed_vector_advanced != expected_vector_advanced or
                vector_vlen["basic_cases"] != len(expected_vector_basic) or
                vector_vlen["advanced_scenarios"] != len(expected_vector_advanced) or
                vector_vlen["full_v_validated"] != len(vector_vlen["results"]) or
                vector_vlen["named_zve_validated"] != len(vector_vlen["results"]) or
                len(vector_vlen["results"]) != len(expected_vector_basic) + len(expected_vector_advanced) or
                any(not (r["full_v_validated"] and r["named_zve_validated"])
                    for r in vector_vlen["results"])):
            raise ValueError("VLEN128 vector report disagrees with basic or advanced Sail reports")
    if vstart_probe and (vstart_probe.get("scenario") != "vector_vstart_arith_resume_probe" or
                         vstart_probe.get("hardware_validated") != 0 or
                         not all(vstart_probe.get(key) for key in
                                 ("disassembly_verified", "qemu_resumed", "sail_default_trap_observed",
                                  "sail_arithmetic_resume_override_validated",
                                  "sail_zve32x_vlen128_resume_validated"))):
        raise ValueError("nonzero-vstart arithmetic probe has incomplete software evidence")
    if (act["generated_elfs"] != act["converted_packages"] or
            act["converted_packages"] != act["host_mock_validated"] or
            act["host_mock_validated"] != act["sail_validated"] or
            act["host_mock_validated"] != len(set(act["test_ids"]))):
        raise ValueError("ACT package and host mock counts disagree")
    act_packages_present = len(list((root / "build/act4/packages").glob("*.json"))) == act["converted_packages"]
    if rv64_act:
        if (rv64_act.get("isa") != "rv64i" or
                len(set(rv64_act["test_ids"])) != rv64_act["generated_elfs"] or
                any(rv64_act[key] != rv64_act["generated_elfs"] for key in
                    ("converted_packages", "sail_validated", "host_mock_validated"))):
            raise ValueError("RV64 ACT package and execution counts disagree")
        rv64_act_packages_present = len(list((root / "build/act4-rv64/packages").glob("*.json"))) == rv64_act["converted_packages"]
    if imc_act:
        if (imc_act.get("isa") != "rv32imc" or
                len(set(imc_act["test_ids"])) != imc_act["generated_elfs"] or
                any(imc_act[key] != imc_act["generated_elfs"] for key in
                    ("converted_packages", "sail_validated", "host_mock_validated")) or
                sum(imc_act["extension_counts"].values()) != imc_act["generated_elfs"]):
            raise ValueError("RV32IMC ACT package and execution counts disagree")
        imc_act_packages_present = len(list((root / "build/act4-rv32imc/packages").glob("*.json"))) == imc_act["converted_packages"]
    if dut:
        dut_ids = set(dut["test_ids"])
        dut_packages_present = len(list((root / "build/act4-cv32e40s/packages").glob("*.json"))) == len(dut_ids)
        wrapper = root.parent / "RV-Bench/overlay/cv32e40s/wrappers/cv32e40s.sv"
        controller_source = root.parent / "RV-Bench/tools/controller/rtl/controller.sv"
        source_hashes = ((hashlib.sha256(wrapper.read_bytes()).hexdigest(),
                          hashlib.sha256(controller_source.read_bytes()).hexdigest())
                         if wrapper.is_file() and controller_source.is_file() else None)
        if profile_audit:
            sail_source = root / "build/act4-cv32e40s/dut_config/sail.json"
            udb_source = root / "build/act4-cv32e40s/dut_config/cv32e40s-rv32imc.yaml"
            memory_source = root.parent / "RV-Bench/tools/controller/rtl/memory.sv"
            profile_current = bool(source_hashes and sail_source.is_file() and
                                   udb_source.is_file() and memory_source.is_file() and
                                   profile_audit.get("source_sha256", {}).get("wrapper") == source_hashes[0] and
                                   profile_audit["source_sha256"].get("controller") == source_hashes[1] and
                                   profile_audit["source_sha256"].get("sail") ==
                                   hashlib.sha256(sail_source.read_bytes()).hexdigest() and
                                   profile_audit["source_sha256"].get("udb") ==
                                   hashlib.sha256(udb_source.read_bytes()).hexdigest() and
                                   profile_audit["source_sha256"].get("memory") ==
                                   hashlib.sha256(memory_source.read_bytes()).hexdigest())
            rtl_dir = root.parent / "RV-Bench/cores/cv32e40s/rtl"
            capability_sources = {
                "core": rtl_dir / "cv32e40s_core.sv",
                "package": rtl_dir / "include/cv32e40s_pkg.sv",
                "csr": rtl_dir / "cv32e40s_cs_registers.sv",
                "pmp": rtl_dir / "cv32e40s_pmp.sv",
                "pma": rtl_dir / "cv32e40s_pma.sv",
                "lsu": rtl_dir / "cv32e40s_load_store_unit.sv",
                "decoder": rtl_dir / "cv32e40s_compressed_decoder.sv",
                "sequencer": rtl_dir / "cv32e40s_sequencer.sv",
                "fsm": rtl_dir / "cv32e40s_controller_fsm.sv",
                "serial_runner": root / "tools/run_act4_cv32e40s_serial.py",
                "probe": root / "tools/probe_rvbench_cv32e40s.py",
            }
            profile_current = profile_current and all(
                path.is_file() and profile_audit["source_sha256"].get(name) ==
                hashlib.sha256(path.read_bytes()).hexdigest()
                for name, path in capability_sources.items())
        else:
            profile_current = False
        if profile_current and (profile_audit.get("act_coverage", {}).get("generated_by_extension") !=
                                {"I": 39, "M": 8, "C": 0} or
                                profile_audit["act_coverage"].get("dut_validated_extensions") != ["I", "M"] or
                                profile_audit["act_coverage"].get("c_upstream_sources") != 0):
            raise ValueError("CV32E40S ACT profile coverage is inconsistent")
        if (dut.get("core") != "RV-Bench CV32E40S" or dut.get("act_release") != "4.1.0" or
                len(dut_ids) != dut["generated_elfs"] or
                dut["direct_sail_passes"] != len(dut_ids) or
                dut["host_oracle_checks"] != len(dut_ids)):
            raise ValueError("CV32E40S ACT software report has inconsistent counts")
        if dut_fit and (dut_fit["checked"] != len(dut_ids) or
                        {row["test_id"] for row in dut_fit["tests"]} != dut_ids or
                        dut_fit["fit"] != sum(row["fits"] for row in dut_fit["tests"])):
            raise ValueError("CV32E40S ACT package-fit report disagrees with software report")
        if shared_fit and (shared_fit["checked"] != len(dut_ids) or
                           {row["test_id"] for row in shared_fit["tests"]} != dut_ids or
                           shared_fit["fit"] != len(dut_ids) or
                           shared_fit["physical_memory_bytes"] != 524288 or
                           shared_fit["reserved_diagnostic_bytes"] != 4096):
            raise ValueError("CV32E40S shared-memory fit report is inconsistent")
        if dut_rtl:
            if not source_hashes or any(row.get("wrapper_sha256") != source_hashes[0] for row in dut_rtl):
                dut_rtl = []  # superseded wrapper evidence is not counted
        if dut_rtl:
            expected = [("I-addi-00", False, 1, "PASS"),
                        ("I-addi-00", True, 3, "SELF_CHECK_FAILURE"),
                        ("M-mul-00", False, 1, "PASS")]
            for row, (test_id, fault, status, classified) in zip(dut_rtl, expected, strict=True):
                if (row["test_id"] != test_id or row["injected_addi_fault"] != fault or
                        row["tohost_observed"] != status or row["classified_outcome"] != classified or
                        row["rtl_result"] != "pass" or
                        row["controller_execution"] or row["fpga_execution"]):
                    raise ValueError(f"CV32E40S ACT RTL evidence is stale or inconsistent: {test_id}")
        for evidence in (controller_run, serial_run):
            if evidence and (not source_hashes or not dut_packages_present or
                             evidence.get("wrapper_sha256") != source_hashes[0] or
                             evidence.get("controller_sha256") != source_hashes[1]):
                if evidence is controller_run:
                    controller_run = None
                else:
                    serial_run = None
                continue
            if evidence:
                rows = evidence["tests"]
                if (evidence["memory_bytes"] != 524288 or
                        {row["test_id"] for row in rows} != dut_ids or
                        len(rows) != len(dut_ids) or
                        any(row["outcome"] != "PASS" or row["status"] != 1 or
                            row["package_sha256"] != hashlib.sha256(
                                (root / "build/act4-cv32e40s/packages" / f"{row['test_id']}.json").read_bytes()
                            ).hexdigest() for row in rows) or
                        evidence["serial_execution"] != (evidence is serial_run) or
                        evidence["serial_load_verified"] != (evidence is serial_run)):
                    raise ValueError("CV32E40S controller execution report is inconsistent")
        expected_negative = {"self_check_failure": (3, "SELF_CHECK_FAILURE"),
                             "unexpected_trap": (3, "UNEXPECTED_TRAP"),
                             "timeout": (1, "TIMEOUT")}
        for name, evidence in list(negative_runs.items()):
            if (not source_hashes or not dut_packages_present or
                    evidence.get("wrapper_sha256") != source_hashes[0] or
                    evidence.get("controller_sha256") != source_hashes[1]):
                del negative_runs[name]
                continue
            rows = evidence["tests"]
            status, classified = expected_negative[name]
            if (len(rows) != 1 or rows[0]["test_id"] != "I-addi-00" or
                    rows[0]["status"] != status or rows[0]["outcome"] != classified or
                    not evidence["serial_execution"] or
                    evidence["serial_load_verified"] != (name != "timeout") or
                    rows[0]["package_sha256"] != hashlib.sha256(
                        (root / "build/act4-cv32e40s/packages/I-addi-00.json").read_bytes()
                    ).hexdigest()):
                raise ValueError(f"CV32E40S {name} serial evidence is inconsistent")
            if name == "unexpected_trap" and rows[0]["trap_diagnostics"] != {"cause": 2, "epc": 0x88}:
                raise ValueError("CV32E40S unexpected-trap cause/EPC evidence is inconsistent")

    groups = {}
    for group in sorted({r["group"] for r in inventory}):
        rows = [r for r in inventory if r["group"] == group]
        groups[group] = {"inventoried": len(rows), "ordinary_sail_validated": sum(r["reference_validated"] for r in rows),
                         "expected_trap_sail_validated": sum(r["exception_validated"] for r in rows),
                         "package_generated": sum(r["package_generated"] for r in rows)}
    categories = Counter(r["category"] for r in advanced_sail["results"])
    vector_forms = groups.get("RV32Zve32x", {}).get("ordinary_sail_validated", 0)
    vector_applicable = groups.get("RV32Zve32x", {}).get("inventoried", 0)
    zve64x_forms = groups.get("RV32Zve64x", {}).get("ordinary_sail_validated", 0)
    zve64x_applicable = groups.get("RV32Zve64x", {}).get("inventoried", 0)
    zve32f_forms = groups.get("RV32Zve32f", {}).get("ordinary_sail_validated", 0)
    zve32f_applicable = groups.get("RV32Zve32f", {}).get("inventoried", 0)
    zve64f_forms = groups.get("RV32Zve64f", {}).get("ordinary_sail_validated", 0)
    zve64f_applicable = groups.get("RV32Zve64f", {}).get("inventoried", 0)
    zve64d_forms = groups.get("RV32Zve64d", {}).get("ordinary_sail_validated", 0)
    zve64d_applicable = groups.get("RV32Zve64d", {}).get("inventoried", 0)
    rv64_zve64x_forms = groups.get("RV64Zve64x", {}).get("ordinary_sail_validated", 0)
    rv64_zve64x_applicable = groups.get("RV64Zve64x", {}).get("inventoried", 0)
    if vector_catalog["selected_zve32x_forms"] != vector_forms:
        raise ValueError("Zve32x inventory and opcode catalog disagree")
    if vector_catalog["zve32x_applicable_forms"] != vector_applicable:
        raise ValueError("Zve32x applicable inventory and opcode catalog disagree")
    if (vector_catalog["selected_rv32_zve64x_forms"] != zve64x_forms or
            vector_catalog["rv32_zve64x_applicable_forms"] != zve64x_applicable):
        raise ValueError("RV32Zve64x inventory and opcode catalog disagree")
    if (vector_catalog["selected_rv32_zve32f_forms"] != zve32f_forms or
            vector_catalog["rv32_zve32f_applicable_forms"] != zve32f_applicable):
        raise ValueError("RV32Zve32f inventory and opcode catalog disagree")
    if (vector_catalog["selected_rv32_zve64f_forms"] != zve64f_forms or
            vector_catalog["rv32_zve64f_applicable_forms"] != zve64f_applicable):
        raise ValueError("RV32Zve64f inventory and opcode catalog disagree")
    if (vector_catalog["selected_rv32_zve64d_forms"] != zve64d_forms or
            vector_catalog["rv32_zve64d_applicable_forms"] != zve64d_applicable):
        raise ValueError("RV32Zve64d inventory and opcode catalog disagree")
    if (vector_catalog["selected_rv64_zve64x_forms"] != rv64_zve64x_forms or
            vector_catalog["rv64_zve64x_only_forms"] != rv64_zve64x_applicable):
        raise ValueError("RV64Zve64x inventory and opcode catalog disagree")
    if vector_catalog["rv32_full_v_selected_forms"] != vector_forms + zve64x_forms + zve32f_forms + zve64f_forms + zve64d_forms:
        raise ValueError("RV32 V selected-form count disagrees with validated groups")
    if vector_catalog["all_catalog_selected_forms"] != vector_catalog["rv32_full_v_selected_forms"] + rv64_zve64x_forms:
        raise ValueError("full-V catalog selected-form count disagrees with validated groups")
    result = {
        "basic_isa": {"inventoried": len(inventory), "ordinary_sail_validated": len(ordinary),
                      "expected_trap_sail_validated": len(inventory_traps), "groups": groups,
                      "vector_opcode_catalog": {key: vector_catalog[key] for key in
                                                ("revision", "all_v_opcode_forms", "selected_zve32x_forms",
                                                 "zve32x_applicable_forms", "zve32x_missing_forms",
                                                 "selected_rv32_zve64x_forms", "rv32_zve64x_applicable_forms",
                                                 "selected_rv32_zve32f_forms", "rv32_zve32f_applicable_forms",
                                                 "selected_rv32_zve64f_forms", "rv32_zve64f_applicable_forms",
                                                 "selected_rv32_zve64d_forms", "rv32_zve64d_applicable_forms",
                                                 "selected_rv64_zve64x_forms", "rv64_zve64x_only_forms",
                                                 "all_catalog_selected_forms", "all_catalog_missing_forms",
                                                 "rv32_full_v_applicable_forms", "rv32_full_v_selected_forms",
                                                 "rv32_full_v_missing_forms",
                                                 "outside_zve32x_forms", "families",
                                                 "minimum_profile_counts")},
                      "coverage_qualifications": ["P profile excluded because its specification is a developing draft",
                                                  f"Zve32x has {vector_forms}/{vector_applicable} applicable opcode forms validated",
                                                  f"RV32Zve64x has {zve64x_forms}/{zve64x_applicable} newly applicable opcode forms validated",
                                                  f"RV32Zve32f has {zve32f_forms}/{zve32f_applicable} FP32 opcode forms validated",
                                                  f"RV32Zve64f has {zve64f_forms}/{zve64f_applicable} FP32/EEW64 opcode forms validated",
                                                  f"RV32Zve64d has {zve64d_forms}/{zve64d_applicable} FP64 opcode forms validated",
                                                  f"{vector_catalog['rv32_full_v_missing_forms']} RV32 full-V opcode forms lack tests; {rv64_zve64x_forms}/{rv64_zve64x_applicable} RV64-only forms validated separately",
                                                  "Zbkb counts unique forms apart from overlapping Zbb forms"]},
        "invalid": {"sail_validated": len(trap_ids), "additional_operations": sorted(trap_ids - inventory_traps),
                    "trap_failure_codes": traps.get("trap_failure_codes")},
        "advanced": {"scenarios": len(advanced_sail["results"]), "qemu_validated": len(qemu_ids),
                     "sail_validated": len(sail_ids), "host_mock_validated": advanced_sail["host_mock_validated"],
                     "categories": dict(sorted(categories.items()))},
        "vector_vlen128": ({"basic_cases": vector_vlen["basic_cases"],
                            "advanced_scenarios": vector_vlen["advanced_scenarios"],
                            "full_v_validated": vector_vlen["full_v_validated"],
                            "named_zve_validated": vector_vlen["named_zve_validated"]}
                           if vector_vlen else None),
        "vector_vstart_probe": vstart_probe,
        "act4": {"release": act["act_release"], "generated_elfs": act["generated_elfs"],
                 "converted_packages": act["converted_packages"], "sail_validated": act["sail_validated"],
                 "host_mock_validated": act["host_mock_validated"],
                 "package_artifacts_present": act_packages_present,
                 "dut_reference_validated": 0},
        "act4_rv64": ({"release": rv64_act["act_release"], "isa": "rv64i",
                       "generated_elfs": rv64_act["generated_elfs"],
                       "converted_packages": rv64_act["converted_packages"],
                       "sail_validated": rv64_act["sail_validated"],
                       "host_mock_validated": rv64_act["host_mock_validated"],
                       "package_artifacts_present": rv64_act_packages_present,
                       "dut_reference_validated": 0} if rv64_act else None),
        "act4_rv32imc": ({"release": imc_act["act_release"], "isa": "rv32imc",
                          "extension_counts": imc_act["extension_counts"],
                          "generated_elfs": imc_act["generated_elfs"],
                          "converted_packages": imc_act["converted_packages"],
                          "sail_validated": imc_act["sail_validated"],
                          "host_mock_validated": imc_act["host_mock_validated"],
                          "package_artifacts_present": imc_act_packages_present,
                          "dut_reference_validated": 0} if imc_act else None),
        "act4_cv32e40s_candidate": ({"release": dut["act_release"], "core": dut["core"],
                                     "generated_elfs": dut["generated_elfs"],
                                     "sail_validated": dut["direct_sail_passes"],
                                     "host_oracle_validated": dut["host_oracle_checks"],
                                     "package_artifacts_present": dut_packages_present,
                                     "rtl_pass_cases": ([row["test_id"] for row in controller_run["tests"]]
                                                        if controller_run else
                                                        [row["test_id"] for row in dut_rtl
                                                         if row["classified_outcome"] == "PASS"]),
                                     "rtl_induced_self_check_failures": (1 if "self_check_failure" in negative_runs else
                                         sum(row["classified_outcome"] == "SELF_CHECK_FAILURE" for row in dut_rtl)),
                                     "controller_rtl_passes": len(controller_run["tests"]) if controller_run else 0,
                                     "uart_full_load_passes": len(serial_run["tests"]) if serial_run else 0,
                                     "shared_512k_fit": (shared_fit["fit"] if shared_fit else None),
                                     "profile_static_audit_current": profile_current,
                                     "act_coverage": (profile_audit["act_coverage"] if profile_current else None),
                                     "profile_findings": (profile_audit["profile_findings"] if profile_current else None),
                                     "known_profile_limitations": (profile_audit["known_profile_limitations"]
                                                                   if profile_current else []),
                                     "remaining_profile_review": (profile_audit["remaining_profile_review"]
                                                                  if profile_current else []),
                                     "serial_negative_cases": sorted(negative_runs),
                                     "board_fit": ({"board": dut_fit["board"], "fit": dut_fit["fit"],
                                                    "checked": dut_fit["checked"]} if dut_fit else None),
                                     "controller_executed": len(controller_run["tests"]) if controller_run else 0,
                                     "fpga_executed": 0} if dut else None),
        "random_riscv_dv": {"integration": "absent from this checkout"},
        "fpga": {"validation": "pending", "executed": 0},
    }
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "combined-summary.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# ProcessorCI software verification summary", "",
             "Counts come from the basic inventory and execution reports. ACT host checks are separate from ISA coverage.", "",
             f"- Basic ISA: {len(inventory)} inventoried; {len(ordinary)} ordinary Sail validated; {len(inventory_traps)} exceptional encodings Sail validated.",
             f"- Vector inventory scope: {vector_catalog['rv32_full_v_selected_forms']}/{vector_catalog['rv32_full_v_applicable_forms']} applicable RV32 full-V opcode forms and {rv64_zve64x_forms}/{rv64_zve64x_applicable} RV64-only forms validated across named Zve groups; parameter combinations are sampled.",
             *([f"- Vector VLEN128 replay: {vector_vlen['basic_cases']} basic and {vector_vlen['advanced_scenarios']} advanced cases passed full-V and matching named-Zve Sail configurations; DUT validation pending."] if vector_vlen else []),
             *(["- Nonzero-vstart arithmetic: QEMU and a permissive Sail profile resumed successfully; the pinned strict Sail profile traps by configuration. This is a conditional probe, outside the advanced PASS count."] if vstart_probe else []),
             f"- Invalid suite: {len(trap_ids)} Sail validated, including {len(trap_ids - inventory_traps)} operations outside the basic inventory.",
             *(["- Trap self-check status: " + ", ".join(f"{code}={meaning}" for code, meaning in traps["trap_failure_codes"].items()) + "."] if traps.get("trap_failure_codes") else []),
             f"- Advanced: {len(sail_ids)} scenarios passed QEMU and Sail.",
             f"- ACT {act['act_release']}: {act['generated_elfs']} ELFs, {act['converted_packages']} packages, {act['sail_validated']} Sail executions, {act['host_mock_validated']} host checks in the recorded build; DUT runs pending.",
             *( [f"- ACT {rv64_act['act_release']} RV64 I: {rv64_act['generated_elfs']} ELFs, {rv64_act['converted_packages']} packages, {rv64_act['sail_validated']} Sail executions, {rv64_act['host_mock_validated']} host checks; DUT runs pending."] if rv64_act else []),
             *([f"- ACT {imc_act['act_release']} RV32 I/M/C software request: {imc_act['generated_elfs']} ELFs, {imc_act['sail_validated']} Sail executions, {imc_act['host_mock_validated']} host checks; I={imc_act['extension_counts'].get('I', 0)}, M={imc_act['extension_counts'].get('M', 0)}, C={imc_act['extension_counts'].get('C', 0)}. This is a software sample, not the selected DUT run."] if imc_act else []),
             *([f"- RV-Bench CV32E40S ACT candidate: {dut['generated_elfs']} I/M ELFs passed Sail and host checks; "
                f"{result['act4_cv32e40s_candidate']['controller_rtl_passes']} passed core/controller RTL, "
                f"{result['act4_cv32e40s_candidate']['uart_full_load_passes']} passed full UART segment loading and execution; "
                f"serial negatives {', '.join(sorted(negative_runs)) if negative_runs else 'pending'}; "
                f"shared 512 KiB fit {shared_fit['fit'] if shared_fit else 0}/{len(dut['test_ids'])}; "
                f"source/profile audit {'current' if profile_current else 'pending'}; ACT DUT scope I/M only, C=0 upstream test sources; "
                f"legacy board profile fit {dut_fit['fit']}/{dut_fit['checked']}; FPGA synthesis and execution pending."]
               if dut and dut_fit else []),
             f"- ACT package artifacts available in this checkout: {'yes' if act_packages_present else 'no; counts are from the archived local report'}.",
             "- riscv-dv: integration absent from this checkout.",
             "- FPGA: execution pending.", "", "## Basic ISA by group", "",
             "| Group | Inventoried | Ordinary Sail | Expected trap | Packages |",
             "|---|---:|---:|---:|---:|"]
    for group, row in groups.items():
        lines.append(f"| {group} | {row['inventoried']} | {row['ordinary_sail_validated']} | {row['expected_trap_sail_validated']} | {row['package_generated']} |")
    lines += ["", "B 1.0 is split into Zba/Zbb/Zbs; Zbc and selected unique Zbkb forms are tracked separately.",
              f"Zve32x has {vector_forms}/{vector_applicable} applicable RV32 opcode forms validated; parameter combinations are sampled.",
              f"Zve64x has {zve64x_forms}/{zve64x_applicable} additional RV32 opcode forms validated; four indexed EEW64 forms were validated separately under RV64.",
              f"Zve32f has {zve32f_forms}/{zve32f_applicable} additional FP32 opcode forms validated.",
              f"Zve64f has {zve64f_forms}/{zve64f_applicable} additional FP32/EEW64 opcode forms validated.",
              f"Zve64d has {zve64d_forms}/{zve64d_applicable} additional FP64 opcode forms validated.",
              f"RV64Zve64x has {rv64_zve64x_forms}/{rv64_zve64x_applicable} indexed EEW64 forms validated separately.",
              "P is excluded from the configured suite while its specification is a developing draft."]
    catalog_note = ("All pinned forms have dedicated Sail-validated cases across RV32 and RV64 software profiles; core-specific hardware coverage remains pending."
                    if vector_catalog["all_catalog_missing_forms"] == 0 else
                    "Unselected forms have a minimum Zve subset and XLEN classification and await dedicated tests.")
    lines += ["", "## Pinned V opcode-form catalog", "",
              catalog_note, "",
              "| Family | Catalog | Selected | Unselected |", "|---|---:|---:|---:|"]
    for family, counts in vector_catalog["families"].items():
        lines.append(f"| {family.replace('_', ' ')} | {counts['catalog_forms']} | {counts['selected_cases']} | {counts['unselected_forms']} |")
    lines += ["", "Minimum Zve profile for an applicable opcode form: " +
              ", ".join(f"{profile} {count}" for profile, count in vector_catalog["minimum_profile_counts"].items()) +
              ". The four EEW64 indexed memory forms were validated under RV64."]
    (reports / "combined-summary.md").write_text("\n".join(lines) + "\n")

    suites = ET.Element("testsuites")
    suite_ids = [("basic.sail", sorted(f"{g}-{i}" for g, i in ordinary)),
                 ("invalid.sail", sorted(trap_ids)),
                 ("advanced.qemu_and_sail", sorted(sail_ids)),
                 ("act4.sail_and_host_mock", sorted(act["test_ids"]))]
    if rv64_act:
        suite_ids.append(("act4.rv64_sail_and_host_mock", sorted(rv64_act["test_ids"])))
    if imc_act:
        suite_ids.append(("act4.rv32imc_sail_and_host_mock", sorted(imc_act["test_ids"])))
    if dut:
        suite_ids.append(("act4.cv32e40s_sail_and_host", sorted(dut["test_ids"])))
    if controller_run:
        suite_ids.append(("act4.cv32e40s_controller_rtl", sorted(dut_ids)))
    if serial_run:
        suite_ids.append(("act4.cv32e40s_uart_full_load", sorted(dut_ids)))
    for name, ids in suite_ids:
        archived = (name == "act4.sail_and_host_mock" and not act_packages_present or
                    name == "act4.rv64_sail_and_host_mock" and not rv64_act_packages_present or
                    name == "act4.rv32imc_sail_and_host_mock" and not imc_act_packages_present or
                    name == "act4.cv32e40s_sail_and_host" and not dut_packages_present)
        suite = ET.SubElement(suites, "testsuite", name=name, tests=str(len(ids)), failures="0", errors="0",
                              skipped=str(len(ids) if archived else 0))
        for test_id in ids:
            case = ET.SubElement(suite, "testcase", name=test_id, classname=name)
            if archived:
                ET.SubElement(case, "skipped", message="ACT package artifacts absent; archived local report only")
    ET.indent(suites)
    ET.ElementTree(suites).write(reports / "combined-software.junit.xml", encoding="utf-8", xml_declaration=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = generate(args.root)
    print(f"Combined report: {report['basic_isa']['ordinary_sail_validated']} basic, "
          f"{report['invalid']['sail_validated']} trap cases, "
          f"{report['advanced']['sail_validated']} advanced, "
          f"{report['act4']['host_mock_validated']} RV32 ACT host checks, "
          f"{report['act4_rv64']['host_mock_validated'] if report['act4_rv64'] else 0} RV64 ACT host checks, "
          f"{report['act4_rv32imc']['host_mock_validated'] if report['act4_rv32imc'] else 0} RV32 I/M/C ACT host checks, "
          f"{report['act4_cv32e40s_candidate']['controller_rtl_passes'] if report['act4_cv32e40s_candidate'] else 0} CV32E40S controller RTL PASS cases, "
          f"{report['act4_cv32e40s_candidate']['uart_full_load_passes'] if report['act4_cv32e40s_candidate'] else 0} UART full-load PASS cases")
