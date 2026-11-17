"""Adapter checks; the real PyFlow test runs when its optional tools are installed."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from riscv_test_runner.cli import main as cli_main
from riscv_test_runner.core.package import InvalidPackage, flat_memory_fit, initial_memory
from riscv_test_runner.core.serial_package import run_package
from riscv_test_runner.riscv_dv import (HostMock, ReferenceTrap, UPSTREAM,
                                       check_split_segments, custom_profile, instrument,
                                       floating_state_at_done, parse_spike_trace,
                                       reference_memory_accesses,
                                       select_memory_signature, stage_pyflow_compat,
                                       stage_rv64i_target, stage_rv64imfdc_target,
                                       stage_user_target,
                                       stage_csr_generator, validate_mscratch_map,
                                       symbol, trace_reference, verify_saved_package)


def package() -> dict:
    return {"schema_version": 1, "test_source": "riscv-dv", "test_id": "mock",
            "isa": "rv32i", "entry": 0,
            "segments": [{"address": 0, "virtual_address": 0, "file_size": 16,
                          "memory_size": 16, "flags": 7, "hex": "00" * 16}],
            "oracle": {"type": "selfcheck_tohost", "address": 8,
                       "pass_value": 1, "failure_rule": "odd value greater than 1"},
            "completion": {"type": "tohost_write", "max_cycles": 100}}


def test_riscvdv_package_uses_existing_serial_contract():
    p = package()
    assert run_package(HostMock(), p, supported_isa={"rv32i"}, memory_base=0,
                       memory_size=16, reset_pc=0)["outcome"] == "PASS"

    class FailingMock(HostMock):
        def execute_until_stop(self, host_timeout: float) -> bytes:
            self.words[self.stop_address] = 3
            return b"luck" + (3).to_bytes(4, "big")

    assert run_package(FailingMock(), p, supported_isa={"rv32i"}, memory_base=0,
                       memory_size=16, reset_pc=0)["outcome"] == "SELF_CHECK_FAILURE"

    class TimeoutMock(HostMock):
        def execute_until_stop(self, host_timeout: float) -> bytes:
            return b"luck" + (self.cycles << 1).to_bytes(4, "big")

    assert run_package(TimeoutMock(), p, supported_isa={"rv32i"}, memory_base=0,
                       memory_size=16, reset_pc=0)["outcome"] == "TIMEOUT"
    assert flat_memory_fit(p, base=0, size=8, reset_pc=0,
                           supported_isa={"rv32i"})
    shifted = {**p, "entry": 0x80000000,
               "segments": [{**p["segments"][0], "address": 0x80000000,
                             "virtual_address": 0x80000000}],
               "oracle": {**p["oracle"], "address": 0x80000008}}
    assert run_package(HostMock(), shifted, supported_isa={"rv32i"},
                       memory_base=0x80000000, memory_size=16,
                       reset_pc=0x80000000)["outcome"] == "PASS"
    bad = {**p, "entry": 32}
    with pytest.raises(InvalidPackage, match="entry"):
        initial_memory(bad)


def test_riscvdv_instrument_checks_registers_before_completion():
    source = ".section .text\n    la x31, test_done\ntest_done:\n    li gp, 1\n    j write_tohost\n"
    checked = instrument(source, list(range(32)), 32)
    assert "bne x1, x31, processorci_fail" in checked
    assert "bne x30, x31, processorci_fail" in checked
    assert "bne x31" not in checked
    assert checked.index("bne x1") < checked.index("li gp, 1")
    assert "processorci_fail:\n    li gp, 3" in checked
    with pytest.raises(ValueError, match="test_done"):
        instrument(".section .text\n", list(range(32)), 32)


def test_riscvdv_spike_memory_signature_handles_overlapping_stores(tmp_path):
    trace = tmp_path / "reference.trace"
    trace.write_text("""\
core   0: 0x00000004 (0x00100093) addi    ra, zero, 1
core   0: 3 0x00000004 (0x00100093) x1 0x00000001
core   0: 0x00000008 (0x00612023) sw      t1, 0(sp)
core   0: 3 0x00000008 (0x00612023) mem 0x00000200 0x11223344
core   0: 0x0000000c (0x006100a3) sb      t1, 1(sp)
core   0: 3 0x0000000c (0x006100a3) mem 0x00000201 0x99
core   0: 0x00000010 (0x00012183) lw      gp, 0(sp)
core   0: 3 0x00000010 (0x00012183) x3 0x11229944 mem 0x00000200
core   0: 0x00000020 (0x0000006f) j       test_done
core   0: 3 0x00000020 (0x0000006f)
core   0: 0x00000024 (0x00312023) sw      gp, 0(sp)
core   0: 3 0x00000024 (0x00312023) mem 0x00000200 0x12345678
core   0: 0x00000028 (0x00312023) sw      gp, 0(sp)
core   0: 3 0x00000028 (0x00312023) mem 0x00000100 0x00000001
""")
    registers, written = parse_spike_trace(trace, done=0x20, tohost=0x100,
                                           memory_base=0, memory_size=0x400)
    assert registers[1] == 1
    assert registers[3] == 0x11229944
    assert written == {0x200: 0x44, 0x201: 0x99, 0x202: 0x22, 0x203: 0x11}
    assert select_memory_signature(written) == written
    selected = select_memory_signature({i: i for i in range(100)})
    assert len(selected) == 64 and 0 in selected and 99 in selected
    assert list(select_memory_signature({i: i for i in range(100)}, 4)) == [0, 33, 66, 99]
    assert list(select_memory_signature({i: i for i in range(100)}, 1)) == [0]
    with pytest.raises(ValueError, match="1 to 1024"):
        select_memory_signature({0: 0}, 0)
    with pytest.raises(RuntimeError, match="outside selected RAM"):
        parse_spike_trace(trace, done=0x20, tohost=0x100,
                          memory_base=0, memory_size=0x202)
    trace.write_text(trace.read_text().replace("sw      t1, 0(sp)",
                                               "cbo.zero 0(sp)"))
    with pytest.raises(RuntimeError, match="unsupported memory operation"):
        parse_spike_trace(trace, done=0x20, tohost=0x100,
                          memory_base=0, memory_size=0x400)


def test_riscvdv_spike_trap_reports_cause_and_pc(tmp_path):
    trace = tmp_path / "reference.trace"
    trace.write_text("core   0: 0x0000002c (0xf20b8053) fmv.d.x ft0, s7\n"
                     "core   0: exception trap_illegal_instruction, epc 0x0000002c\n"
                     "core   0:           tval 0x00000000f20b8053\n")
    with pytest.raises(ReferenceTrap, match="trap_illegal_instruction at PC 0x2c") as error:
        parse_spike_trace(trace, done=0x100, tohost=0x200,
                          memory_base=0, memory_size=0x1000)
    assert error.value.cause == "trap_illegal_instruction"
    assert error.value.epc == 0x2c


def test_riscvdv_floating_commit_and_fcsr_signature(tmp_path):
    trace = tmp_path / "reference.trace"
    lines = ["core   0: 0x00000004 (0x0021d073) csrwi frm, 3\n",
             "core   0: 3 0x00000004 (0x0021d073) c2_frm 0x3\n"]
    for number in range(32):
        lines.append(f"core   0: 3 0x00000008 (0xf20b8053) f{number} 0x{number:x}\n")
    lines += ["core   0: 3 0x0000000c (0xc21d71d3) c1_fflags 0x11 x3 0xffffffffffffffff\n",
              "core   0: 0x00000020 (0x00000013) nop\n",
              "core   0: 3 0x00000024 (0x00312023) mem 0x00000100 0x00000001\n"]
    trace.write_text("".join(lines))
    gpr, _ = parse_spike_trace(trace, done=0x20, tohost=0x100,
                               memory_base=0, memory_size=0x1000)
    assert gpr[3] == 0xffffffffffffffff
    fpr, fcsr = floating_state_at_done(trace, done=0x20)
    assert fpr == list(range(32)) and fcsr == 0x71
    source = ".section .text\n    la x14, test_done\ntest_done:\n    li gp, 1\n    j write_tohost\n"
    checked = instrument(source, gpr, 64, floating_signature=(fpr, fcsr))
    assert "fmv.x.d x1, f31" in checked
    assert "csrr x1, fcsr\n    li x14, 0x71" in checked


def test_riscvdv_instrument_checks_selected_memory_after_registers():
    source = ".section .text\n    la x31, test_done\ntest_done:\n    li gp, 1\n    j write_tohost\n"
    checked = instrument(source, list(range(32)), 32, {0x200: 0x44})
    assert "lbu x1, 0(x31)" in checked
    assert "li x31, 0x44\n    bne x1, x31, processorci_fail" in checked
    assert checked.index("bne x30") < checked.index("lbu x1") < checked.index("li gp, 1")


def test_riscvdv_split_regions_keep_instruction_and_data_loads_separate():
    segments = [{"address": 0x80000000, "memory_size": 0x100, "flags": 5},
                {"address": 0x80020000, "memory_size": 0x100, "flags": 6}]
    check_split_segments(segments, memory_base=0x80000000,
                         data_base=0x80020000, memory_end=0x80080000)
    with pytest.raises(RuntimeError, match="data LOAD"):
        check_split_segments([{**segments[1], "address": 0x80001000}, segments[0]],
                             memory_base=0x80000000, data_base=0x80020000,
                             memory_end=0x80080000)


def test_riscvdv_invalid_isa_rejected():
    with pytest.raises(SystemExit, match="2"):
        cli_main(["--tool", "riscv-dv", "--isa", "rv32e"])


def test_riscvdv_custom_testlist_checks_streams_and_controls(tmp_path):
    pytest.importorskip("yaml")
    testlist = tmp_path / "testlist.yaml"
    prefix = "- test: riscv_rand_instr_test\n  gen_test: riscv_instr_base_test\n  gen_opts: "
    testlist.write_text(prefix + "+instr_cnt=80 +num_of_sub_program=0 +directed_instr_0=riscv_jal_instr,5\n")
    entry, digest = custom_profile(testlist, "riscv_rand_instr_test",
                                   load_store=False, floating=False)
    assert entry["test"] == "riscv_rand_instr_test"
    assert digest == hashlib.sha256(testlist.read_bytes()).hexdigest()
    testlist.write_text(prefix + "+instr_cnt=80 +directed_instr_0=riscv_amo_instr_stream,5\n")
    with pytest.raises(ValueError, match="unvalidated custom directed stream"):
        custom_profile(testlist, "riscv_rand_instr_test", load_store=False, floating=False)
    testlist.write_text(prefix + "+instr_cnt=80 +bare_program_mode=0\n")
    with pytest.raises(ValueError, match="cannot change bare_program_mode"):
        custom_profile(testlist, "riscv_rand_instr_test", load_store=False, floating=False)
    testlist.write_text(prefix + "+instr_cnt=80 +directed_instr_0=riscv_load_store_rand_instr_stream,5\n")
    with pytest.raises(ValueError, match="requires --load-store"):
        custom_profile(testlist, "riscv_rand_instr_test", load_store=False, floating=False)


def test_riscvdv_staged_pyflow_fixes_leave_pinned_source_unchanged(tmp_path):
    sources = [UPSTREAM / "pygen/pygen_src/riscv_load_store_instr_lib.py",
               UPSTREAM / "pygen/pygen_src/isa/riscv_instr.py",
               UPSTREAM / "pygen/pygen_src/target/rv64imc/riscv_core_setting.py",
               UPSTREAM / "pygen/pygen_src/target/rv64imafdc/riscv_core_setting.py"]
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in sources]
    compatibility = stage_pyflow_compat(tmp_path)
    target = stage_rv64i_target(tmp_path)
    floating_target = stage_rv64imfdc_target(tmp_path)
    assert len(compatibility["module_sha256"]) == 2
    assert target["supported_isa"] == ["RV32I", "RV64I"]
    assert floating_target["removed_isa"] == ["RV32A", "RV64A"]
    for relative, digest in compatibility["module_sha256"].items():
        staged = tmp_path / "pyflow_compat/pygen_src" / relative
        assert hashlib.sha256(staged.read_bytes()).hexdigest() == digest
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in sources] == before


def test_riscvdv_user_target_checks_package_critical_settings(tmp_path):
    source = (UPSTREAM / "pygen/pygen_src/target/rv32i/riscv_core_setting.py").read_text()
    target = stage_user_target(tmp_path, settings=source.encode(), isa="rv32i",
                               target="rv32i", load_store=True)
    staged = tmp_path / "pyflow_user_target/pygen_src/target/rv32i/riscv_core_setting.py"
    assert staged.read_text() == source
    assert target["settings_sha256"] == hashlib.sha256(source.encode()).hexdigest()
    with pytest.raises(ValueError, match="configuration assignments"):
        stage_user_target(tmp_path, settings=(source + "\nprint('unexpected')\n").encode(),
                          isa="rv32i", target="rv32i", load_store=False)
    for old, new, message in (
            ("XLEN = 32", "XLEN = 64", "XLEN differs"),
            ("supported_isa = [riscv_instr_group_t.RV32I]",
             "supported_isa = [riscv_instr_group_t.RV32I, riscv_instr_group_t.RV32A]",
             "supported_isa must match"),
            ("SATP_MODE = satp_mode_t.BARE", "SATP_MODE = satp_mode_t.SV32",
             "bare machine mode"),
            ("VECTOR_EXTENSION_ENABLE = 0", "VECTOR_EXTENSION_ENABLE = 1",
             "VECTOR_EXTENSION_ENABLE=0"),
            ("support_unaligned_load_store = 1", "support_unaligned_load_store = 0",
             "support_unaligned_load_store=1")):
        assert old in source
        with pytest.raises(ValueError, match=message):
            stage_user_target(tmp_path, settings=source.replace(old, new).encode(),
                              isa="rv32i", target="rv32i", load_store=True)


def test_riscvdv_rv64ima_user_target_requires_exact_a_and_one_hart(tmp_path):
    source = (Path(__file__).resolve().parents[1] /
              "examples/riscv-dv/rv64ima-core-target.py").read_text()
    target = stage_user_target(tmp_path, settings=source.encode(), isa="rv64ima",
                               target="rv64ima", load_store=False)
    assert target["supported_isa"] == sorted({"RV32I", "RV32M", "RV32A",
                                               "RV64I", "RV64M", "RV64A"})
    with pytest.raises(ValueError, match="supported_isa must match"):
        stage_user_target(tmp_path, settings=source.replace(
            "riscv_instr_group_t.RV64A]", "riscv_instr_group_t.RV64I]").encode(),
            isa="rv64ima", target="rv64ima", load_store=False)
    with pytest.raises(ValueError, match="NUM_HARTS=1"):
        stage_user_target(tmp_path, settings=source.replace("NUM_HARTS = 1", "NUM_HARTS = 2").encode(),
                          isa="rv64ima", target="rv64ima", load_store=False)


def test_riscvdv_csr_map_and_isolated_generator(tmp_path):
    if importlib.util.find_spec("yaml") is None:
        pytest.skip("optional CSR profile YAML dependency not installed")
    source = Path(__file__).resolve().parents[1] / "examples/riscv-dv/csr-mscratch.yaml"
    for xlen in (32, 64):
        assert validate_mscratch_map(source.read_bytes(), xlen=xlen) == ["mscratch"]
    extended = source.with_name("csr-mscratch-mepc.yaml")
    for xlen in (32, 64):
        assert validate_mscratch_map(extended.read_bytes(), xlen=xlen) == ["mscratch", "mepc"]
    import yaml
    mepc_only = [yaml.safe_load(extended.read_text())[1]]
    with pytest.raises(ValueError, match="requires mscratch"):
        validate_mscratch_map(yaml.safe_dump(mepc_only).encode(), xlen=32)
    with pytest.raises(ValueError, match="machine-mode mscratch and mepc only"):
        validate_mscratch_map(source.read_bytes().replace(b"mscratch", b"mstatus"), xlen=32)
    staged = stage_csr_generator(tmp_path)
    assert staged["kind"] == "pinned_bitstring5_compatibility"
    assert staged["upstream_sha256"] == hashlib.sha256(
        (UPSTREAM / "scripts/gen_csr_test.py").read_bytes()).hexdigest()
    assert (tmp_path / "csr_compat/gen_csr_test.py").is_file()


@pytest.mark.parametrize(("extra", "message"), [
    (["--backend", "verilator"], "only the validated pyflow backend"),
    (["--upstream-option", "+enable_interrupt=1"], "unvalidated upstream options"),
    (["--upstream-option", "+bare_program_mode=0"], "ProcessorCI controls upstream options"),
    (["--memory-size", "0x800"], "4 KiB-aligned base and size"),
    (["--memory-base", "0x80000001"], "4 KiB-aligned base and size"),
    (["--memory-base", "0x100000000"], "within 32-bit addresses"),
    (["--data-base", "0x2001"], "data base must be 4 KiB-aligned"),
    (["--data-base", "0"], "above reset PC"),
    (["--memory-signature-limit", "0"], "memory signature limit must be 1 to 1024"),
    (["--reset-pc", "0x82"], "reset PC must be word-aligned"),
    (["--reset-pc", "0x80000"], "reset PC must be word-aligned and inside"),
    (["--isa", "rv64imfdc", "--profile", "riscv_rand_instr_test",
      "--upstream-option", "+no_directed_instr=0"], "controls directed and load/store"),
    (["--isa", "rv64imfdc", "--profile", "riscv_jump_stress_test",
      "--upstream-option", "+no_branch_jump=0"], "jump profile controls no_branch_jump"),
    (["--isa", "rv64imfdc", "--single-hart-no-csr"],
     "single-hart CSR-free startup is unavailable"),
    (["--isa", "rv32imc_zbb", "--profile", "riscv_rand_instr_test"],
     "RV32IMC_Zbb currently requires the bounded arithmetic profile"),
    (["--single-hart-no-csr", "--upstream-option", "+no_fence=0"],
     "single-hart CSR-free startup requires no_fence=1"),
])
def test_riscvdv_rejects_unsupported_configurations(extra, message, tmp_path, capsys):
    with pytest.raises(SystemExit, match="2"):
        cli_main(["--tool", "riscv-dv", "--output", str(tmp_path), *extra])
    assert message in capsys.readouterr().err


@pytest.mark.parametrize(("unavailable", "message"), [
    ("riscv32-unknown-elf-gcc", "riscv32-unknown-elf-gcc"),
    ("/missing/spike", "/missing/spike"),
])
def test_riscvdv_reports_missing_tools(unavailable, message, tmp_path, capsys, monkeypatch):
    # Keep the preflight independent of the CI runner's installed toolchains.
    monkeypatch.setattr("riscv_test_runner.riscv_dv.shutil.which",
                        lambda name: None if name == unavailable else name)
    with pytest.raises(SystemExit, match="2"):
        cli_main(["--tool", "riscv-dv", "--output", str(tmp_path),
                  "--spike", "/missing/spike"])
    assert f"required tool unavailable: {message}" in capsys.readouterr().err


def test_riscvdv_reports_missing_pyflow_dependency(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr("riscv_test_runner.riscv_dv.shutil.which", lambda name: name)
    monkeypatch.setattr("riscv_test_runner.riscv_dv.importlib.util.find_spec",
                        lambda name: None if name == "vsc" else object())
    with pytest.raises(SystemExit, match="2"):
        cli_main(["--tool", "riscv-dv", "--output", str(tmp_path)])
    assert "PyFlow dependency unavailable: vsc" in capsys.readouterr().err


def test_riscvdv_matrix_runs_named_configurations_and_records_unsupported(tmp_path, monkeypatch):
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps({"configurations": [
        {"name": "arithmetic", "isa": "rv32i", "seed": 1},
        {"name": "unsupported", "isa": "rv128i", "seed": 2},
        {"name": "jump", "isa": "rv64imc", "profile": "riscv_jump_stress_test",
         "seed": 3},
    ]}))
    seen = []

    def fake_generate(args):
        seen.append((args.output.name, args.isa, args.profile, args.seed))
        if args.isa == "rv128i":
            raise ValueError("unsupported ISA: rv128i")
        return {"requested": 1, "generated": 1, "compiled": 1,
                "spike_validated": 1, "package_validated": 1,
                "host_mock_validated": 1, "hardware_validated": 0,
                "failed": 0}

    monkeypatch.setattr("riscv_test_runner.riscv_dv.generate", fake_generate)
    output = tmp_path / "output"
    with pytest.raises(SystemExit, match="1"):
        cli_main(["--tool", "riscv-dv", "--matrix", str(matrix),
                  "--output", str(output)])
    report = json.loads((output / "report.json").read_text())
    assert [row["status"] for row in report["results"]] == ["passed", "unsupported", "passed"]
    assert report["requested"] == 3 and report["package_validated"] == 2
    assert "unsupported ISA: rv128i" in report["results"][1]["error"]
    assert seen == [("arithmetic", "rv32i", "riscv_arithmetic_basic_test", 1),
                    ("unsupported", "rv128i", "riscv_arithmetic_basic_test", 2),
                    ("jump", "rv64imc", "riscv_jump_stress_test", 3)]
    assert (output / "report.junit.xml").is_file()


def test_riscvdv_matrix_rejects_duplicate_or_unsafe_names(tmp_path):
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps({"configurations": [
        {"name": "same"}, {"name": "same"}]}))
    with pytest.raises(SystemExit, match="2"):
        cli_main(["--tool", "riscv-dv", "--matrix", str(matrix),
                  "--output", str(tmp_path / "output")])
    matrix.write_text(json.dumps({"configurations": [{"name": "../escape"}]}))
    with pytest.raises(SystemExit, match="2"):
        cli_main(["--tool", "riscv-dv", "--matrix", str(matrix),
                  "--output", str(tmp_path / "output")])


def test_riscvdv_matrix_records_real_unsupported_isa(tmp_path):
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps({"configurations": [
        {"name": "unknown-isa", "isa": "rv128i", "tests": 1}]}))
    output = tmp_path / "output"
    with pytest.raises(SystemExit, match="1"):
        cli_main(["--tool", "riscv-dv", "--matrix", str(matrix),
                  "--output", str(output)])
    report = json.loads((output / "report.json").read_text())
    assert report["failed"] == 1
    assert report["results"][0]["status"] == "unsupported"
    assert "unsupported ISA: rv128i" in report["results"][0]["error"]


def test_riscvdv_saved_package_digest_detects_corruption(tmp_path, capsys):
    source = UPSTREAM.parents[1] / "examples/riscv-dv/rv32i-arithmetic-seed5000"
    for name in ("manifest.json", "generated.S", "program.elf", "imem.hex", "dmem.hex"):
        shutil.copy2(source / name, tmp_path / name)
    package, digest = verify_saved_package(tmp_path)
    assert package["test_id"] == "riscv_arithmetic_basic_test-rv32i-5000"
    cli_main(["--tool", "riscv-dv", "--verify-package", str(tmp_path),
              "--expected-manifest-sha256", digest])
    assert '"verified": true' in capsys.readouterr().out
    with pytest.raises(SystemExit, match="2"):
        cli_main(["--tool", "riscv-dv", "--verify-package", str(tmp_path),
                  "--expected-manifest-sha256", "0" * 64])
    (tmp_path / "imem.hex").write_bytes((tmp_path / "imem.hex").read_bytes() + b"00")
    with pytest.raises(ValueError, match="imem.hex SHA-256 mismatch"):
        verify_saved_package(tmp_path)


def test_riscvdv_real_pyflow_reproducibility(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    outputs = []
    for name in ("one", "two"):
        output = tmp_path / name
        cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
                  "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
                  "--seed", "42", "--instr-count", "40", "--spike", spike,
                  "--output", str(output)])
        report = json.loads((output / "report.json").read_text())
        assert (report["generated"], report["compiled"], report["spike_validated"],
                report["package_validated"], report["host_mock_validated"],
                report["failed"]) == (1, 1, 1, 1, 1, 0)
        outputs.append(output / "riscv_arithmetic_basic_test-rv32i-42")
        assert report["results"][0]["manifest_sha256"] == hashlib.sha256(
            (outputs[-1] / "manifest.json").read_bytes()).hexdigest()
    assert (outputs[0] / "generated.S").read_bytes() == (outputs[1] / "generated.S").read_bytes()
    manifest = json.loads((outputs[0] / "manifest.json").read_text())
    assert manifest["entry"] == 0
    assert manifest["isa"] == "rv32i_zicsr_zifencei"
    assert manifest["hardware_execution"] == "pending"
    assert (outputs[0] / "imem.hex").is_file()
    assert (outputs[0] / "dmem.hex").is_file()
    image_bytes = {}
    for filename in ("imem.hex", "dmem.hex"):
        for line in (outputs[0] / filename).read_text().splitlines():
            address, *values = line.split()
            assert address.startswith("@")
            base = int(address[1:], 16)
            for offset, value in enumerate(values):
                assert base + offset not in image_bytes
                image_bytes[base + offset] = int(value, 16)
    assert image_bytes == initial_memory(manifest, supported_isa={manifest["isa"]})

    # Deliberately corrupt one expected GPR in the completion checks. The
    # independent Spike run must no longer report successful completion.
    checked = (outputs[0] / "checked.S").read_text()
    done_offset = checked.index("test_done:")
    match = re.search(r"(    li x(\d+), )0x[0-9a-f]+", checked[done_offset:])
    assert match
    start = done_offset + match.start()
    end = done_offset + match.end()
    wrong = int(match.group(0).split("0x", 1)[1], 16) ^ 1
    corrupted = checked[:start] + match.group(1) + f"0x{wrong:x}" + checked[end:]
    bad_source = outputs[0] / "corrupted.S"
    bad_source.write_text(corrupted)
    bad_elf = outputs[0] / "corrupted.elf"
    subprocess.run(["riscv32-unknown-elf-gcc", "-static", "-mcmodel=medany",
                    "-fvisibility=hidden", "-nostdlib", "-nostartfiles",
                    "-Wl,--no-relax", "-Wl,--build-id=none",
                    "-I", str(UPSTREAM / "user_extension"),
                    "-T", str(outputs[0] / "link.ld"),
                    "-march=rv32i_zicsr_zifencei", "-mabi=ilp32",
                    str(bad_source), "-o", str(bad_elf)], check=True)
    with pytest.raises(RuntimeError, match="tohost=1"):
        trace_reference(bad_elf, spike=spike, isa="rv32i", nm="riscv32-unknown-elf-nm",
                        budget=3000, trace=outputs[0] / "corrupted.trace", memory_base=0)

    too_small = tmp_path / "too-small"
    with pytest.raises(SystemExit, match="1"):
        cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
                  "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
                  "--seed", "42", "--instr-count", "40", "--spike", spike,
                  "--memory-size", "0x1000", "--output", str(too_small)])
    failed = json.loads((too_small / "report.json").read_text())
    assert failed["failed"] == 1
    assert "LOAD segment" in failed["results"][0]["error"]


def test_riscvdv_real_nonzero_reset_pc_package(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
              "--seed", "9700", "--instr-count", "60", "--reset-pc", "0x80",
              "--spike", spike, "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1
    package = tmp_path / "riscv_arithmetic_basic_test-rv32i-9700"
    manifest, _ = verify_saved_package(package)
    assert manifest["entry"] == 0x80
    assert manifest["core_requirements"]["reset_pc"] == 0x80
    assert "--reset-pc 0x80" in report["results"][0]["reproduction_command"]


def test_riscvdv_real_nonzero_ram_base_and_offset_entry(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    base, entry = 0x80000000, 0x80000080
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
              "--seed", "10001", "--instr-count", "80",
              "--memory-base", hex(base), "--reset-pc", hex(entry),
              "--spike", spike, "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    directory = tmp_path / "riscv_arithmetic_basic_test-rv32i-10001"
    manifest, _ = verify_saved_package(directory)
    assert manifest["entry"] == entry
    assert manifest["core_requirements"]["memory_base"] == base
    assert manifest["oracle"]["address"] >= base
    assert flat_memory_fit(manifest, base=base, size=0x80000, reset_pc=entry,
                           supported_isa={manifest["isa"]}) == []


def test_riscvdv_real_single_hart_no_csr_package(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
              "--seed", "10110", "--instr-count", "100", "--single-hart-no-csr",
              "--memory-base", "0x80000000", "--reset-pc", "0x80000080",
              "--spike", spike, "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    directory = tmp_path / "riscv_arithmetic_basic_test-rv32i-10110"
    manifest, _ = verify_saved_package(directory)
    assert manifest["isa"] == "rv32i"
    assert manifest["core_requirements"]["zicsr"] is False
    assert manifest["core_requirements"]["mhartid"] is False
    assert "csrr x5, 0xf14" in (directory / "upstream-generated.S").read_text()
    assert "li x5, 0" in (directory / "generated.S").read_text()
    assert "csrr x5, 0xf14" not in (directory / "generated.S").read_text()
    upstream = directory / "upstream-generated.S"
    upstream.write_bytes(upstream.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="upstream-generated.S SHA-256 mismatch"):
        verify_saved_package(directory)


def test_riscvdv_real_user_target_is_saved_and_hashed(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    settings = Path(__file__).resolve().parents[1] / "examples/riscv-dv/rv32i-core-target.py"
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
              "--seed", "10200", "--instr-count", "100",
              "--target-settings", str(settings), "--spike", spike,
              "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    directory = tmp_path / "riscv_arithmetic_basic_test-rv32i-10200"
    package, _ = verify_saved_package(directory)
    assert package["generation"]["pyflow_target"]["kind"] == "user_target"
    assert package["generation"]["input_target_sha256"] == hashlib.sha256(settings.read_bytes()).hexdigest()
    assert "--target-settings" in report["results"][0]["reproduction_command"]
    target_copy = directory / "input-target.py"
    target_copy.write_bytes(target_copy.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="custom target SHA-256 mismatch"):
        verify_saved_package(directory)


def test_riscvdv_real_atomic_commit_memory_oracle(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or
            not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional RISC-V compiler and Spike not installed")
    linker = tmp_path / "link.ld"
    linker.write_text((UPSTREAM / "scripts/link.ld").read_text().replace(
        "0x80000000", "0x0", 1))
    source = Path(__file__).resolve().parents[1] / "examples/riscv-dv/atomic-toolchain-smoke.S"
    elf = tmp_path / "atomic.elf"
    subprocess.run(["riscv32-unknown-elf-gcc", "-static", "-mcmodel=medany",
                    "-nostdlib", "-nostartfiles", "-Wl,--no-relax",
                    "-Wl,--build-id=none", "-T", str(linker),
                    "-march=rv32ima_zicsr_zifencei", "-mabi=ilp32",
                    str(source), "-o", str(elf)], check=True)
    _, written = trace_reference(elf, spike=spike, isa="rv32ima",
                                 nm="riscv32-unknown-elf-nm", budget=3000,
                                 trace=tmp_path / "atomic.trace", memory_base=0,
                                 memory_size=0x80000)
    address = symbol(elf, "riscv32-unknown-elf-nm", "atomic_word")
    assert [written[address + offset] for offset in range(4)] == [6, 0, 0, 0]
    accesses = reference_memory_accesses(tmp_path / "atomic.trace",
                                         entry=symbol(elf, "riscv32-unknown-elf-nm", "_start"),
                                         done=symbol(elf, "riscv32-unknown-elf-nm", "test_done"))
    assert accesses["stores"] == 1


def test_riscvdv_real_csr_mscratch_package_rejects_wrong_expectation(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or
            not shutil.which("riscv32-unknown-elf-gcc") or
            importlib.util.find_spec("bitstring") is None):
        pytest.skip("optional CSR generator dependencies, compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_csr_test", "--seed", "10300", "--tests", "1",
              "--spike", spike, "--output", str(tmp_path)])
    directory = tmp_path / "riscv_csr_test-rv32i-10300"
    manifest, _ = verify_saved_package(directory)
    assert manifest["core_requirements"]["mscratch"] is True
    assert manifest["oracle"]["address"] == 0x2000
    assert manifest["generation"]["backend"] == "directed_csr_python"
    source = (directory / "generated.S").read_text()
    wrong, count = re.subn(r"(\tcsrrw x\d+, 832, x\d+\n\tli x\d+, )0x00000000",
                           r"\g<1>0x00000001", source, count=1)
    assert count == 1
    bad_source = directory / "wrong-csr.S"
    bad_source.write_text(wrong)
    bad_elf = directory / "wrong-csr.elf"
    subprocess.run(["riscv32-unknown-elf-gcc", "-static", "-mcmodel=medany",
                    "-nostdlib", "-nostartfiles", "-Wl,--no-relax",
                    "-Wl,--build-id=none", "-T", str(directory / "link.ld"),
                    "-march=rv32i_zicsr_zifencei", "-mabi=ilp32",
                    str(bad_source), "-o", str(bad_elf)], check=True)
    bad_trace = directory / "wrong-csr.trace"
    with pytest.raises(RuntimeError, match="tohost=1"):
        trace_reference(bad_elf, spike=spike, isa="rv32i",
                        nm="riscv32-unknown-elf-nm", budget=10000,
                        trace=bad_trace, memory_base=0, memory_size=0x80000)
    assert re.search(r"mem 0x00002000 0x00000101", bad_trace.read_text())
    csr_map = directory / "input-csr-map.yaml"
    csr_map.write_bytes(csr_map.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="CSR map SHA-256 mismatch"):
        verify_saved_package(directory)


@pytest.mark.parametrize("isa,seed,prefix", [
    ("rv32i", 10900, "riscv32-unknown-elf-"),
    ("rv64i", 10910, "riscv64-elf-"),
])
def test_riscvdv_real_csr_mepc_package_rejects_wrong_expectation(
        tmp_path: Path, isa: str, seed: int, prefix: str):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or
            not shutil.which(prefix + "gcc") or
            importlib.util.find_spec("bitstring") is None):
        pytest.skip("optional CSR generator dependencies, compiler, and Spike not installed")
    csr_map = Path(__file__).resolve().parents[1] / "examples/riscv-dv/csr-mscratch-mepc.yaml"
    cli_main(["--tool", "riscv-dv", "--isa", isa, "--profile", "riscv_csr_test",
              "--csr-map", str(csr_map), "--seed", str(seed), "--tests", "1",
              "--spike", spike, "--output", str(tmp_path)])
    directory = tmp_path / f"riscv_csr_test-{isa}-{seed}"
    manifest, _ = verify_saved_package(directory)
    assert manifest["generation"]["csrs"] == ["mscratch", "mepc"]
    assert manifest["core_requirements"]["mepc"] is True
    source = (directory / "generated.S").read_text()
    wrong, count = re.subn(r"(\tcsrrw x\d+, 833, x\d+\n\tli x\d+, )0x0+",
                           r"\g<1>0x1", source, count=1)
    assert count == 1
    bad_source = directory / "wrong-mepc.S"
    bad_source.write_text(wrong)
    bad_elf = directory / "wrong-mepc.elf"
    subprocess.run([prefix + "gcc", "-static", "-mcmodel=medany", "-nostdlib",
                    "-nostartfiles", "-Wl,--no-relax", "-Wl,--build-id=none",
                    "-T", str(directory / "link.ld"),
                    f"-march={isa}_zicsr_zifencei",
                    "-mabi=ilp32" if isa == "rv32i" else "-mabi=lp64",
                    str(bad_source), "-o", str(bad_elf)], check=True)
    with pytest.raises(RuntimeError, match="tohost=1"):
        trace_reference(bad_elf, spike=spike, isa=isa, nm=prefix + "nm",
                        budget=10000, trace=directory / "wrong-mepc.trace",
                        memory_base=0, memory_size=0x80000)


def test_riscvdv_real_lrsc_package_and_wrong_gpr(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or
            not shutil.which("riscv64-elf-gcc") or
            importlib.util.find_spec("vsc") is None):
        pytest.skip("optional PyFlow, RV64 compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv64ima",
              "--profile", "riscv_lr_sc_test", "--seed", "10400", "--tests", "1",
              "--spike", spike, "--output", str(tmp_path)])
    directory = tmp_path / "riscv_lr_sc_test-rv64ima-10400"
    manifest, _ = verify_saved_package(directory)
    assert manifest["isa"] == "rv64ima_zicsr_zifencei"
    assert manifest["core_requirements"]["atomic"] is True
    assert manifest["core_requirements"]["single_hart"] is True
    assert manifest["reference_memory_accesses"]["loads"] == 1
    assert manifest["reference_memory_accesses"]["stores"] == 1
    assert manifest["memory_signature_total_written_bytes"] == 8
    assert re.search(r"\blr\.d", (directory / "generated.S").read_text())
    sc_register = re.search(r"x(\d+) holds permitted SC", manifest["signature_policy"])
    assert sc_register and f"x{sc_register.group(1)}" not in manifest["register_signature"]
    assert (directory / "upstream-generated.S").read_bytes() != (directory / "generated.S").read_bytes()
    checked = (directory / "checked.S").read_text()
    wrong, count = re.subn(r"(test_done:\s*\n\s*li x\d+, 0x)([0-9a-f]+)",
                           lambda m: m.group(1) + m.group(2)[:-1] +
                           format(int(m.group(2)[-1], 16) ^ 1, "x"), checked, count=1)
    assert count == 1
    bad_source = directory / "wrong-gpr.S"
    bad_source.write_text(wrong)
    bad_elf = directory / "wrong-gpr.elf"
    subprocess.run(["riscv64-elf-gcc", "-static", "-mcmodel=medany",
                    "-nostdlib", "-nostartfiles", "-Wl,--no-relax",
                    "-Wl,--build-id=none", "-I", str(directory),
                    "-I", str(UPSTREAM / "user_extension"),
                    "-T", str(directory / "link.ld"),
                    "-march=rv64ima_zicsr_zifencei", "-mabi=lp64",
                    str(bad_source), "-o", str(bad_elf)], check=True)
    bad_trace = directory / "wrong-gpr.trace"
    with pytest.raises(RuntimeError):
        trace_reference(bad_elf, spike=spike, isa="rv64ima",
                        nm="riscv64-elf-nm", budget=10000,
                        trace=bad_trace, memory_base=0, memory_size=0x80000)
    assert re.search(r"mem 0x0000000000001000 0x00000003", bad_trace.read_text())
    upstream_source = directory / "upstream-generated.S"
    original_upstream = upstream_source.read_bytes()
    upstream_source.write_bytes(original_upstream + b"\n# changed\n")
    with pytest.raises(ValueError, match="upstream-generated.S SHA-256 mismatch"):
        verify_saved_package(directory)
    upstream_source.write_bytes(original_upstream)
    factory = directory / "lrsc-instruction-factory.py"
    factory.write_bytes(factory.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="lrsc-instruction-factory.py SHA-256 mismatch"):
        verify_saved_package(directory)


def test_riscvdv_amo_stream_relocation_preserves_main_label():
    from riscv_test_runner.riscv_dv import relocate_amo_to_done, relocate_amo_stream_to_done
    source = ("main: la t2, amo_0+48 #start riscv_amo_instr_stream_0\n"
              "  amoadd.d.rl s4, t4, (t2) #end riscv_amo_instr_stream_0\n"
              "  add a0, a0, a1\n"
              "  la x14, test_done\n"
              "  jalr x0, x14, 0\n"
              "test_done:\n")
    adapted, operation = relocate_amo_to_done(source)
    assert operation == "amoadd.d"
    assert "main:\n  add a0, a0, a1" in adapted
    assert adapted.index("amoadd.d.rl") < adapted.index("la x14, test_done")
    assert adapted.index("add a0, a0, a1") < adapted.index("amoadd.d.rl")
    pair = source.replace(
        "  amoadd.d.rl s4, t4, (t2) #end riscv_amo_instr_stream_0\n",
        "  amoand.d.rl s4, t4, (t2)\n"
        "  amomin.w.rl s9, s5, (t2) #end riscv_amo_instr_stream_0\n")
    adapted_pair, operations = relocate_amo_stream_to_done(pair, count=2)
    assert operations == ["amoand.d", "amomin.w"]
    assert "main:\n  add a0, a0, a1" in adapted_pair
    assert adapted_pair.index("amoand.d.rl") < adapted_pair.index("amomin.w.rl")
    assert adapted_pair.index("amomin.w.rl") < adapted_pair.index("la x14, test_done")
    triple = pair.replace(
        "  amomin.w.rl s9, s5, (t2) #end riscv_amo_instr_stream_0\n",
        "  amomin.w.rl s9, s5, (t2)\n"
        "  amoxor.d.rl t3, t0, (t2) #end riscv_amo_instr_stream_0\n")
    adapted_triple, operations = relocate_amo_stream_to_done(triple, count=3)
    assert operations == ["amoand.d", "amomin.w", "amoxor.d"]
    assert adapted_triple.index("amoxor.d.rl") < adapted_triple.index("la x14, test_done")


@pytest.mark.parametrize("profile,seed,stores", [
    ("riscv_amo_test", 10500, 1),
    ("riscv_amo_pair_test", 10600, 2),
    ("riscv_amo_triple_test", 10800, 3),
])
def test_riscvdv_real_amo_package_rejects_wrong_memory(
        tmp_path: Path, profile: str, seed: int, stores: int):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or
            not shutil.which("riscv64-elf-gcc") or
            importlib.util.find_spec("vsc") is None):
        pytest.skip("optional PyFlow, RV64 compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv64ima",
              "--profile", profile, "--seed", str(seed), "--tests", "1",
              "--spike", spike, "--output", str(tmp_path)])
    directory = tmp_path / f"{profile}-rv64ima-{seed}"
    manifest, _ = verify_saved_package(directory)
    assert manifest["core_requirements"]["atomic"] is True
    assert manifest["core_requirements"]["single_hart"] is True
    operations = manifest["atomic_outcome"].get("operations") or [manifest["atomic_outcome"]["operation"]]
    assert len(operations) == stores and all(operation.startswith("amo") for operation in operations)
    assert manifest["reference_memory_accesses"]["stores"] == stores
    assert manifest["memory_signature_total_written_bytes"] == 8
    assert len(manifest["register_signature"]) == 30
    checked = (directory / "checked.S").read_text()
    wrong, count = re.subn(
        r"(# ProcessorCI Spike-derived memory byte checks\n\s*li x\d+, 0x[0-9a-f]+\n"
        r"\s*lbu x\d+, 0\(x\d+\)\n\s*li x\d+, 0x)([0-9a-f]+)",
        lambda m: m.group(1) + m.group(2)[:-1] +
        format(int(m.group(2)[-1], 16) ^ 1, "x"), checked, count=1)
    assert count == 1
    bad_source = directory / "wrong-memory.S"
    bad_source.write_text(wrong)
    bad_elf = directory / "wrong-memory.elf"
    subprocess.run(["riscv64-elf-gcc", "-static", "-mcmodel=medany",
                    "-nostdlib", "-nostartfiles", "-Wl,--no-relax",
                    "-Wl,--build-id=none", "-I", str(directory),
                    "-I", str(UPSTREAM / "user_extension"),
                    "-T", str(directory / "link.ld"),
                    "-march=rv64ima_zicsr_zifencei", "-mabi=lp64",
                    str(bad_source), "-o", str(bad_elf)], check=True)
    trace = directory / "wrong-memory.trace"
    with pytest.raises(RuntimeError):
        trace_reference(bad_elf, spike=spike, isa="rv64ima",
                        nm="riscv64-elf-nm", budget=10000,
                        trace=trace, memory_base=0, memory_size=0x80000)
    assert re.search(r"mem 0x0000000000001000 0x00000003", trace.read_text())
    stem = "amo-pair" if stores == 2 else "amo-triple" if stores == 3 else "amo"
    factory = directory / f"{stem}-instruction-factory.py"
    factory.write_bytes(factory.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match=f"{stem}-instruction-factory.py SHA-256 mismatch"):
        verify_saved_package(directory)


def test_riscvdv_real_vector_store_trace_reads_all_elements(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if not spike or not Path(spike).is_file() or not shutil.which("riscv64-elf-gcc"):
        pytest.skip("optional RVV compiler and Spike not installed")
    linker = UPSTREAM / "scripts/link.ld"
    source = Path(__file__).resolve().parents[1] / "examples/riscv-dv/vector-spike-smoke.S"
    elf = tmp_path / "vector.elf"
    subprocess.run(["riscv64-elf-gcc", "-static", "-mcmodel=medany",
                    "-nostdlib", "-nostartfiles", "-Wl,--no-relax",
                    "-Wl,--build-id=none", "-T", str(linker),
                    "-march=rv64gcv_zicsr_zifencei", "-mabi=lp64d",
                    str(source), "-o", str(elf)], check=True)
    _, written = trace_reference(elf, spike=spike, isa="rv64gcv",
                                 nm="riscv64-elf-nm", budget=3000,
                                 trace=tmp_path / "vector.trace",
                                 memory_base=0x80000000, memory_size=0x80000)
    address = symbol(elf, "riscv64-elf-nm", "vector_output")
    assert bytes(written[address + i] for i in range(16)) == (3).to_bytes(4, "little") * 4


def test_riscvdv_real_disjoint_instruction_and_data_images(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_rand_instr_test", "--tests", "1",
              "--seed", "42", "--instr-count", "100", "--load-store",
              "--memory-base", "0x80000000", "--reset-pc", "0x80000000",
              "--data-base", "0x80020000", "--spike", spike,
              "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    directory = tmp_path / "riscv_rand_instr_test-rv32i-42"
    manifest, _ = verify_saved_package(directory)
    assert manifest["memory_layout"]["mode"] == "split_disjoint"
    assert manifest["core_requirements"]["split_memory"] is True
    assert manifest["memory_signature_total_written_bytes"] > 0
    assert (directory / "imem.hex").read_text().startswith("@0000000080000000")
    assert (directory / "dmem.hex").read_text().startswith("@0000000080020000")
    manifest["memory_layout"]["data_base"] += 0x1000
    (directory / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="invalid split memory layout"):
        verify_saved_package(directory)


def test_riscvdv_real_load_store_rejects_wrong_memory_byte(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_rand_instr_test", "--tests", "1",
              "--seed", "42", "--instr-count", "100", "--load-store",
              "--memory-signature-limit", "4",
              "--spike", spike, "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert (report["generated"], report["compiled"], report["spike_validated"],
            report["package_validated"], report["host_mock_validated"],
            report["failed"]) == (1, 1, 1, 1, 1, 0)
    directory = tmp_path / "riscv_rand_instr_test-rv32i-42"
    manifest = json.loads((directory / "manifest.json").read_text())
    assert manifest["memory_signature_total_written_bytes"] > 0
    assert len(manifest["memory_signature"]) == 4

    checked = (directory / "checked.S").read_text()
    memory_checks = checked.index("# ProcessorCI Spike-derived memory byte checks")
    match = re.search(r"(    li x\d+, )0x([0-9a-f]+)\n    bne x\d+, x\d+, processorci_fail",
                      checked[memory_checks:])
    assert match
    start = memory_checks + match.start(2)
    end = memory_checks + match.end(2)
    bad_source = directory / "wrong-memory.S"
    bad_source.write_text(checked[:start] + f"{int(match.group(2), 16) ^ 1:x}" + checked[end:])
    bad_elf = directory / "wrong-memory.elf"
    subprocess.run(["riscv32-unknown-elf-gcc", "-static", "-mcmodel=medany",
                    "-fvisibility=hidden", "-nostdlib", "-nostartfiles",
                    "-Wl,--no-relax", "-Wl,--build-id=none",
                    "-I", str(UPSTREAM / "user_extension"),
                    "-T", str(directory / "link.ld"),
                    "-march=rv32i_zicsr_zifencei", "-mabi=ilp32",
                    str(bad_source), "-o", str(bad_elf)], check=True)
    with pytest.raises(RuntimeError, match="tohost=1"):
        trace_reference(bad_elf, spike=spike, isa="rv32i", nm="riscv32-unknown-elf-nm",
                        budget=3000, trace=directory / "wrong-memory.trace",
                        misaligned=True, memory_base=0)


def test_riscvdv_long_load_store_stabilizes_raw_and_checked_layout(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_rand_instr_test", "--tests", "1",
              "--seed", "6005", "--instr-count", "1000", "--load-store",
              "--upstream-option", "+no_branch_jump=1", "--spike", spike,
              "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    directory = tmp_path / "riscv_rand_instr_test-rv32i-6005"
    manifest = json.loads((directory / "manifest.json").read_text())
    assert manifest["linker_layout"]["mode"] == "fixed_tohost"
    assert manifest["memory_signature_total_written_bytes"] > 0
    assert len(manifest["memory_signature"]) > 0
    assert symbol(directory / "reference.elf", "riscv32-unknown-elf-nm", "tohost") == \
        symbol(directory / "program.elf", "riscv32-unknown-elf-nm", "tohost")


def test_riscvdv_real_reference_coverage_is_saved_and_labeled(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
              "--seed", "7100", "--instr-count", "100", "--reference-coverage",
              "--spike", spike, "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["package_validated"] == 1 and report["failed"] == 0
    assert report["reference_coverage_validated"] == 1
    directory = tmp_path / "riscv_arithmetic_basic_test-rv32i-7100"
    package, _ = verify_saved_package(directory,
                                      expected_manifest_sha256=report["results"][0]["manifest_sha256"])
    coverage = package["reference_coverage"]
    assert coverage["kind"] == "spike_reference_execution"
    assert coverage["converted_instructions"] > 0
    assert coverage["model_processed_instructions"] > 0
    assert coverage["coverage_groups_reported"] > 0
    assert coverage["dut_coverage"] is False
    saved_report = directory / coverage["report"]
    saved_report.write_bytes(saved_report.read_bytes() + b"corrupt")
    with pytest.raises(ValueError, match="reference coverage report SHA-256 mismatch"):
        verify_saved_package(directory)


@pytest.mark.parametrize("seed", [9500, 9511])
def test_riscvdv_unaligned_hazard_stream(tmp_path: Path, seed: int):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_unaligned_load_store_test", "--tests", "1",
              "--seed", str(seed), "--instr-count", "100",
              "--spike", spike, "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    assert report["pyflow_compatibility"]["kind"] == "isolated_pyflow_load_store_fix"
    assert len(report["pyflow_compatibility"]["module_sha256"]) == 2
    directory = tmp_path / f"riscv_unaligned_load_store_test-rv32i-{seed}"
    package, _ = verify_saved_package(directory)
    assert package["core_requirements"]["misaligned_load_store"] is True
    assert package["generation"]["pyflow_compatibility"]["module_sha256"] == report["pyflow_compatibility"]["module_sha256"]
    assert package["memory_signature_total_written_bytes"] > 0
    assert package["reference_memory_accesses"]["misaligned_wide"] > 0
    generated = (directory / "generated.S").read_text()
    assert "riscv_load_store_hazard_instr_stream" in generated
    assert "la         zero, region_" not in generated


def test_riscvdv_real_floating_signature_rejects_wrong_fpr(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv64-elf-gcc")):
        pytest.skip("optional PyFlow, RV64 compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv64imfdc",
              "--profile", "riscv_rand_instr_test", "--tests", "1",
              "--seed", "9910", "--instr-count", "100",
              "--spike", spike, "--output", str(tmp_path)])
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    directory = tmp_path / "riscv_rand_instr_test-rv64imfdc-9910"
    package = json.loads((directory / "manifest.json").read_text())
    assert len(package["floating_signature"]["registers"]) == 32
    checked = (directory / "checked.S").read_text()
    start = checked.index("# ProcessorCI Spike-derived FPR and fcsr checks")
    match = re.search(r"fmv\.x\.d x\d+, f0\n    li x\d+, 0x([0-9a-f]+)", checked[start:])
    assert match
    begin, end = start + match.start(1), start + match.end(1)
    wrong = directory / "wrong-fpr.S"
    wrong.write_text(checked[:begin] + f"{int(match.group(1), 16) ^ 1:x}" + checked[end:])
    elf = directory / "wrong-fpr.elf"
    subprocess.run(["riscv64-elf-gcc", "-static", "-mcmodel=medany",
                    "-fvisibility=hidden", "-nostdlib", "-nostartfiles",
                    "-Wl,--no-relax", "-Wl,--build-id=none",
                    "-I", str(directory), "-I", str(UPSTREAM / "user_extension"),
                    "-T", str(directory / "link.ld"),
                    "-march=rv64imfdc_zicsr_zifencei", "-mabi=lp64d",
                    str(wrong), "-o", str(elf)], check=True)
    with pytest.raises(RuntimeError, match="tohost=1"):
        trace_reference(elf, spike=spike, isa="rv64imfdc", nm="riscv64-elf-nm",
                        budget=3300, trace=directory / "wrong-fpr.trace")
    startup = directory / "user_init.s"
    startup.write_bytes(startup.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="floating startup SHA-256 mismatch"):
        verify_saved_package(directory)


def test_riscvdv_real_rv64imfdc_jump_executes_jumps_and_float(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv64-elf-gcc")):
        pytest.skip("optional PyFlow, RV64 compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv64imfdc",
              "--profile", "riscv_jump_stress_test", "--tests", "1",
              "--seed", "10702", "--instr-count", "200",
              "--spike", spike, "--output", str(tmp_path)])
    directory = tmp_path / "riscv_jump_stress_test-rv64imfdc-10702"
    package, _ = verify_saved_package(directory)
    assert package["reference_jump_instructions"] > 0
    assert len(package["floating_signature"]["registers"]) == 32
    assert "+no_branch_jump=1" in package["generation"]["options"]
    assert "+enable_floating_point=1" in package["generation"]["options"]
    assert "ProcessorCI Spike-derived FPR and fcsr checks" in (directory / "checked.S").read_text()


def test_riscvdv_real_filtered_zbb_executes_and_saves_target(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or
            not shutil.which("riscv32-unknown-elf-gcc") or
            not shutil.which("riscv32-unknown-elf-readelf") or
            importlib.util.find_spec("vsc") is None):
        pytest.skip("optional PyFlow, RV32 Zbb compiler, and Spike not installed")
    cli_main(["--tool", "riscv-dv", "--isa", "rv32imc_zbb",
              "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
              "--seed", "11002", "--instr-count", "200", "--spike", spike,
              "--output", str(tmp_path)])
    directory = tmp_path / "riscv_arithmetic_basic_test-rv32imc_zbb-11002"
    package, _ = verify_saved_package(directory)
    assert package["reference_zbb_instructions"] > 0
    assert package["core_requirements"]["zbb"] is True
    arch = subprocess.check_output(["riscv32-unknown-elf-readelf", "-A",
                                    str(directory / "program.elf")], text=True)
    assert "_zbb1p0" in arch
    target = directory / "target-settings.py"
    target.write_bytes(target.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="Zbb target-settings.py SHA-256 mismatch"):
        verify_saved_package(directory)


def test_riscvdv_real_custom_testlist_is_saved_and_hashed(tmp_path: Path):
    spike = os.environ.get("PROCESSORCI_SPIKE")
    if (not spike or not Path(spike).is_file() or not UPSTREAM.joinpath("run.py").is_file()
            or importlib.util.find_spec("vsc") is None
            or not shutil.which("riscv32-unknown-elf-gcc")):
        pytest.skip("optional PyFlow, RISC-V compiler, and Spike not installed")
    testlist = tmp_path / "custom.yaml"
    testlist.write_text("- test: riscv_arithmetic_basic_test\n"
                        "  gen_test: riscv_instr_base_test\n"
                        "  gen_opts: +instr_cnt=60 +num_of_sub_program=0 "
                        "+directed_instr_0=riscv_int_numeric_corner_stream,4 "
                        "+no_fence=1 +no_data_page=1 +no_branch_jump=1\n")
    output = tmp_path / "output"
    cli_main(["--tool", "riscv-dv", "--isa", "rv32i",
              "--profile", "riscv_arithmetic_basic_test", "--tests", "1",
              "--seed", "9950", "--instr-count", "60", "--testlist", str(testlist),
              "--spike", spike, "--output", str(output)])
    report = json.loads((output / "report.json").read_text())
    assert report["host_mock_validated"] == 1 and report["failed"] == 0
    directory = output / "riscv_arithmetic_basic_test-rv32i-9950"
    saved = directory / "input-testlist.yaml"
    manifest, _ = verify_saved_package(directory)
    assert saved.read_bytes() == testlist.read_bytes()
    assert manifest["generation"]["input_testlist_sha256"] == hashlib.sha256(saved.read_bytes()).hexdigest()
    assert str(saved) in report["results"][0]["reproduction_command"]
    saved.write_bytes(saved.read_bytes() + b"# changed\n")
    with pytest.raises(ValueError, match="custom test list SHA-256 mismatch"):
        verify_saved_package(directory)
