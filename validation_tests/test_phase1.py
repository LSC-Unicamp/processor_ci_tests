import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from advanced_cases import CASES, source
from audit_test_directories import generate as audit_test_directories
from basic_cases import CASES as BASIC_CASES, source as basic_source
from build_basic_sail import CONFIG as SAIL_CONFIG, CONFIG64, CONFIG_Z, GCC as BASIC_GCC, OBJDUMP as BASIC_OBJDUMP, SAIL as SAIL_EXE, build as build_basic, target_encoding
from build_invalid_sail import CASES as TRAP_CASES, source as trap_source
from validate_advanced_sail import sail_source
from build_advanced import PREFIX, build, elf_segments
from combined_report import generate as generate_combined
from act4_package import classify_tohost, convert
from check_dut_package_fit import board_memory_bytes, check as check_dut_fit
from probe_controller_rtl import CONTROLLER as CONTROLLER_RTL, probe as probe_controller_rtl
from probe_vector_vstart import probe as probe_vector_vstart
from validate_legacy_basic_sail import observe as observe_legacy
from validate_legacy_advanced_sail import arithmetic_expected, validate as validate_legacy_advanced
from validate_legacy_advanced_timer import validate as validate_legacy_timer
from isa_audit import legacy_basic_assets, legacy_hex, scan, scan_categories
from extension_profiles import RATIFIED_Z_INVENTORY
from riscv_test_runner.core.selection import isa_compatible, select_directories
from riscv_test_runner.cli import main as cli_main
from riscv_test_runner.core.package import InvalidPackage, flat_memory_fit, initial_memory, outcome
from riscv_test_runner.core.package import TRAP_FAILURE_CODES
from riscv_test_runner.core.serial_package import run_package


def test_inventory_reports_missing_and_placeholders():
    rows, problems = scan()
    assert sum(not r["source_present"] for r in rows) == 3
    assert sum(r["exception_validated"] for r in rows) == 3
    assert any("RV32F" in item for item in problems)
    assert sum(r["reference_validated"] for r in rows) == len(BASIC_CASES)
    assert all(r["instruction_bits"] == (16 if r["instruction"].startswith("c.") else 32)
               and len(r["target_opcode_hex"]) == r["instruction_bits"] // 4
               for r in rows if r["reference_validated"])
    assert all(r["has_instruction"] for r in scan_categories(ROOT) if r["category"] == "advanced")
    with (ROOT / "reports/isa-audit/basic_coverage.csv").open() as handle:
        audited = {(r["group"], r["instruction"]): r for r in csv.DictReader(handle)}
    old = audited["RV32A", "lr.w"]
    assert old["legacy_compiled"] == "True" and old["legacy_image_matches_source"] == "True"
    assert old["legacy_issue"] == "no independent reference execution of legacy source"
    placeholder = audited["RV32F", "flw"]
    assert placeholder["legacy_issue"] == "legacy source has no identifiable target instruction"
    assert placeholder["reference_validated"] == "True"


def test_test_directory_audit_distinguishes_packages_from_legacy_gaps(tmp_path):
    report = audit_test_directories(output=tmp_path / "test_directories.json")
    assert report["configured_legacy_groups"] == 12
    assert report["package_only_groups"] == 11
    assert report["retired_legacy_advanced_placeholders"] == 147
    assert report["package_totals"] == {"basic": len(BASIC_CASES),
                                        "advanced": len(CASES), "invalid": len(TRAP_CASES)}
    assert not any(issue["severity"] == "error" for issue in report["issues"])
    by_group = {row["group"]: row for row in report["groups"]}
    assert all(row["packages"]["advanced"]["validated_packages"] > 0
               for row in report["groups"] if row["configured_legacy"])
    assert by_group["RV32Zve32x"]["packages"]["basic"]["validated_packages"] == 259
    assert by_group["RV32Zve32x"]["legacy"]["basic"]["sources"] == 0
    assert by_group["RV32M"]["legacy"]["advanced"]["missing_reference"] == []
    assert by_group["RV32M"]["legacy"]["advanced"]["orphan_reference"] == []
    assert by_group["RV32M"]["legacy"]["advanced"]["substantive_without_numeric_reference"] == []
    assert by_group["RV32I"]["legacy"]["advanced"]["missing_reference"] == []
    assert report["extra_tests"] == [] and not report["extra_tests_included"]
    assert report["issues"] == []


def test_legacy_advanced_oracles_and_timer_image(tmp_path):
    report = validate_legacy_advanced(output=tmp_path / "legacy_advanced.json")
    assert report["cases"] == report["validated"] == 82
    assert all(row["source_image_matches"] and row["fits_64_byte_loader"]
               and row["independent_oracle_matches_sail"]
               and row["reference_matches"] for row in report["results"])
    div_zero = next(row for row in report["results"] if row["source"].endswith("044-div.s"))
    rem_zero = next(row for row in report["results"] if row["source"].endswith("064-rem.s"))
    assert div_zero["expected_word"] == "ffffffff"
    assert rem_zero["expected_word"] == "000004d2"
    with pytest.raises(ValueError, match="observable result store"):
        arithmetic_expected("li a1, 1\nli a2, 0\ndiv a3, a1, a2\nsw zero, 60(zero)\n")
    timer = validate_legacy_timer(output=tmp_path / "timer.json")
    assert timer["source_image_matches"] and timer["reference_word"] == "00000001"
    assert timer["core_execution"] == "pending"


def test_legacy_basic_reference_classification(tmp_path):
    rows = legacy_basic_assets(ROOT)
    assert len(rows) == 166
    assert sum(row["reference_status"] == "words" for row in rows) == 71
    assert sum(row["reference_status"] == "placeholder" for row in rows) == 95
    model = json.loads((ROOT / "reports/isa-audit/legacy_basic_sail.json").read_text())
    assert model["counts"]["match"] == 67
    assert model["counts"].get("mismatch", 0) == 0
    assert model["counts"]["reference_placeholder"] == 11
    assert model["counts"]["no_completion_write"] == 1
    atomic = next(row for row in rows if row["source"].endswith("RV32A/basic/src/000-lr.w.s"))
    assert atomic["source_has_instructions"] and atomic["memory_status"] == "words"
    assert atomic["reference_status"] == "placeholder"
    malformed = tmp_path / "bad.hex"
    malformed.write_text("00000001\n# comment mixed with words\n")
    assert legacy_hex(malformed)[0] == "malformed"


def test_legacy_replay_stops_on_first_completion_write():
    trace = ("mem[W,0x000000038] <- 0x00000002\n"
             "mem[W,0x00000003C] <- 0x00000005\n"
             "mem[W,0x00000003C] <- 0x00000009\n")
    stopped, memory = observe_legacy(b"\0" * 64, trace)
    assert stopped and memory[56] == 2 and memory[60] == 5
    assert observe_legacy(b"\0" * 64, "mem[W,0x000000038] <- 0x00000002\n")[0] is False


def test_split_extension_inventory_and_retired_umbrella_groups():
    assert all(not (ROOT / "tests" / group).exists() for group in ("RV32B", "RV32P", "RV32V"))
    assert {d["name"] for d in json.loads((ROOT / "config.json").read_text())["test_directories"]}.isdisjoint({"RV32B", "RV32P", "RV32V"})
    assert len(RATIFIED_Z_INVENTORY["RV32Zve32x"]) == 259
    assert len(RATIFIED_Z_INVENTORY["RV32Zve64x"]) == 11
    assert len(RATIFIED_Z_INVENTORY["RV32Zve32f"]) == 66
    assert len(RATIFIED_Z_INVENTORY["RV32Zve64f"]) == 6
    assert len(RATIFIED_Z_INVENTORY["RV32Zve64d"]) == 29
    assert len(RATIFIED_Z_INVENTORY["RV64Zve64x"]) == 4
    for group, inventory in RATIFIED_Z_INVENTORY.items():
        assert {mnemonic for case_group, mnemonic, *_ in BASIC_CASES if case_group == group} == set(inventory)
    opcode_catalog = json.loads((ROOT / "reports/isa-audit/vector_opcode_candidates.json").read_text())
    assert opcode_catalog["all_v_opcode_forms"] == 375
    assert opcode_catalog["selected_zve32x_forms"] == 259
    assert opcode_catalog["selected_rv32_zve64x_forms"] == 11
    assert opcode_catalog["rv32_zve64x_applicable_forms"] == 11
    assert opcode_catalog["selected_rv32_zve32f_forms"] == 66
    assert opcode_catalog["rv32_zve32f_applicable_forms"] == 66
    assert opcode_catalog["selected_rv32_zve64f_forms"] == opcode_catalog["rv32_zve64f_applicable_forms"] == 6
    assert opcode_catalog["selected_rv32_zve64d_forms"] == opcode_catalog["rv32_zve64d_applicable_forms"] == 29
    assert opcode_catalog["selected_rv64_zve64x_forms"] == opcode_catalog["rv64_zve64x_only_forms"] == 4
    assert (opcode_catalog["all_catalog_selected_forms"], opcode_catalog["all_catalog_missing_forms"]) == (375, 0)
    assert (opcode_catalog["rv32_full_v_selected_forms"],
            opcode_catalog["rv32_full_v_applicable_forms"],
            opcode_catalog["rv32_full_v_missing_forms"]) == (371, 371, 0)
    assert opcode_catalog["zve32x_applicable_forms"] == 259
    assert opcode_catalog["zve32x_missing_forms"] == 0
    assert opcode_catalog["outside_zve32x_forms"] == 116
    assert opcode_catalog["minimum_profile_counts"] == {
        "Zve32x": 259, "Zve32f": 66, "Zve64x": 15,
        "Zve64f": 6, "Zve64d": 29}
    assert sum(row["minimum_xlen"] == 64 for row in opcode_catalog["rows"]) == 4
    assert {family: counts["unselected_forms"] for family, counts in opcode_catalog["families"].items()} == {
        "configuration": 0, "memory": 0, "integer_mask_fixed_point_permutation": 0,
        "floating_point": 0}


def test_combined_report_reconciles_sources_and_rejects_stale_counts(tmp_path):
    shutil.copytree(ROOT / "reports", tmp_path / "reports")
    summary = tmp_path / "build/advanced/summary.json"
    summary.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "build/advanced/summary.json", summary)
    result = generate_combined(tmp_path)
    assert result["basic_isa"]["ordinary_sail_validated"] == len(BASIC_CASES)
    assert result["basic_isa"]["vector_opcode_catalog"]["zve32x_missing_forms"] == 0
    assert result["basic_isa"]["groups"]["RV32Zve64x"]["ordinary_sail_validated"] == 11
    assert result["basic_isa"]["groups"]["RV32Zve32f"]["ordinary_sail_validated"] == 66
    assert result["basic_isa"]["groups"]["RV32Zve64f"]["ordinary_sail_validated"] == 6
    assert result["basic_isa"]["groups"]["RV32Zve64d"]["ordinary_sail_validated"] == 29
    assert result["basic_isa"]["groups"]["RV64Zve64x"]["ordinary_sail_validated"] == 4
    assert result["basic_isa"]["expected_trap_sail_validated"] == 3
    assert result["invalid"]["sail_validated"] == len(TRAP_CASES)
    assert result["invalid"]["additional_operations"] == sorted(
        target for target, _, _ in TRAP_CASES if target not in ("ecall", "ebreak", "c.ebreak"))
    assert result["advanced"]["sail_validated"] == len(CASES)
    assert result["vector_vlen128"] == {"basic_cases": 375, "advanced_scenarios": 14,
                                         "full_v_validated": 389, "named_zve_validated": 389}
    assert result["vector_vstart_probe"]["sail_zve32x_vlen128_resume_validated"]
    assert result["act4"]["host_mock_validated"] == 39
    rv64_act = result["act4_rv64"]
    if rv64_act:
        assert rv64_act["isa"] == "rv64i"
        assert rv64_act["sail_validated"] == rv64_act["host_mock_validated"] == 51
    imc_act = result["act4_rv32imc"]
    if imc_act:
        assert imc_act["isa"] == "rv32imc"
        assert imc_act["extension_counts"] == {"I": 39, "M": 8, "C": 0}
        assert imc_act["sail_validated"] == imc_act["host_mock_validated"] == 47
    dut_act = result["act4_cv32e40s_candidate"]
    if dut_act:
        assert dut_act["sail_validated"] == dut_act["host_oracle_validated"] == 47
        assert dut_act["shared_512k_fit"] == 47
    root = ET.parse(tmp_path / "reports/combined-software.junit.xml").getroot()
    assert sum(int(s.get("tests")) for s in root) == len(BASIC_CASES) + len(TRAP_CASES) + len(CASES) + 39 + (51 if rv64_act else 0) + (47 if imc_act else 0) + (47 if dut_act else 0)
    assert sum(int(s.get("skipped")) for s in root) == 39 + (51 if rv64_act else 0) + (47 if imc_act else 0) + (47 if dut_act else 0)
    inventory_path = tmp_path / "reports/isa-audit/instruction_inventory.json"
    inventory = json.loads(inventory_path.read_text())
    c_row = next(row for row in inventory["rows"] if row["instruction"] == "c.addi")
    c_row["instruction_bits"] = 32
    inventory_path.write_text(json.dumps(inventory))
    with pytest.raises(ValueError, match="target opcode width"):
        generate_combined(tmp_path)
    shutil.copyfile(ROOT / "reports/isa-audit/instruction_inventory.json", inventory_path)
    vector_path = tmp_path / "reports/vector-vlen128-summary.json"
    vector = json.loads(vector_path.read_text())
    vector["results"][0]["named_zve_validated"] = False
    vector_path.write_text(json.dumps(vector))
    with pytest.raises(ValueError, match="VLEN128 vector report"):
        generate_combined(tmp_path)
    shutil.copyfile(ROOT / "reports/vector-vlen128-summary.json", vector_path)
    act_path = tmp_path / "reports/act4-summary.json"
    act = json.loads(act_path.read_text())
    act["host_mock_validated"] -= 1
    act_path.write_text(json.dumps(act))
    with pytest.raises(ValueError, match="ACT package"):
        generate_combined(tmp_path)


def test_selection_keeps_xlen_and_extensions_exact():
    config = json.loads((ROOT / "config.json").read_text())
    assert {d["name"] for d in select_directories(config, "rv64im")} == {"RV64I", "RV64M"}
    assert {d["name"] for d in select_directories(config, "rv32imc")} == {"RV32I", "RV32M", "RV32C"}
    assert {d["name"] for d in select_directories(config, "rv32id")} == {"RV32I", "RV32F", "RV32D", "RV32Zicsr"}
    assert {d["name"] for d in select_directories(config, "rv32ib")} == {"RV32I"}
    with pytest.raises(ValueError, match="developing draft"):
        select_directories(config, "rv32ip")
    assert isa_compatible("rv32im", "rv32imc")
    assert isa_compatible("rv32ifd_zicsr", "rv32g")
    assert isa_compatible("rv32if_zicsr", "rv32if")
    assert not isa_compatible("rv64i", "rv32imc")
    assert not isa_compatible("rv32ifd_zicsr", "rv32imc")
    assert isa_compatible("rv32i_zbb", "rv32ib")
    assert isa_compatible("rv32im_zicsr_zve32x_zvl128b", "rv32imv")
    assert isa_compatible("rv32i_zicsr_zve32x_zvl32b", "rv32i_zve64x")
    assert isa_compatible("rv32i_zicsr_zve32x_zvl32b", "rv32i_zve32f")
    assert not isa_compatible("rv32if_zicsr_zve32f", "rv32i_zve64x")
    assert isa_compatible("rv32ifd_zicsr_zve64d_zvl64b", "rv32iv")
    assert isa_compatible("rv32im_zicsr_zve32x_zvl128b", "rv32im_zicsr_zve32x_zvl256b")
    assert not isa_compatible("rv32im_zicsr_zve32x_zvl128b", "rv32im_zicsr_zve32x_zvl64b")


def test_cli_package_listing_filters_isa(capsys):
    cli_main(["--list", "--suite", "basic,advanced,arch", "--march", "rv32imc"])
    output = capsys.readouterr().out
    assert "package basic RV32M-mul" in output
    assert "package advanced mul_consumer" in output
    assert "ACT4 arch I-addi-00" in output
    assert "RV64I-addiw" not in output
    assert "RV32F-fadd.s" not in output
    assert "rv64_store_load_dependency" not in output
    cli_main(["--list", "--suite", "advanced", "--march", "rv64i"])
    assert "package advanced rv64_store_load_dependency" in capsys.readouterr().out
    cli_main(["--list", "--suite", "basic", "--march", "rv32ib"])
    bit_output = capsys.readouterr().out
    assert "package basic RV32Zbb-andn" in bit_output
    assert "package basic RV32Zbc-clmul" not in bit_output
    cli_main(["--list", "--suite", "basic,advanced", "--march", "rv32im_zicsr_zve32x_zvl128b"])
    vector_output = capsys.readouterr().out
    assert "package basic RV32Zve32x-vadd.vv" in vector_output
    assert "package advanced vector_load_add_store" in vector_output
    cli_main(["--list", "--suite", "basic", "--march", "rv32im_zicsr_zve64x_zvl128b"])
    integer64_output = capsys.readouterr().out
    assert "package basic RV32Zve64x-vle64.v" in integer64_output
    assert "RV32Zve32f-vfadd.vv" not in integer64_output
    cli_main(["--list", "--suite", "basic", "--march", "rv32imfdv"])
    full_rv32_output = capsys.readouterr().out
    assert "package basic RV32Zve64d-vfwadd.vv" in full_rv32_output
    assert "RV64Zve64x-vluxei64.v" not in full_rv32_output
    cli_main(["--list", "--suite", "basic", "--march", "rv64imfdv"])
    assert "package basic RV64Zve64x-vluxei64.v" in capsys.readouterr().out
    cli_main(["--list", "--suite", "invalid", "--march", "rv32i"])
    assert "package invalid" not in capsys.readouterr().out
    cli_main(["--list", "--suite", "invalid", "--march", "rv32i_zicsr"])
    invalid_output = capsys.readouterr().out
    assert "package invalid trap-ecall" in invalid_output
    assert "trap-c.ebreak" not in invalid_output
    cli_main(["--list", "--suite", "invalid", "--march", "rv32ic_zicsr"])
    assert "package invalid trap-c.ebreak" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="stop-cause handling"):
        cli_main(["--suite", "invalid", "--march", "rv32ic_zicsr", "--port", "mock"])


def test_cli_offline_filters_instruction_scenario_category_and_id(capsys):
    cli_main(["--list", "--suite", "basic,advanced,arch", "--march", "rv32imc",
              "--instruction", "addi"])
    lines = capsys.readouterr().out.splitlines()
    assert "package basic RV32I-addi" in lines
    assert "RV32I basic 000-addi" in lines
    assert all("advanced" not in line and "arch" not in line for line in lines)

    cli_main(["--list", "--suite", "basic", "--march", "rv32ic", "--instruction", "c.addi"])
    assert set(capsys.readouterr().out.splitlines()) == {
        "package basic RV32C-c.addi", "RV32C basic 000-caddi"}

    cli_main(["--list", "--suite", "advanced,basic", "--march", "rv32if_zicsr",
              "--scenario", "fp_dynamic_rounding_flags"])
    assert capsys.readouterr().out.splitlines() == ["package advanced fp_dynamic_rounding_flags"]
    cli_main(["--list", "--suite", "advanced,arch,basic", "--march", "rv32ifd_zicsr",
              "--category", "floating"])
    category_lines = capsys.readouterr().out.splitlines()
    assert "package advanced fp_dynamic_rounding_flags" in category_lines
    assert all(line.startswith("package advanced ") for line in category_lines)

    cli_main(["--list", "--suite", "arch,advanced", "--march", "rv32i",
              "--test-id", "I-addi-00"])
    assert capsys.readouterr().out.splitlines() == ["ACT4 arch I-addi-00"]
    cli_main(["--list", "--suite", "invalid", "--march", "rv32i_zicsr",
              "--test-id", "trap-illegal32"])
    assert capsys.readouterr().out.splitlines() == ["package invalid trap-illegal32"]
    cli_main(["--list", "--suite", "basic", "--march", "rv32i",
              "--test-id", "RV64I-addiw"])
    assert capsys.readouterr().out == ""
    with pytest.raises(SystemExit):
        cli_main(["--list", "--instruction", "addi", "--scenario", "alu_raw"])
    with pytest.raises(SystemExit, match="filters require --list"):
        cli_main(["--suite", "basic", "--march", "rv32i", "--instruction", "addi", "--port", "mock"])


@pytest.mark.skipif(not __import__("shutil").which("qemu-riscv32"), reason="QEMU unavailable")
def test_advanced_build_and_corrupted_oracle(tmp_path):
    report = build(tmp_path)
    assert report["cases"] >= 30
    assert report["compiled"] == report["qemu_validated"] == report["cases"]
    entry, segments = elf_segments(tmp_path / "alu_raw.elf")
    assert entry == 0 and len(segments) >= 2
    bad_source = source(CASES[0]).replace("li t0, 15", "li t0, 16")
    path = tmp_path / "bad.S"
    path.write_text(bad_source)
    elf = tmp_path / "bad.elf"
    subprocess.run([PREFIX + "gcc", "-nostdlib", "-static", "-Wl,-Ttext=0x0",
                    "-Wl,--no-relax", "-march=rv32i", "-mabi=ilp32", str(path), "-o", str(elf)], check=True)
    assert subprocess.run(["qemu-riscv32", str(elf)], timeout=5).returncode == 1


def test_malformed_package_rejected(tmp_path):
    path = tmp_path / "bad.elf"
    path.write_bytes(b"not an ELF")
    with pytest.raises(ValueError):
        elf_segments(path)


@pytest.mark.parametrize("source,oracle_type", [
    ("ACT4", "act4_tohost"), ("basic", "selfcheck_tohost"),
    ("advanced", "selfcheck_tohost"), ("invalid", "trap_selfcheck_tohost")])
def test_sparse_oracle_rejects_mismatched_type_and_bad_status_bytes(source, oracle_type):
    package = {"schema_version": 1, "test_source": source, "isa": "rv32i", "entry": 0,
               "segments": [{"address": 0, "file_size": 12, "memory_size": 12,
                             "hex": "000000000000000000000000"}],
               "oracle": {"type": oracle_type, "address": 4, "pass_value": 1,
                          "failure_rule": "odd value greater than 1"},
               "completion": {"type": "tohost_write", "max_cycles": 100}}
    memory = initial_memory(package)
    memory[4] = 1
    assert outcome(package, memory, stopped=True) == "PASS"
    memory[4] = 2
    assert outcome(package, memory, stopped=True) == "INVALID_TEST"
    memory[4] = 256
    with pytest.raises(InvalidPackage, match="invalid bytes"):
        outcome(package, memory, stopped=True)
    del memory[4]
    with pytest.raises(InvalidPackage, match="missing"):
        outcome(package, memory, stopped=True)
    wrong_type = "act4_tohost" if oracle_type != "act4_tohost" else "selfcheck_tohost"
    for field, value in (("type", wrong_type), ("pass_value", 3),
                         ("failure_rule", "anything")):
        bad = {**package, "oracle": {**package["oracle"], field: value}}
        with pytest.raises(InvalidPackage, match="status"):
            initial_memory(bad)
    bad = {**package, "completion": {"type": "tohost_write", "max_cycles": True}}
    with pytest.raises(InvalidPackage, match="completion"):
        initial_memory(bad)
    for field, value, message in (("segments", [None], "segment"),
                                  ("oracle", [], "oracle"),
                                  ("completion", [], "completion")):
        with pytest.raises(InvalidPackage, match=message):
            initial_memory({**package, field: value})


def test_trap_selfcheck_distinguishes_missing_wrong_cause_and_wrong_pc():
    package = {"schema_version": 1, "test_source": "invalid", "isa": "rv32i", "entry": 0,
               "segments": [{"address": 0, "file_size": 12, "memory_size": 12, "hex": "00" * 12}],
               "oracle": {"type": "trap_selfcheck_tohost", "address": 4, "pass_value": 1,
                          "failure_rule": "odd value greater than 1",
                          "trap_failure_codes": TRAP_FAILURE_CODES},
               "completion": {"type": "tohost_write", "max_cycles": 100}}
    memory = initial_memory(package)
    for value, expected in ((1, "PASS"), (3, "EXPECTED_TRAP_MISSING"),
                            (5, "UNEXPECTED_TRAP"), (7, "ARCHITECTURAL_MISMATCH"),
                            (9, "SELF_CHECK_FAILURE")):
        memory[4] = value
        assert outcome(package, memory, stopped=True) == expected
    legacy = {**package, "oracle": {key: value for key, value in package["oracle"].items()
                                     if key != "trap_failure_codes"}}
    memory[4] = 3
    assert outcome(legacy, memory, stopped=True) == "SELF_CHECK_FAILURE"
    bad = {**package, "oracle": {**package["oracle"],
                                 "trap_failure_codes": {"3": "PASS"}}}
    with pytest.raises(InvalidPackage, match="trap failure codes"):
        initial_memory(bad)
    with pytest.raises(InvalidPackage, match="trap failure codes"):
        outcome(bad, memory, stopped=True)


def test_flat_memory_fit_checks_reset_segments_and_status():
    package = {"schema_version": 1, "test_source": "ACT4", "isa": "rv32i", "entry": 0,
               "segments": [{"address": 0, "file_size": 16, "memory_size": 16, "hex": "00" * 16}],
               "oracle": {"type": "act4_tohost", "address": 8, "pass_value": 1,
                          "failure_rule": "odd value greater than 1"},
               "completion": {"type": "tohost_write", "max_cycles": 100}}
    assert flat_memory_fit(package, base=0, size=8192, reset_pc=0, supported_isa={"rv32i"}) == []
    reasons = flat_memory_fit(package, base=4, size=8, reset_pc=4, supported_isa={"rv32i"})
    assert any("entry" in reason for reason in reasons)
    assert any("LOAD" in reason for reason in reasons)
    assert any("tohost" in reason for reason in reasons)
    assert board_memory_bytes("digilent_nexys4_ddr", ROOT.parent / "processor_ci") == 8192
    if (ROOT / "build/act4/packages").exists():
        report = check_dut_fit("picorv32", "digilent_nexys4_ddr", ROOT / "build/act4/packages",
                               processor_ci=ROOT.parent / "processor_ci", base=0, reset_pc=0)
        assert report["checked"] == 39 and report["fit"] == 0
        assert report["smallest_load_file_bytes"] == 77776
        assert report["smallest_load_memory_bytes"] > report["memory_bytes"]


def test_sparse_memory_packing_rejects_overlap_and_bad_lengths():
    package = {"schema_version": 1, "test_source": "basic", "isa": "rv32i", "entry": 0,
               "segments": [{"address": 16, "file_size": 2, "memory_size": 8, "hex": "aabb"},
                            {"address": 0, "file_size": 4, "memory_size": 4, "hex": "01020304"}],
               "oracle": {"type": "selfcheck_tohost", "address": 16, "pass_value": 1,
                          "failure_rule": "odd value greater than 1"},
               "completion": {"type": "tohost_write", "max_cycles": 100}}
    memory = initial_memory(package, supported_isa={"rv32i"})
    assert [memory[i] for i in range(4)] == [1, 2, 3, 4]
    assert [memory[i] for i in range(16, 24)] == [0xaa, 0xbb, 0, 0, 0, 0, 0, 0]
    assert 8 not in memory
    assert flat_memory_fit(package, base=0, size=24, reset_pc=0,
                           supported_isa={"rv32i"}) == []
    bad_segment = {**package, "segments": [{**package["segments"][0], "address": 2},
                                            package["segments"][1]]}
    with pytest.raises(InvalidPackage, match="overlapping segments"):
        initial_memory(bad_segment)
    for changed in ({"file_size": 3}, {"memory_size": 1}, {"hex": "not hex"}):
        bad = {**package, "segments": [{**package["segments"][0], **changed},
                                        package["segments"][1]]}
        with pytest.raises(InvalidPackage, match="segment"):
            initial_memory(bad)
    with pytest.raises(InvalidPackage, match="status"):
        initial_memory({**package, "oracle": {**package["oracle"], "address": 20}})


def test_address_zero_dut_smoke_package_when_available():
    path = ROOT / "build/dut-smoke/picorv32-addi.json"
    if not path.is_file():
        pytest.skip("DUT smoke package not built")
    package = json.loads(path.read_text())
    report = json.loads((ROOT / "reports/dut-smoke-summary.json").read_text())
    assert report["sail_validated"] and report["static_board_fit"]
    assert report["load_memory_bytes"] <= 8192
    assert flat_memory_fit(package, base=0, size=8192, reset_pc=0,
                           supported_isa={"rv32i"}) == []
    memory = initial_memory(package, supported_isa={"rv32i"})
    assert outcome(package, memory, stopped=False) == "INCONCLUSIVE"


def test_serial_sparse_adapter_loads_and_checks_status():
    package = {"schema_version": 1, "test_source": "ACT4", "isa": "rv32i", "entry": 0,
               "segments": [{"address": 0, "file_size": 16, "memory_size": 16, "hex": "00" * 16}],
               "oracle": {"type": "act4_tohost", "address": 8, "pass_value": 1,
                          "failure_rule": "odd value greater than 1"},
               "completion": {"type": "tohost_write", "max_cycles": 100}}

    class MockSerial:
        def __init__(self, value=1, stopped=True, elapsed_cycles=1):
            self.value, self.stopped, self.elapsed_cycles, self.calls = value, stopped, elapsed_cycles, []

        def stop_clk(self): self.calls.append(("stop",))
        def load_msb_accumulator(self, value): self.calls.append(("msb", value))
        def load_lsb_accumulator(self, value): self.calls.append(("lsb", value))
        def write_from_accumulator(self, count, words): self.calls.append(("write", count, words))
        def set_timeout(self, cycles): self.calls.append(("timeout", cycles))
        def set_execution_end_address(self, word): self.calls.append(("end", word))
        def execute_until_stop(self, host_timeout):
            self.calls.append(("execute", host_timeout))
            return b"luck" + ((self.elapsed_cycles << 1) | int(self.stopped)).to_bytes(4, "big")
        def read_memory(self, address):
            self.calls.append(("read", address))
            return (self.value if address == 8 else 0).to_bytes(4, "big")

    device = MockSerial()
    result = run_package(device, package, supported_isa={"rv32i"},
                         memory_base=0, memory_size=64, reset_pc=0)
    assert result["outcome"] == "PASS" and result["tohost"] == 1
    assert device.calls[:4] == [("stop",), ("msb", 0), ("lsb", 0),
                                ("write", 16, [0] * 16)]
    assert ("end", 2) in device.calls and ("read", 8) in device.calls
    for value, stopped, expected in ((3, True, "SELF_CHECK_FAILURE"),
                                     (2, True, "INVALID_TEST"),
                                     (1, False, "TIMEOUT")):
        device = MockSerial(value, stopped)
        assert run_package(device, package, supported_isa={"rv32i"},
                           memory_base=0, memory_size=64, reset_pc=0)["outcome"] == expected
    trap_package = {**package, "test_source": "invalid",
                    "oracle": {**package["oracle"], "type": "trap_selfcheck_tohost",
                               "trap_failure_codes": TRAP_FAILURE_CODES}}
    for value, expected in ((3, "EXPECTED_TRAP_MISSING"),
                            (5, "UNEXPECTED_TRAP"), (7, "ARCHITECTURAL_MISMATCH")):
        result = run_package(MockSerial(value), trap_package, supported_isa={"rv32i"},
                             memory_base=0, memory_size=64, reset_pc=0)
        assert result["outcome"] == expected and result["tohost"] == value
    boundary = MockSerial(1, True, elapsed_cycles=100)
    assert run_package(boundary, package, supported_isa={"rv32i"},
                       memory_base=0, memory_size=64, reset_pc=0)["outcome"] == "TIMEOUT"
    device = MockSerial()
    with pytest.raises(InvalidPackage, match="does not fit"):
        run_package(device, package, supported_isa={"rv32i"},
                    memory_base=0, memory_size=8, reset_pc=0)
    assert device.calls == []

    shifted = {**package, "entry": 4, "segments": [{"address": 4, "file_size": 16,
                "memory_size": 16, "hex": "00" * 16}],
               "oracle": {**package["oracle"], "address": 12}}
    with pytest.raises(InvalidPackage, match="zero-based"):
        run_package(MockSerial(), shifted, supported_isa={"rv32i"},
                    memory_base=4, memory_size=64, reset_pc=4)

    class BadResponse(MockSerial):
        def execute_until_stop(self, host_timeout): return b"invalid!"

    with pytest.raises(RuntimeError, match="completion response"):
        run_package(BadResponse(), package, supported_isa={"rv32i"},
                    memory_base=0, memory_size=64, reset_pc=0)

    diagnostic_text = ("RVCP: ===== TRAP FAILURE DIAGNOSTICS =====\n"
                       "RVCP: XEPC: 0x00000088\nRVCP: XCAUSE: 0x00000002\n")

    class DiagnosticSerial(MockSerial):
        def __init__(self): super().__init__(3)
        def write_memory(self, address, value): self.calls.append(("clear_diagnostics", address, value))
        def read_memory(self, address):
            if address == 8:
                return (3).to_bytes(4, "big")
            if address == 64:
                return len(diagnostic_text).to_bytes(4, "big")
            if address == 68:
                return (1024).to_bytes(4, "big")
            offset = address - (64 + 0x100)
            value = int.from_bytes(diagnostic_text.encode()[offset:offset+4].ljust(4, b"\0"), "little")
            return value.to_bytes(4, "big")

    diagnostic_device = DiagnosticSerial()
    diagnostic_result = run_package(diagnostic_device, package, supported_isa={"rv32i"},
                                    memory_base=0, memory_size=64, reset_pc=0,
                                    diagnostic_base=64)
    assert diagnostic_result["outcome"] == "UNEXPECTED_TRAP"
    assert diagnostic_result["diagnostics"]["trap_cause"] == 2
    assert diagnostic_result["diagnostics"]["trap_epc"] == 0x88
    assert ("clear_diagnostics", 64, 0) in diagnostic_device.calls


@pytest.mark.skipif(not CONTROLLER_RTL.is_dir() or not shutil.which("iverilog") or
                    not shutil.which("verilator"), reason="RV-Bench controller RTL or simulator unavailable")
def test_controller_rtl_completion_probe(tmp_path):
    report = probe_controller_rtl(tmp_path / "controller.json")
    assert report["interpreter_protocol"] == "passed"
    assert report["idle_address_triggers_finish"] is False
    assert report["primary_write_qualified_finish"]
    assert report["data_write_qualified_finish"]
    assert report["shared_512k_memory"].startswith("passed")
    assert report["act_diagnostic_window_serial_readable"]
    assert report["decoded_trap_cause_available"] is False


def test_act4_status_is_not_breakpoint_only():
    assert classify_tohost(1, stopped=True) == "PASS"
    assert classify_tohost(3, stopped=True) == "SELF_CHECK_FAILURE"
    assert classify_tohost(1, stopped=True, timed_out=True) == "TIMEOUT"
    assert classify_tohost(1, stopped=True, trapped=True) == "UNEXPECTED_TRAP"
    assert classify_tohost(0, stopped=True) == "INCONCLUSIVE"
    assert classify_tohost(1, stopped=False) == "INCONCLUSIVE"


def test_act4_conversion_rejects_non_act_elf(tmp_path):
    if not (ROOT / "build/advanced/alu_raw.elf").exists():
        pytest.skip("advanced ELF unavailable")
    with pytest.raises(ValueError, match="tohost"):
        convert(ROOT / "build/advanced/alu_raw.elf", isa="rv32i", revision="test")


def test_act4_sparse_package_mock_and_failures(tmp_path):
    assembly = tmp_path / "act_style.S"
    assembly.write_text(".global _start\n_start: la t0, tohost\nli t1, 1\nsw t1, 0(t0)\nli a0, 0\nli a7, 93\necall\n.section .data\n.balign 8\n.global tohost\ntohost: .dword 0\n")
    elf = tmp_path / "act_style.elf"
    subprocess.run([PREFIX + "gcc", "-nostdlib", "-static", "-Wl,-Ttext=0x0",
                    "-Wl,--no-relax", "-march=rv32i", "-mabi=ilp32", str(assembly), "-o", str(elf)], check=True)
    package = convert(elf, isa="rv32i", revision="6e8a45123f14cebfb3df151a0e7b849b4389b33b")
    memory = initial_memory(package, supported_isa={"rv32i"})
    assert outcome(package, memory, stopped=True) == "INCONCLUSIVE"
    address = package["oracle"]["address"]
    memory[address] = 1
    assert outcome(package, memory, stopped=True) == "PASS"
    memory[address] = 3
    assert outcome(package, memory, stopped=True) == "SELF_CHECK_FAILURE"
    assert outcome(package, memory, stopped=True, timed_out=True) == "TIMEOUT"
    assert outcome(package, memory, stopped=True, trapped=True) == "UNEXPECTED_TRAP"
    with pytest.raises(InvalidPackage, match="unsupported ISA"):
        initial_memory(package, supported_isa={"rv64i"})
    bad = {**package, "segments": []}
    with pytest.raises(InvalidPackage, match="missing LOAD"):
        initial_memory(bad)
    bad = {**package, "entry": 0xffffffff}
    with pytest.raises(InvalidPackage, match="entry"):
        initial_memory(bad)


def test_generated_act4_packages_when_available():
    paths = sorted((ROOT / "build" / "act4" / "packages").glob("*.json"))
    if not paths:
        pytest.skip("ACT4 toolchain not installed in default CI")
    assert len(paths) >= 1
    for path in paths:
        package = json.loads(path.read_text())
        memory = initial_memory(package, supported_isa={"rv32i"})
        assert package["provenance"]["revision"] == "6e8a45123f14cebfb3df151a0e7b849b4389b33b"
        assert outcome(package, memory, stopped=False) == "INCONCLUSIVE"


def test_advanced_sail_package_when_available():
    path = ROOT / "build/advanced-sail/alu_raw.json"
    if not path.is_file():
        pytest.skip("advanced Sail packages not built")
    package = json.loads(path.read_text())
    assert package["test_source"] == "advanced"
    memory = initial_memory(package, supported_isa={"rv32i"})
    assert outcome(package, memory, stopped=False) == "INCONCLUSIVE"
    memory[package["oracle"]["address"]] = 1
    assert outcome(package, memory, stopped=True) == "PASS"
    for name, isa in (("atomic_result_load", "rv32ia"),
                      ("fp_single_dependency", "rv32if_zicsr"),
                      ("fp_double_to_integer", "rv32ifd_zicsr"),
                      ("fp_invalid_sqrt_flag", "rv32if_zicsr"),
                      ("fp_dynamic_rounding_flags", "rv32if_zicsr"),
                      ("rv64_store_load_dependency", "rv64i"),
                      ("vector_load_add_store", "rv32im_zicsr_zve32x_zvl128b"),
                      ("vector_e64_two_lane_store", "rv32im_zicsr_zve64x_zvl128b"),
                      ("vector_mask_undisturbed", "rv32im_zicsr_zve32x_zvl128b"),
                      ("vector_tail_undisturbed", "rv32im_zicsr_zve32x_zvl128b"),
                      ("vector_vstart_csr_reset", "rv32im_zicsr_zve32x_zvl128b"),
                      ("vector_vstart_load_resume", "rv32im_zicsr_zve32x_zvl128b"),
                      ("vector_vxsat_sticky", "rv32im_zicsr_zve32x_zvl128b")):
        special = json.loads((ROOT / "build/advanced-sail" / f"{name}.json").read_text())
        assert special["isa"] == isa
        assert outcome(special, initial_memory(special, supported_isa={isa}), stopped=False) == "INCONCLUSIVE"
        if name == "vector_load_add_store":
            assert special["vector_profile"]["minimum_vlen_bits"] == 128
            assert special["vector_profile"]["vl"] == 2
        if name == "vector_e64_two_lane_store":
            assert special["vector_profile"]["extension"] == "Zve64x"
            assert special["vector_profile"]["sew_bits"] == 64
        if name in ("vector_mask_undisturbed", "vector_vstart_csr_reset", "vector_vstart_load_resume"):
            assert special["vector_profile"]["vl"] == 4
        if name == "vector_tail_undisturbed":
            assert special["vector_profile"]["vl"] == 2
        if name == "vector_vxsat_sticky":
            assert special["vector_profile"]["sew_bits"] == 8


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
def test_basic_sail_build_and_corrupted_expectation(tmp_path):
    report = build_basic(tmp_path / "basic")
    assert report["tests"] == report["sail_validated"] == len(BASIC_CASES)
    assert all(row["instruction_bits"] == (16 if row["instruction"].startswith("c.") else 32)
               for row in report["results"])
    package = json.loads((tmp_path / "basic" / "RV32M-mul.json").read_text())
    memory = initial_memory(package, supported_isa={"rv32im"})
    assert outcome(package, memory, stopped=False) == "INCONCLUSIVE"
    bad_source = basic_source(next(c for c in BASIC_CASES if c[1] == "mul")).replace("li t0, 42", "li t0, 43")
    source_path = tmp_path / "bad_basic.S"
    source_path.write_text(bad_source)
    elf = tmp_path / "bad_basic.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", "-march=rv32im", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(source_path), "-o", str(elf)], check=True)
    run = subprocess.run([str(SAIL_EXE), "--config", str(SAIL_CONFIG), str(elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE" in run.stdout


def test_compressed_target_rejects_32bit_substitute(tmp_path):
    case = next(item for item in BASIC_CASES if item[0] == "RV32C" and item[1] == "c.addi")
    original = basic_source(case)
    assert original.count("c.addi a0, 2") == 1
    wrong = original.replace("c.addi a0, 2", ".option push\n.option norvc\naddi a0, a0, 2\n.option pop")
    source_path = tmp_path / "wide_addi.S"
    elf = tmp_path / "wide_addi.elf"
    source_path.write_text(wrong)
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", "-march=rv32ic", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(source_path), "-o", str(elf)],
                   check=True)
    disassembly = subprocess.check_output([BASIC_OBJDUMP, "-M", "no-aliases", "-d", str(elf)], text=True)
    assert "addi\ta0,a0,2" in disassembly
    with pytest.raises(RuntimeError, match="16-bit opcode"):
        target_encoding(disassembly, "c.addi")


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
def test_vector_vstart_arithmetic_is_configuration_dependent(tmp_path):
    report = probe_vector_vstart(tmp_path / "probe", tmp_path / "report.json")
    assert report["disassembly_verified"]
    assert report["qemu_resumed"]
    assert report["sail_default_trap_observed"]
    assert report["sail_arithmetic_resume_override_validated"]
    assert report["sail_zve32x_vlen128_resume_validated"]
    assert report["hardware_validated"] == 0


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
def test_vector_profile_and_corrupted_expected_value(tmp_path):
    case = next(c for c in BASIC_CASES if c[0] == "RV32Zve32x" and c[1] == "vadd.vv")
    package = json.loads((ROOT / "build/basic-sail/RV32Zve32x-vadd.vv.json").read_text())
    assert package["vector_profile"]["minimum_vlen_bits"] == 128
    assert package["vector_profile"]["sew_bits"] == 32
    assert package["vector_profile"]["lmul"] == "m1"
    for name, sew in (("vle8.v", 8), ("vnclip.wi", 16), ("vwadd.vv", 16)):
        specialized = json.loads((ROOT / "build/basic-sail" / f"RV32Zve32x-{name}.json").read_text())
        assert specialized["vector_profile"]["sew_bits"] == sew
    whole = json.loads((ROOT / "build/basic-sail/RV32Zve32x-vl8re32.v.json").read_text())
    assert whole["completion"]["max_cycles"] == 200000
    assert max(segment["memory_size"] for segment in whole["segments"]) >= 2 * 65536
    higher = json.loads((ROOT / "build/basic-sail/RV32Zve64x-vsext.vf8.json").read_text())
    assert higher["vector_profile"]["extension"] == "Zve64x"
    assert higher["vector_profile"]["sew_bits"] == 64
    fp = json.loads((ROOT / "build/basic-sail/RV32Zve32f-vfadd.vv.json").read_text())
    assert fp["vector_profile"]["extension"] == "Zve32f"
    wide = json.loads((ROOT / "build/basic-sail/RV32Zve64d-vfwadd.vv.json").read_text())
    assert wide["vector_profile"]["extension"] == "Zve64d"
    indexed64 = json.loads((ROOT / "build/basic-sail/RV64Zve64x-vluxei64.v.json").read_text())
    assert indexed64["isa"].startswith("rv64")
    assert outcome(package, initial_memory(package, supported_isa={case[2]}), stopped=False) == "INCONCLUSIVE"
    assert outcome(package, initial_memory(package, supported_isa={"rv32imv"}), stopped=False) == "INCONCLUSIVE"
    with pytest.raises(InvalidPackage, match="unsupported ISA"):
        initial_memory(package, supported_isa={"rv32im_zicsr_zve32x_zvl64b"})
    bad = tmp_path / "bad_vector.S"
    bad.write_text(basic_source(case).replace("li t0, 5\nbne a0", "li t0, 6\nbne a0"))
    elf = tmp_path / "bad_vector.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={case[2]}", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(bad), "-o", str(elf)], check=True)
    run = subprocess.run([str(SAIL_EXE), "--config", str(CONFIG_Z), str(elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE" in run.stdout
    fp_case = next(c for c in BASIC_CASES if c[0] == "RV32Zve32f" and c[1] == "vfadd.vv")
    bad_fp = tmp_path / "bad_vector_fp.S"
    bad_fp.write_text(basic_source(fp_case).replace(
        f"li t0, {fp_case[3]}\nbne a0", f"li t0, {fp_case[3] + 1}\nbne a0"))
    bad_fp_elf = tmp_path / "bad_vector_fp.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={fp_case[2]}", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(bad_fp), "-o", str(bad_fp_elf)], check=True)
    fp_run = subprocess.run([str(SAIL_EXE), "--config", str(CONFIG_Z), str(bad_fp_elf)],
                            capture_output=True, text=True, timeout=10)
    assert fp_run.returncode != 0 and "FAILURE" in fp_run.stdout


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
def test_expected_trap_rejects_wrong_cause(tmp_path):
    trap_report = json.loads((ROOT / "reports/invalid-sail-summary.json").read_text())
    assert {(r["instruction"], r["mcause"]) for r in trap_report["results"]
            if r["allow_misaligned_negative_rejected"]} == {("misaligned_load", 4), ("misaligned_store", 6)}
    target, march, cause = TRAP_CASES[0]
    src = tmp_path / "wrong_cause.S"
    src.write_text(trap_source(target, cause).replace("li t2, 11", "li t2, 3"))
    elf = tmp_path / "wrong_cause.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={march}", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)], check=True)
    run = subprocess.run([str(SAIL_EXE), "--config", str(SAIL_CONFIG), str(elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE: 2 " in run.stdout
    bad_pc = tmp_path / "wrong_mepc.S"
    bad_pc.write_text(trap_source("illegal_csr", 2).replace("la t2, trigger", "la t2, trap_handler"))
    bad_pc_elf = tmp_path / "wrong_mepc.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", "-march=rv32i_zicsr", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(bad_pc), "-o", str(bad_pc_elf)], check=True)
    run = subprocess.run([str(SAIL_EXE), "--config", str(SAIL_CONFIG), str(bad_pc_elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE: 3 " in run.stdout
    u_target, u_march, _ = next(c for c in TRAP_CASES if c[0] == "u_mode_mret")
    u_bad = tmp_path / "wrong_u_cause.S"
    u_bad.write_text(trap_source(u_target, 3))
    u_elf = tmp_path / "wrong_u_cause.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={u_march}", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(u_bad), "-o", str(u_elf)], check=True)
    u_run = subprocess.run([str(SAIL_EXE), "--config", str(CONFIG_Z), str(u_elf)],
                           capture_output=True, text=True, timeout=10)
    assert u_run.returncode != 0 and "FAILURE" in u_run.stdout


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
def test_replaced_invalid_placeholders_and_fp_enabled_negative(tmp_path):
    replacements = json.loads((ROOT / "reports/isa-audit/invalid_replacements.json").read_text())
    retired = json.loads((ROOT / "reports/isa-audit/legacy_invalid_retired.json").read_text())
    assert len(retired) == 60
    assert {row["status"] for row in retired} == {
        "replaced_by_package", "retired_undefined_placeholder"}
    assert sum(row["status"] == "replaced_by_package" for row in retired) == 3
    assert not list((ROOT / "tests").glob("RV*/invalid/src/*-invalid*.s"))
    for row in retired:
        source = ROOT / row["source"]
        assert not source.exists()
        for folder in ("memory", "reference"):
            assert not (source.parents[1] / folder / f"{source.stem}.hex").exists()
    assert {row["package"] for row in replacements} == {
        "build/invalid-sail/illegal32.json", "build/invalid-sail/illegal16.json",
        "build/invalid-sail/fp_disabled_fadd.json"}
    for row in replacements:
        assert not (ROOT / row["legacy_placeholder"]).exists()
        package = json.loads((ROOT / row["package"]).read_text())
        assert package["replaces_legacy_placeholder"] == row["legacy_placeholder"]
        assert package["expected_trap_cause"] == row["expected_mcause"]
        assert package["source_path"].split("/")[1] == row["legacy_placeholder"].split("/")[1]

    target, march, cause = next(case for case in TRAP_CASES if case[0] == "fp_disabled_fadd")
    enabled = trap_source(target, cause).replace(
        "_start:\n", "_start:\nli t6, 0x6000\ncsrs mstatus, t6\n", 1)
    src = tmp_path / "fp_enabled.S"
    src.write_text(enabled)
    elf = tmp_path / "fp_enabled.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={march}", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)], check=True)
    run = subprocess.run([str(SAIL_EXE), "--config", str(SAIL_CONFIG), str(elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE: 1 " in run.stdout


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
@pytest.mark.parametrize("target", ["fp_disabled_fadd_d", "rv64_fp_disabled_fadd_s",
                                     "rv64_fp_disabled_fadd_d", "vector_disabled_vset",
                                     "amo_misaligned_word", "rv64_amo_misaligned_double"])
def test_new_state_traps_reject_restored_legal_state(tmp_path, target):
    _, march, cause = next(case for case in TRAP_CASES if case[0] == target)
    program = trap_source(target, cause)
    if target.startswith(("fp_disabled_", "rv64_fp_disabled_")):
        program = program.replace("_start:\n", "_start:\nli t6, 0x6000\ncsrs mstatus, t6\n", 1)
    elif target == "vector_disabled_vset":
        program = program.replace("_start:\n", "_start:\nli t6, 0x600\ncsrs mstatus, t6\n", 1)
    else:
        assert program.count("addi t4, t4, 1") == 1
        program = program.replace("addi t4, t4, 1", "addi t4, t4, 0")
    src = tmp_path / f"legal_{target}.S"
    src.write_text(program)
    elf = tmp_path / f"legal_{target}.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={march}",
                    "-mabi=lp64" if march.startswith("rv64") else "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)], check=True)
    config = (CONFIG_Z if target == "vector_disabled_vset" else
              CONFIG64 if march.startswith("rv64") else SAIL_CONFIG)
    run = subprocess.run([str(SAIL_EXE), "--config", str(config), str(elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE: 1 " in run.stdout


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
@pytest.mark.parametrize("group,target", [("RV32A", "amoadd.w"),
                                           ("RV32D", "fadd.d"),
                                           ("RV64I", "addiw")])
def test_atomic_double_and_rv64_basic_oracles_reject_bad_result(tmp_path, group, target):
    case = next(case for case in BASIC_CASES if case[:2] == (group, target))
    expected_line = f"li t0, {case[3]}\nbne a0, t0, failure"
    program = basic_source(case)
    assert program.count(expected_line) == 1
    src = tmp_path / f"bad_{target}.S"
    src.write_text(program.replace(expected_line,
                                   f"li t0, {case[3] + 1}\nbne a0, t0, failure"))
    elf = tmp_path / f"bad_{target}.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={case[2]}",
                    "-mabi=lp64" if group.startswith("RV64") else "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)], check=True)
    config = CONFIG64 if group.startswith("RV64") else SAIL_CONFIG
    run = subprocess.run([str(SAIL_EXE), "--config", str(config), str(elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE" in run.stdout


@pytest.mark.skipif(not SAIL_EXE.is_file() or not shutil.which("qemu-riscv32"),
                    reason="Sail or QEMU unavailable")
def test_vector_lmul_boundary_and_resumed_store_reject_corruption(tmp_path):
    cases = {case[0]: case for case in CASES}
    group = cases["vector_lmul2_cross_register"]
    resumed = cases["vector_vstart_store_resume"]
    assert json.loads((ROOT / "build/advanced-sail/vector_lmul2_cross_register.json").read_text())[
        "vector_profile"]["lmul"] == "m2"
    mutations = (
        (group, "addi t6, t4, 2\nbne t5, t6, failure",
         "addi t6, t4, 2\nli t0, 17\nbne t4, t0, 2f\naddi t6, t6, 1\n2: bne t5, t6, failure"),
        (resumed, "lw t2, 0(t1)\nli t3, 9\nbne t2, t3, failure",
         "lw t2, 0(t1)\nli t3, 5\nbne t2, t3, failure"),
        (cases["vector_fractional_lmul_half"], "addi t6, t4, 3\nbne t5, t6, failure",
         "addi t6, t4, 4\nbne t5, t6, failure"),
        (cases["vector_lmul8_e16_cross_register"], "li t5, 7\nbne t4, t5, failure",
         "li t5, 8\nbne t4, t5, failure"),
        (cases["vector_vxrm_rounding_modes"],
         "vmv.x.s t1, v2\nli t2, 2\nbne t1, t2, failure\ncsrrwi zero, vxrm, 2",
         "vmv.x.s t1, v2\nli t2, 3\nbne t1, t2, failure\ncsrrwi zero, vxrm, 2"),
        (cases["vector_masked_store_preserves_memory"],
         "lw t2, 0(t1)\nli t3, 9\nbne t2, t3, failure",
         "lw t2, 0(t1)\nli t3, 5\nbne t2, t3, failure"),
        (cases["vector_vlmax_sew_lmul_clamp"],
         "slli t2, t1, 1\nbne t0, t2, failure",
         "slli t2, t1, 2\nbne t0, t2, failure"),
    )
    for case, expected, corrupted in mutations:
        for mode, program, compiler, text_address, config in (
                ("qemu", source(case), PREFIX + "gcc", "0x0", None),
                ("sail", sail_source(case), BASIC_GCC, "0x80000000", CONFIG_Z)):
            assert program.count(expected) == 1
            src = tmp_path / f"{case[0]}_{mode}.S"
            src.write_text(program.replace(expected, corrupted))
            elf = tmp_path / f"{case[0]}_{mode}.elf"
            subprocess.run([compiler, "-nostdlib", "-static", f"-march={case[2]}",
                            "-mabi=ilp32", f"-Wl,-Ttext={text_address}", "-Wl,--no-relax",
                            str(src), "-o", str(elf)], check=True)
            command = (["qemu-riscv32", str(elf)] if config is None else
                       [str(SAIL_EXE), "--config", str(config), str(elf)])
            run = subprocess.run(command, capture_output=True, text=True, timeout=10)
            assert run.returncode != 0
            if config is not None:
                assert "FAILURE" in run.stdout


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
def test_advanced_sail_rejects_corrupted_expected_value(tmp_path):
    src = tmp_path / "bad_advanced.S"
    src.write_text(sail_source(CASES[0]).replace("li t0, 15", "li t0, 16"))
    elf = tmp_path / "bad_advanced.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", "-march=rv32i", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)], check=True)
    run = subprocess.run([str(SAIL_EXE), "--config", str(SAIL_CONFIG), str(elf)],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode != 0 and "FAILURE" in run.stdout
    fp_case = next(case for case in CASES if case[0] == "fp_invalid_sqrt_flag")
    fp_src = tmp_path / "wrong_fp_flag.S"
    fp_src.write_text(sail_source(fp_case).replace("li t3, 16\n", "li t3, 0\n"))
    fp_elf = tmp_path / "wrong_fp_flag.elf"
    subprocess.run([BASIC_GCC, "-nostdlib", "-static", f"-march={fp_case[2]}", "-mabi=ilp32",
                    "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(fp_src), "-o", str(fp_elf)], check=True)
    fp_run = subprocess.run([str(SAIL_EXE), "--config", str(SAIL_CONFIG), str(fp_elf)],
                            capture_output=True, text=True, timeout=10)
    assert fp_run.returncode != 0 and "FAILURE" in fp_run.stdout


@pytest.mark.skipif(not SAIL_EXE.is_file(), reason="Sail unavailable")
def test_fp_dynamic_rounding_rejects_wrong_mode(tmp_path):
    case = next(item for item in CASES if item[0] == "fp_dynamic_rounding_flags")
    expected = "li t1, 1\ncsrrw zero, frm, t1\n"
    wrong = "li t1, 3\ncsrrw zero, frm, t1\n"
    qemu_source = source(case)
    sail_program = sail_source(case)
    assert qemu_source.count(expected) == sail_program.count(expected) == 1
    for label, program, address, compiler, config in (
            ("qemu", qemu_source.replace(expected, wrong), "0x0", PREFIX + "gcc", None),
            ("sail", sail_program.replace(expected, wrong), "0x80000000", BASIC_GCC, SAIL_CONFIG)):
        src = tmp_path / f"wrong_rounding_{label}.S"
        elf = tmp_path / f"wrong_rounding_{label}.elf"
        src.write_text(program)
        subprocess.run([compiler, "-nostdlib", "-static", f"-march={case[2]}", "-mabi=ilp32",
                        f"-Wl,-Ttext={address}", "-Wl,--no-relax", str(src), "-o", str(elf)],
                       check=True)
        command = (["qemu-riscv32", str(elf)] if config is None else
                   [str(SAIL_EXE), "--config", str(config), str(elf)])
        run = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if config is None:
            assert run.returncode == 1 and not run.stderr
        else:
            assert run.returncode != 0
            assert "FAILURE" in run.stdout
