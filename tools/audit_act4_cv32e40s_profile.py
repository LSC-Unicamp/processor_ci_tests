"""Check the staged ACT profile against RV-Bench's pinned CV32E40S RTL path."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from build_act4 import REVISION
from build_act4_cv32e40s import (ACT_MEMORY_BYTES, ACT_PROGRAM_BYTES,
                                 CORE_REVISION, ROOT, RV_BENCH)

WRAPPER = RV_BENCH / "overlay/cv32e40s/wrappers/cv32e40s.sv"
CONTROLLER = RV_BENCH / "tools/controller/rtl/controller.sv"
MEMORY = RV_BENCH / "tools/controller/rtl/memory.sv"
CORE = RV_BENCH / "cores/cv32e40s/rtl/cv32e40s_core.sv"
RTL = CORE.parent
PKG = RTL / "include/cv32e40s_pkg.sv"
CSR = RTL / "cv32e40s_cs_registers.sv"
PMP = RTL / "cv32e40s_pmp.sv"
PMA = RTL / "cv32e40s_pma.sv"
LSU = RTL / "cv32e40s_load_store_unit.sv"
DECODER = RTL / "cv32e40s_compressed_decoder.sv"
SEQUENCER = RTL / "cv32e40s_sequencer.sv"
FSM = RTL / "cv32e40s_controller_fsm.sv"
PROBE = ROOT / "tools/probe_rvbench_cv32e40s.py"
PROBE_REPORT = ROOT / "reports/act4-cv32e40s-rvbench-probe.json"
SERIAL_RUNNER = ROOT / "tools/run_act4_cv32e40s_serial.py"
CAPABILITY_RTL = {"core": CORE, "package": PKG, "csr": CSR, "pmp": PMP,
                  "pma": PMA, "lsu": LSU, "decoder": DECODER,
                  "sequencer": SEQUENCER, "fsm": FSM}


def _require(source: str, pattern: str, label: str) -> None:
    if re.search(pattern, source, re.M) is None:
        raise RuntimeError(f"pinned source no longer proves {label}; review the ACT DUT profile")


def _json_with_line_comments(path: Path) -> dict:
    content = re.sub(r"(?m)^\s*//[^\n]*$", "", path.read_text())
    return json.loads(content)


def audit(config_dir: Path, report_path: Path) -> dict:
    wrapper = WRAPPER.read_text()
    controller = CONTROLLER.read_text()
    memory = MEMORY.read_text()
    core = CORE.read_text()
    pkg = PKG.read_text()
    csr = CSR.read_text()
    pmp = PMP.read_text()
    pma = PMA.read_text()
    lsu = LSU.read_text()
    decoder = DECODER.read_text()
    sequencer = SEQUENCER.read_text()
    fsm = FSM.read_text()
    linker = (config_dir / "link.ld").read_text()
    udb = (config_dir / "cv32e40s-rv32imc.yaml").read_text()
    sail = _json_with_line_comments(config_dir / "sail.json")
    test_config = (config_dir / "test_config.yaml").read_text()

    actual_core = subprocess.check_output(["git", "-C", str(CORE.parents[1]),
                                           "rev-parse", "HEAD"], text=True).strip()
    if actual_core != CORE_REVISION:
        raise RuntimeError("CV32E40S RTL revision differs from the pinned ACT target")
    actual_act = subprocess.check_output(["git", "-C", str(ROOT / "third_party_repositories/riscv-arch-test"),
                                          "rev-parse", "HEAD"], text=True).strip()
    if actual_act != REVISION:
        raise RuntimeError("ACT 4.1 revision differs from the pinned target")

    for label, source, pattern in (
        ("RV32I default", core, r"\bRV32\s*=\s*RV32I\b"),
        ("M extension default", core, r"\bM_EXT\s*=\s*M\b"),
        ("B extension disabled", core, r"\bB_EXT\s*=\s*B_NONE\b"),
        ("PMA regions absent", core, r"\bPMA_NUM_REGIONS\s*=\s*0\b"),
        ("PMP regions absent", core, r"\bPMP_NUM_REGIONS\s*=\s*0\b"),
        ("compressed decode enabled", core, r"\bZC_EXT\s*=\s*1\b"),
        ("reset address zero", wrapper, r"\.boot_addr_i\s*\(0\)"),
        ("shared controller memory", wrapper, r"\.SHARED_MEMORY\s*\(1\)"),
        ("512 KiB controller capacity", wrapper, r"`define CV32E40S_ACT_MEMORY_BYTES 524288"),
        ("instruction byte enables", wrapper, r"\.core_sel_i\s*\(core_sel\)"),
        ("data byte enables", wrapper, r"\.data_mem_sel_i\s*\(data_mem_sel\)"),
        ("ACT printer write port", controller, r"data_mem_addr_i\s*==\s*32'h10000000"),
        ("ACT diagnostic window", controller, r"ACT_DIAGNOSTIC_BASE\s*=\s*32'h0007f000"),
        ("reserved hardware RAM window", controller, r"ACCESSIBLE_BYTES\(MEMORY_SIZE - 4096\)"),
        ("address bounds check", memory, r"a_addr_i\s*<\s*ACCESSIBLE_BYTES"),
        ("program origin", linker, r"RAM_ORIGIN\s*=\s*0x00000000;"),
        ("reset-zero linker entry", linker, r"TEST_BASE\s*=\s*0x00000000;"),
        ("UDB I implementation", udb, r"\bname:\s*I,\s*version:"),
        ("UDB M implementation", udb, r"\bname:\s*M,\s*version:"),
        ("UDB zero PMP entries", udb, r"\bNUM_PMP_ENTRIES:\s*0\b"),
        ("ACT config UDB path", test_config, r"^udb_config: .+cv32e40s-rv32imc\.yaml$"),
        ("host ACT ISA selection limited to I/M", SERIAL_RUNNER.read_text(),
         r'^ISA\s*=\s*\{"rv32i",\s*"rv32im"\}$'),
        ("secure core and U mode implemented", pkg, r"\bSECURE\s*=\s*1;[\s\S]*?\bUSER\s*=\s*SECURE;"),
        ("zero PMP denies unmatched U-mode access", pmp, r"access_fault\s*=\s*\(priv_lvl_i\s*!=\s*PRIV_LVL_M\)\s*\?\s*1'b1"),
        ("PMA default is non-cacheable", pkg, r"NO_PMA_R_DEFAULT\s*=\s*'\{[\s\S]*?main\s*:\s*1'b1,[\s\S]*?cacheable\s*:\s*1'b0"),
        ("PMA uses zero-region default", pma, r"if\s*\(PMA_NUM_REGIONS\s*==\s*0\)[\s\S]*?pma_cfg\s*=\s*NO_PMA_R_DEFAULT"),
        ("misaligned word access is split", lsu, r"2'b10:\s*// word[\s\S]*?trans\.addr\[1:0\]\s*!=\s*2'b00[\s\S]*?lsu_split_0_o\s*=\s*1'b1"),
        ("mtvec reserved modes preserve previous value", pkg, r"mtvec_mode_clint_resolve[\s\S]*?next_value\s*!=\s*2'b00[\s\S]*?next_value\s*!=\s*2'b01[\s\S]*?\?\s*current_value"),
        ("CSR basic mtvec mask", pkg, r"CSR_BASIC_MTVEC_MASK\s*=\s*32'hFFFFFF81"),
        ("CSR mepc mask", pkg, r"CSR_MEPC_MASK\s*=\s*32'hFFFFFFFE"),
        ("CSR M-mode reset", pkg, r"MSTATUS_RESET_VAL\s*=\s*'\{[\s\S]*?mpp\s*:\s*PRIV_LVL_M"),
        ("MRET restores privilege", csr, r"csr_restore_mret:[\s\S]*?priv_lvl_n\s*=\s*privlvl_t'\(mstatus_rdata\.mpp\)"),
        ("Zc decode is enabled", core, r"localparam bit ZC_EXT\s*=\s*1"),
        ("Zcb decoding depends on B parameter", decoder, r"if\s*\(B_EXT\s*!=\s*B_NONE\)\s*begin[\s\S]*?c\.sext\.b"),
        ("Zcmp sequencing exists", sequencer, r"// cm\.push[\s\S]*?seq_instr\s*=\s*PUSH"),
        ("Zcmt sequencing exists", sequencer, r"seq_instr\s*=\s*TBLJMP"),
        ("WFI can enter sleep", fsm, r"wfi_in_wb\s*\|\|\s*wfe_in_wb[\s\S]*?WFI/WFE will stay in WB until we exit sleep mode"),
        ("wrapper has no interrupt stimulus", wrapper, r"\.irq_i\s*\(0\)"),
        ("wrapper has no WFE wakeup stimulus", wrapper, r"\.wu_wfe_i\s*\(0\)"),
    ):
        _require(source, pattern, label)
    _require(linker, rf"RAM_LENGTH\s*=\s*{ACT_PROGRAM_BYTES:#x};", "508 KiB program RAM")

    regions = {(int(row["base"]["value"], 0), int(row["size"]["value"], 0)):
               row["attributes"] for row in sail["memory"]["regions"]}
    expected_regions = {(0, ACT_PROGRAM_BYTES), (0x02000000, 0x00200000),
                        (0x10000000, 0x1000)}
    if set(regions) != expected_regions:
        raise RuntimeError(f"Sail regions disagree with audited ACT/reference map: {sorted(regions)}")
    if not regions[(0, ACT_PROGRAM_BYTES)]["executable"] or regions[(0x10000000, 0x1000)]["readable"]:
        raise RuntimeError("Sail RAM or ACT printer permissions disagree with DUT")
    if not all(sail["platform"][name]["supported"] for name in
               ("clint", "simple_interrupt_generator")):
        raise RuntimeError("ACT Sail signature generation requires reference-only interrupt devices")
    if sail["platform"]["clock_frequency"] != 100000000:
        raise RuntimeError("Sail clock frequency differs from the selected board profile")
    if any(sail["extensions"][name]["supported"] for name in ("Zicntr", "Zihpm")):
        raise RuntimeError("Sail counter extensions exceed the conservative UDB profile")
    if regions[(0, ACT_PROGRAM_BYTES)]["cacheable"]:
        raise RuntimeError("Sail RAM is cacheable but the pinned core's default PMA is not")
    if sail["platform"]["wfi_is_nop"]:
        raise RuntimeError("Sail WFI-as-NOP differs from the pinned core's sleep behavior")
    if not sail["extensions"]["U"]["supported"] or sail["memory"]["pmp"]["count"] != 0:
        raise RuntimeError("Sail privilege/PMP profile differs from pinned core defaults")
    if not re.search(r"MTVEC_ILLEGAL_WRITE_BEHAVIOR:\s*custom", udb):
        raise RuntimeError("UDB mtvec WARL behavior differs from pinned RTL")
    if not re.search(r"JVT_BASE_MASK:\s*0x7FFFFFC0", udb):
        raise RuntimeError("UDB JVT schema-limited mask changed; review against RTL")

    probe = json.loads(PROBE_REPORT.read_text())
    expected_checks = {"machine_isa_and_ids", "mtvec_reserved_mode_preserves_previous", "machine_ecall_trap_return",
                       "rv32m_mul_div", "compressed_c_addi", "misaligned_word_store_load",
                       "u_mode_fetch_fault_with_zero_pmp"}
    if (probe.get("source_revision") != CORE_REVISION or
            probe.get("wrapper_sha256") != hashlib.sha256(WRAPPER.read_bytes()).hexdigest() or
            probe.get("probe_sha256") != hashlib.sha256(PROBE.read_bytes()).hexdigest() or
            probe.get("result", {}).get("status") != "pass" or
            probe.get("initial_mstatus_observed") != 0 or
            set(probe.get("checks", [])) != expected_checks):
        raise RuntimeError("directed CV32E40S capability probe is missing or stale")

    build_summary = json.loads((ROOT / "build/act4-cv32e40s/summary.json").read_text())
    counts = build_summary.get("extension_counts", {})
    if (build_summary.get("act_revision") != REVISION or
            build_summary.get("core_revision") != CORE_REVISION or
            counts != {"I": 39, "M": 8} or build_summary.get("elfs") != 47):
        raise RuntimeError("ACT I/M build coverage differs from the audited target")
    c_sources = list((ROOT / "third_party_repositories/riscv-arch-test/tests").glob("**/C/*.S"))
    if c_sources:
        raise RuntimeError("ACT C test sources are now available; update coverage scope")

    report = {
        "act_revision": actual_act, "core_revision": actual_core,
        "core": "RV-Bench CV32E40S", "test_scope": ["I", "M"],
        "memory": {"controller_bytes": ACT_MEMORY_BYTES,
                   "executable_program_bytes": ACT_PROGRAM_BYTES,
                   "diagnostic_base": ACT_PROGRAM_BYTES,
                   "diagnostic_window_bytes": ACT_MEMORY_BYTES - ACT_PROGRAM_BYTES,
                   "virtual_printer_address": 0x10000000},
        "sail_reference_only": {"clint": [0x02000000, 0x020c0000],
                                "simple_interrupt_generator": 0x020c0000,
                                "io_region": [0x02000000, 0x02200000],
                                "printer_page_granularity_bytes": 4096},
        "source_sha256": {**{name: hashlib.sha256(path.read_bytes()).hexdigest()
                             for name, path in CAPABILITY_RTL.items()},
                          "serial_runner": hashlib.sha256(SERIAL_RUNNER.read_bytes()).hexdigest(),
                          "probe": hashlib.sha256(PROBE.read_bytes()).hexdigest(),
                          "wrapper": hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
                          "controller": hashlib.sha256(CONTROLLER.read_bytes()).hexdigest(),
                          "memory": hashlib.sha256(MEMORY.read_bytes()).hexdigest(),
                          "sail": hashlib.sha256((config_dir / "sail.json").read_bytes()).hexdigest(),
                          "udb": hashlib.sha256((config_dir / "cv32e40s-rv32imc.yaml").read_bytes()).hexdigest()},
        "act_coverage": {"generated_by_extension": {"I": 39, "M": 8, "C": 0},
                         "dut_validated_extensions": ["I", "M"],
                         "host_accepted_isa": ["rv32i", "rv32im"],
                         "c_upstream_sources": 0,
                         "c_status": "unavailable in pinned ACT 4.1 source tree"},
        "directed_probe": {"status": "pass", "checks": sorted(expected_checks),
                           "initial_mstatus_observed": probe["initial_mstatus_observed"],
                           "source_sha256": probe["probe_sha256"]},
        "profile_findings": {
            "csr": "mtvec reserved-mode retention, MISA/IDs, M-mode traps and MRET sampled in RTL; initial mstatus read was 0 although RTL reset constant has MPP=M (0x1800); cause unresolved; full CSR WARL matrix untested",
            "u_mode": "implemented in core, but zero PMP regions deny U-mode instruction fetch in this wrapper; excluded from ACT execution scope",
            "misalignment": "split word store/load passed the pinned wrapper probe; source and Sail permit misaligned main RAM",
            "compressed": "C decode is enabled and c.addi passed; Zcb instructions depend on B_EXT, while broader Zc behavior and JVT remain untested",
            "interrupt_wfi": "CLIC=0 and wrapper interrupt/wakeup inputs are tied low; Sail CLINT is reference-only; WFI sleep cannot complete through this wrapper",
            "zkt": "upstream core manual advertises Zkt; data-independent timing has not been measured",
        },
        "known_profile_limitations": [
            "Sail reference-only CLINT and interrupt generator have no DUT counterpart",
            "PMA_NUM_REGIONS=0 marks the whole core address space as main; the controller only decodes the exact ACT printer write port",
            "upstream UDB JVT_BASE_MASK=0x7fffffc0 omits RTL bit 31 because of a UDB schema constraint",
            "initial mstatus read in the RV-Bench wrapper probe was 0; pinned RTL MSTATUS_RESET_VAL specifies MPP=M (0x1800)",
        ],
        "remaining_profile_review": ["resolve mstatus reset/read discrepancy and full CSR WARL matrix", "Zc subextension and JVT behavior",
                                     "external interrupt/WFI execution after wrapper support",
                                     "Zkt data-independent timing"],
        "fpga_execution": False,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path,
                        default=ROOT / "build/act4-cv32e40s/dut_config")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/act4-cv32e40s-profile-audit.json")
    args = parser.parse_args()
    result = audit(args.config_dir.resolve(), args.output.resolve())
    print(f"ACT {result['act_revision'][:8]} CV32E40S profile: "
          f"{result['memory']['executable_program_bytes']} program bytes; "
          f"{len(result['remaining_profile_review'])} detailed review areas remain")
