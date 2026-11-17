"""Generate reproducible riscv-dv PyFlow programs and ProcessorCI packages."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from riscv_test_runner.core.package import flat_memory_fit, initial_memory, outcome
from riscv_test_runner.core.serial_package import run_package

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "third_party_repositories" / "riscv-dv"
PIN = "f557b89ed6881a20515481a2585e9d004cd9642b"
PYFLOW_COMPAT = {
    "riscv_load_store_instr_lib.py": [(
        "    # TODO Getting pyvsc error -- > rs1 has not been build yet\n"
        "    '''@vsc.constraint\n"
        "    def rs1_c(self):\n"
        "        self.rs1_reg.not_inside(vsc.rangelist(cfg.reserved_regs,\n"
        "                                              self.reserved_rd, riscv_reg_t.ZERO))'''",
        "    @vsc.constraint\n"
        "    def rs1_not_zero_c(self):\n"
        "        self.rs1_reg != riscv_reg_t.ZERO",
    ), (
        "            if not cfg.enable_unaligned_load_store:\n",
        "            if cfg.enable_unaligned_load_store:\n"
        "                allowed_instr.extend([riscv_instr_name_t.LH, riscv_instr_name_t.LHU,\n"
        "                                      riscv_instr_name_t.SH, riscv_instr_name_t.LW,\n"
        "                                      riscv_instr_name_t.SW])\n"
        "                if rcs.XLEN >= 64:\n"
        "                    allowed_instr.extend([riscv_instr_name_t.LWU, riscv_instr_name_t.LD,\n"
        "                                          riscv_instr_name_t.SD])\n"
        "            if not cfg.enable_unaligned_load_store:\n",
    )],
    "isa/riscv_instr.py": [(
        "        instr_h = copy.copy(cls.instr_template[name])\n"
        "        return instr_h\n\n    @classmethod\n    def get_instr",
        "        instr_h = copy.deepcopy(cls.instr_template[name])\n"
        "        return instr_h\n\n    @classmethod\n    def get_instr",
    )],
}
ISAS = {"rv32i": ("rv32i", "ilp32", "riscv32-unknown-elf-"),
        "rv32im": ("rv32imc", "ilp32", "riscv32-unknown-elf-"),
        "rv32imc": ("rv32imc", "ilp32", "riscv32-unknown-elf-"),
        "rv32imc_zbb": ("rv32imcb", "ilp32", "riscv32-unknown-elf-"),
        "rv64i": ("rv64i", "lp64", "riscv64-elf-"),
        "rv64ima": ("rv64ima", "lp64", "riscv64-elf-"),
        "rv64imfdc": ("rv64imfdc", "lp64d", "riscv64-elf-"),
        "rv64im": ("rv64imc", "lp64", "riscv64-elf-"),
        "rv64imc": ("rv64imc", "lp64", "riscv64-elf-")}
PROFILES = ("riscv_arithmetic_basic_test", "riscv_rand_instr_test",
            "riscv_jump_stress_test", "riscv_unaligned_load_store_test",
            "riscv_csr_test", "riscv_lr_sc_test", "riscv_amo_test",
            "riscv_amo_pair_test", "riscv_amo_triple_test")
MATRIX_FIELDS = {"isa", "profile", "tests", "seed", "instr_count", "load_store",
                 "backend", "target", "toolchain_prefix", "spike", "memory_base",
                 "memory_size", "reset_pc", "data_base", "max_cycles", "generator_timeout",
                 "upstream_option", "stop_on_error", "reference_coverage",
                 "experimental_profile", "testlist", "memory_signature_limit",
                 "single_hart_no_csr", "target_settings", "csr_map"}
EXPECTED_TARGET_GROUPS = {
    "rv32i": {"RV32I"},
    "rv32im": {"RV32I", "RV32M"},
    "rv32imc": {"RV32I", "RV32M", "RV32C"},
    "rv32imc_zbb": {"RV32I", "RV32M", "RV32C", "RV32B"},
    "rv64i": {"RV32I", "RV64I"},
    "rv64ima": {"RV32I", "RV32M", "RV32A", "RV64I", "RV64M", "RV64A"},
    "rv64im": {"RV32I", "RV32M", "RV64I", "RV64M"},
    "rv64imc": {"RV32I", "RV32M", "RV32C", "RV64I", "RV64M", "RV64C"},
    "rv64imfdc": {"RV32I", "RV32M", "RV32C", "RV32F", "RV32D",
                  "RV64I", "RV64M", "RV64C", "RV64F", "RV64D"},
}
MATRIX_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
COMMIT = re.compile(r"^core\s+0:\s+3\s+0x([0-9a-f]+)\s+\(0x[0-9a-f]+\)(?:\s+x(\d+)\s+0x([0-9a-f]+))?", re.I)
GPR_COMMIT = re.compile(r"\bx(\d{1,2})\s+0x([0-9a-f]+)", re.I)
FETCH = re.compile(r"^core\s+0:\s+0x([0-9a-f]+)\s+\(0x[0-9a-f]+\)\s+([a-z0-9_.]+)", re.I)
EXCEPTION = re.compile(r"^core\s+0:\s+exception\s+([a-z0-9_]+),\s+epc\s+0x([0-9a-f]+)", re.I)
STORE = re.compile(r"\bmem\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)", re.I)
MEMORY_ACCESS = re.compile(r"\bmem\s+0x[0-9a-f]+", re.I)
MEMORY_ADDRESS = re.compile(r"\bmem\s+0x([0-9a-f]+)", re.I)
STORE_WIDTHS = {"sb": 1, "sh": 2, "sw": 4, "sd": 8,
                "c.sw": 4, "c.swsp": 4, "c.sd": 8, "c.sdsp": 8}
LOAD_NAMES = {"lb", "lbu", "lh", "lhu", "lw", "lwu", "ld",
              "c.lw", "c.lwsp", "c.ld", "c.ldsp"}
LOAD_WIDTHS = {"lb": 1, "lbu": 1, "lh": 2, "lhu": 2, "lw": 4,
               "lwu": 4, "ld": 8, "c.lw": 4, "c.lwsp": 4,
               "c.ld": 8, "c.ldsp": 8}
JUMP_NAMES = {"jal", "jalr", "j", "jr", "c.j", "c.jal", "c.jalr", "c.jr"}
ZBB_NAMES = {"andn", "orn", "xnor", "min", "max", "minu", "maxu",
             "rol", "ror", "rori", "clz", "ctz"}
ZBB_ENUMS = {name.upper() for name in ZBB_NAMES}
ATOMIC_WIDTH = re.compile(r"\.(w|d)(?:\.|$)")
VECTOR_STORE_WIDTH = re.compile(r"^vse(8|16|32|64)\.v$")
VECTOR_LOAD = re.compile(r"^vle(?:8|16|32|64)\.v$")
MEMORY_SIGNATURE_LIMIT = 64
OPTION = re.compile(r"\+[a-z][a-z0-9_]*=[a-zA-Z0-9_,.:-]+\Z")
CONTROLLED_OPTIONS = {"instr_cnt", "bare_program_mode", "no_csr_instr", "no_ebreak",
                      "no_wfi", "disable_compressed_instr", "num_of_harts",
                      "num_of_sub_program", "enable_unaligned_load_store",
                      "require_signature_addr", "signature_addr"}
SAFE_OPTIONS = {"no_branch_jump", "no_fence", "no_load_store", "no_data_page",
                "no_directed_instr", "fix_sp", "hint_instr_ratio"}
CUSTOM_STREAMS = {
    "riscv_arithmetic_basic_test": {"riscv_int_numeric_corner_stream"},
    "riscv_rand_instr_test": {"riscv_jal_instr", "riscv_load_store_rand_instr_stream"},
    "riscv_jump_stress_test": {"riscv_jal_instr"},
    "riscv_unaligned_load_store_test": {"riscv_load_store_rand_instr_stream",
                                        "riscv_load_store_hazard_instr_stream"},
}
CUSTOM_FIXED_OPTIONS = {"bare_program_mode": "1", "no_csr_instr": "1",
                        "no_ebreak": "1", "no_wfi": "1", "num_of_sub_program": "0",
                        "boot_mode": "m"}


class ReferenceTrap(RuntimeError):
    """A Spike trap before the generated program's completion point."""

    def __init__(self, cause: str, epc: int):
        self.cause = cause
        self.epc = epc
        super().__init__(f"Spike reference trap {cause} at PC {epc:#x}")


def custom_profile(testlist: Path, profile_name: str, *, load_store: bool,
                   floating: bool) -> tuple[dict, str]:
    """Select one vetted PyFlow profile from a user test list."""
    import yaml

    raw = testlist.read_bytes()
    try:
        entries = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid custom test-list YAML: {exc}") from exc
    if not isinstance(entries, list):
        raise ValueError("custom test list must be a YAML list")
    selected = [entry for entry in entries if isinstance(entry, dict)
                and entry.get("test") == profile_name]
    if len(selected) != 1:
        raise ValueError(f"custom test list needs exactly one {profile_name} entry")
    entry = selected[0]
    if (set(entry) - {"test", "gen_test", "gen_opts", "iterations", "description"}
            or entry.get("gen_test") != "riscv_instr_base_test"
            or not isinstance(entry.get("gen_opts"), str)):
        raise ValueError("custom test list entry needs the base PyFlow generator and safe fields")
    tokens = entry["gen_opts"].split()
    if not tokens:
        raise ValueError("custom test list has no generation options")
    streams = []
    seen = set()
    for token in tokens:
        if not OPTION.fullmatch(token):
            raise ValueError(f"unsafe custom test-list option: {token}")
        name, value = token[1:].split("=", 1)
        if name in seen:
            raise ValueError(f"duplicate custom test-list option: {name}")
        seen.add(name)
        if name == "instr_cnt":
            if not value.isdecimal() or int(value) < 1:
                raise ValueError("custom instr_cnt must be positive")
        elif name in CUSTOM_FIXED_OPTIONS:
            if value != CUSTOM_FIXED_OPTIONS[name]:
                raise ValueError(f"custom test list cannot change {name}")
        elif name == "enable_unaligned_load_store":
            if profile_name != "riscv_unaligned_load_store_test" or value != "1":
                raise ValueError("unaligned generation belongs to the unaligned profile")
        elif name == "disable_compressed_instr":
            if value != "1":
                raise ValueError("custom test list cannot force compressed generation")
        elif name in SAFE_OPTIONS:
            if floating and name in {"no_directed_instr", "no_load_store"}:
                raise ValueError("RV64IMFDC controls directed and load/store streams")
            if (profile_name in {"riscv_jump_stress_test", "riscv_unaligned_load_store_test"}
                    and name == "no_directed_instr" and value == "1"):
                raise ValueError("selected profile requires its directed stream")
            if (profile_name == "riscv_unaligned_load_store_test"
                    and name == "no_load_store" and value == "1"):
                raise ValueError("unaligned profile requires load/store generation")
            if name == "no_load_store" and value != "1" and not load_store:
                raise ValueError("custom load/store generation requires --load-store")
        elif re.fullmatch(r"directed_instr_\d+", name):
            match = re.fullmatch(r"([A-Za-z0-9_]+),(\d+)", value)
            if not match or not 1 <= int(match.group(2)) <= 1000:
                raise ValueError(f"invalid custom directed stream: {token}")
            stream = match.group(1)
            if floating or stream not in CUSTOM_STREAMS[profile_name]:
                raise ValueError(f"unvalidated custom directed stream: {stream}")
            if stream.startswith("riscv_load_store") and not (
                    load_store or profile_name == "riscv_unaligned_load_store_test"):
                raise ValueError("custom load/store stream requires --load-store")
            streams.append(stream)
        else:
            raise ValueError(f"unvalidated custom test-list option: {name}")
    if profile_name == "riscv_jump_stress_test" and "riscv_jal_instr" not in streams:
        raise ValueError("custom jump profile requires riscv_jal_instr")
    if (profile_name == "riscv_unaligned_load_store_test" and
            "riscv_load_store_hazard_instr_stream" not in streams):
        raise ValueError("custom unaligned profile requires its hazard stream")
    return entry, hashlib.sha256(raw).hexdigest()


def command(args: list[str], *, cwd: Path | None = None, timeout: int = 180,
            env: dict[str, str] | None = None, log: Path | None = None) -> None:
    def run(stream=None):
        process = subprocess.Popen(args, cwd=cwd, env=env,
                                   stdout=stream or subprocess.PIPE,
                                   stderr=subprocess.STDOUT if stream else subprocess.PIPE,
                                   text=stream is None, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # run.py launches PyFlow children; kill the entire process group.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise
        return process.returncode, stdout or "", stderr or ""

    if log is None:
        code, stdout, stderr = run()
        if code:
            raise RuntimeError(f"{' '.join(args)} failed ({code}):\n{stdout[-3000:]}\n{stderr[-3000:]}")
    else:
        with log.open("w", encoding="utf-8") as stream:
            code, _, _ = run(stream)
        if code:
            raise RuntimeError(f"{' '.join(args)} failed ({code}); see {log}")


def symbol(elf: Path, nm: str, name: str) -> int:
    output = subprocess.check_output([nm, str(elf)], text=True)
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[2] == name:
            return int(fields[0], 16)
    raise ValueError(f"ELF lacks {name}")


def stage_pyflow_compat(output: Path) -> dict:
    """Stage pinned PyFlow load/store fixes without changing the submodule."""
    overlay = output / "pyflow_compat"
    hashes = {}
    for relative, changes in PYFLOW_COMPAT.items():
        source = UPSTREAM / "pygen/pygen_src" / relative
        text = source.read_text()
        for original, replacement in changes:
            if text.count(original) != 1:
                raise ValueError(f"pinned PyFlow compatibility marker changed: {relative}")
            text = text.replace(original, replacement, 1)
        staged = overlay / "pygen_src" / relative
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(text)
        hashes[relative] = hashlib.sha256(staged.read_bytes()).hexdigest()
    return {"kind": "isolated_pyflow_load_store_fix", "path": str(overlay),
            "module_sha256": hashes,
            "changes": ["exclude x0 as load/store base", "deep-copy load/store instruction templates",
                        "enable non-byte loads and stores in unaligned mode"]}


def stage_rv64i_target(output: Path) -> dict:
    """Stage a base-I-only PyFlow target from the pinned RV64IMC settings."""
    source = UPSTREAM / "pygen/pygen_src/target/rv64imc/riscv_core_setting.py"
    original = ("supported_isa = [riscv_instr_group_t.RV32I, riscv_instr_group_t.RV32M,\n"
                "                 riscv_instr_group_t.RV32C, riscv_instr_group_t.RV64I,\n"
                "                 riscv_instr_group_t.RV64M, riscv_instr_group_t.RV64C]")
    replacement = "supported_isa = [riscv_instr_group_t.RV32I, riscv_instr_group_t.RV64I]"
    text = source.read_text()
    if text.count(original) != 1:
        raise ValueError("pinned RV64IMC target setting changed; review RV64I derivation")
    overlay = output / "pyflow_rv64i_target"
    staged = overlay / "pygen_src/target/rv64i/riscv_core_setting.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(text.replace(original, replacement, 1))
    return {"kind": "derived_rv64i_target", "path": str(overlay),
            "settings_sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
            "base_target": "rv64imc", "supported_isa": ["RV32I", "RV64I"]}


def stage_rv64imfdc_target(output: Path) -> dict:
    """Derive the pinned F/D target without its unvalidated A groups."""
    source = UPSTREAM / "pygen/pygen_src/target/rv64imafdc/riscv_core_setting.py"
    original = "                 riscv_instr_group_t.RV32A, riscv_instr_group_t.RV64A,\n"
    text = source.read_text()
    if text.count(original) != 1:
        raise ValueError("pinned RV64IMAFDC target setting changed; review RV64IMFDC derivation")
    overlay = output / "pyflow_rv64imfdc_target"
    staged = overlay / "pygen_src/target/rv64imfdc/riscv_core_setting.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(text.replace(original, "", 1))
    return {"kind": "derived_rv64imfdc_target", "path": str(overlay),
            "settings_sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
            "base_target": "rv64imafdc", "removed_isa": ["RV32A", "RV64A"]}


def stage_rv64ima_target(output: Path) -> dict:
    """Derive an exact RV64IMA PyFlow target from pinned RV64IMAFDC."""
    source = UPSTREAM / "pygen/pygen_src/target/rv64imafdc/riscv_core_setting.py"
    original = ("supported_isa = [riscv_instr_group_t.RV32I, riscv_instr_group_t.RV32M,\n"
                "                 riscv_instr_group_t.RV64I, riscv_instr_group_t.RV64M,\n"
                "                 riscv_instr_group_t.RV32C, riscv_instr_group_t.RV64C,\n"
                "                 riscv_instr_group_t.RV32A, riscv_instr_group_t.RV64A,\n"
                "                 riscv_instr_group_t.RV32F, riscv_instr_group_t.RV64F,\n"
                "                 riscv_instr_group_t.RV32D, riscv_instr_group_t.RV64D]")
    replacement = ("supported_isa = [riscv_instr_group_t.RV32I, riscv_instr_group_t.RV32M,\n"
                   "                 riscv_instr_group_t.RV32A, riscv_instr_group_t.RV64I,\n"
                   "                 riscv_instr_group_t.RV64M, riscv_instr_group_t.RV64A]")
    content = source.read_text()
    if content.count(original) != 1:
        raise ValueError("pinned RV64IMAFDC target setting changed; review RV64IMA derivation")
    overlay = output / "pyflow_rv64ima_target"
    staged = overlay / "pygen_src/target/rv64ima/riscv_core_setting.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(content.replace(original, replacement, 1))
    return {"kind": "derived_rv64ima_target", "path": str(overlay),
            "settings_sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
            "base_target": "rv64imafdc", "supported_isa": sorted(EXPECTED_TARGET_GROUPS["rv64ima"])}


def stage_rv32imc_zbb_target(output: Path) -> dict:
    """Filter pinned draft RV32B to a compiler-compatible ratified Zbb slice."""
    target = UPSTREAM / "pygen/pygen_src/target/rv32imcb/riscv_core_setting.py"
    b_model = UPSTREAM / "pygen/pygen_src/isa/rv32b_instr.py"
    names = set(re.findall(r"DEFINE_B_INSTR\(riscv_instr_name_t\.([A-Z0-9_]+)",
                           b_model.read_text()))
    if not ZBB_ENUMS <= names or len(names) != 55:
        raise ValueError("pinned RV32B instruction model changed; review Zbb filter")
    source = target.read_text()
    imports = "                                       privileged_mode_t)"
    setting = "unsupported_instr = []"
    if source.count(imports) != 1 or source.count(setting) != 1:
        raise ValueError("pinned RV32IMCB target changed; review Zbb derivation")
    source = source.replace(imports, "                                       privileged_mode_t, riscv_instr_name_t)", 1)
    source = source.replace(setting, "unsupported_instr = [" + ", ".join(
        "riscv_instr_name_t." + name for name in sorted(names - ZBB_ENUMS)) + "]", 1)
    overlay = output / "pyflow_rv32imc_zbb_target"
    staged = overlay / "pygen_src/target/rv32imcb/riscv_core_setting.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(source)
    return {"kind": "filtered_rv32imc_zbb_target", "path": str(overlay),
            "settings_sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
            "base_target": "rv32imcb", "allowed_b_instructions": sorted(ZBB_NAMES)}


def stage_lrsc_compat(output: Path) -> dict:
    """Repair pinned PyFlow's LR/SC stream in an isolated import overlay."""
    source = UPSTREAM / "pygen/pygen_src/riscv_amo_instr_lib.py"
    content = source.read_text()
    edits = (
        ("        self.avail_regs = vsc.randsz_list_t(vsc.enum_t(riscv_reg_t))\n", ""),
        ("random.randrange(0, max_data_page_id - 1)", "random.randrange(0, max_data_page_id)"),
        ("        self.reserved_rd.append(self.rs1_reg)\n",
         "        for reg in self.rs1_reg:\n            self.reserved_rd.append(reg)\n"),
        ("        self.num_mixed_instr in vsc.rangelist(vsc.rng(0, 15))\n",
         "        self.num_mixed_instr == 0\n"),
        ("            # self.lr_instr.rd != self.rs1_reg[0]  # TODO\n",
         "            self.lr_instr.rd != riscv_reg_t.ZERO\n"),
        ("            # self.sc_instr.rd != self.rs1_reg[0]  # TODO\n",
         "            self.sc_instr.rd != riscv_reg_t.ZERO\n"),
        ("        self.sc_instr = riscv_instr.get_rand_instr(include_instr = allowed_sc_instr)\n",
         "        self.sc_instr = riscv_instr.get_rand_instr(include_instr = [\n"
         "            riscv_instr_name_t.SC_D if self.lr_instr.instr_name == riscv_instr_name_t.LR_D\n"
         "            else riscv_instr_name_t.SC_W])\n"),
        ("        self.instr_list.extend((self.lr_instr, self.sc_instr))\n",
         "        if self.lr_instr.rd == self.rs1_reg[0]:\n"
         "            self.lr_instr.rd = (riscv_reg_t.T0 if self.rs1_reg[0] != riscv_reg_t.T0\n"
         "                                else riscv_reg_t.T1)\n"
         "        self.lr_instr.rs1 = self.rs1_reg[0]\n"
         "        self.sc_instr.rs1 = self.rs1_reg[0]\n"
         "        self.sc_instr.rs2 = self.lr_instr.rd\n"
         "        self.instr_list.extend((self.lr_instr, self.sc_instr))\n"),
    )
    for before, after in edits:
        if content.count(before) != 1:
            raise ValueError(f"pinned LR/SC compatibility marker changed: {before.strip()}")
        content = content.replace(before, after, 1)
    overlay = output / "pyflow_lrsc_compat"
    staged = overlay / "pygen_src/riscv_amo_instr_lib.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(content)
    factory = UPSTREAM / "pygen/pygen_src/isa/riscv_instr.py"
    factory_source = factory.read_text()
    before = "idx = random.randrange(0, len(include_instr) - 1)"
    if factory_source.count(before) != 1:
        raise ValueError("pinned instruction factory selection marker changed")
    factory_staged = overlay / "pygen_src/isa/riscv_instr.py"
    factory_staged.parent.mkdir(parents=True, exist_ok=True)
    factory_staged.write_text(factory_source.replace(
        before, "idx = random.randrange(0, len(include_instr))", 1))
    return {"kind": "isolated_lrsc_stream_fix", "path": str(overlay),
            "module_sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
            "instruction_factory_sha256": hashlib.sha256(factory_staged.read_bytes()).hexdigest(),
            "changes": ["repair AMO list construction and one-page selection",
                        "bind LR/SC base, width, and SC data registers",
                        "select both LR.W and LR.D from the pinned instruction factory",
                        "keep LR/SC adjacent for a bounded single-hart oracle"]}


def stage_amo_compat(output: Path, *, count: int = 1) -> dict:
    """Bound the pinned PyFlow AMO stream to one, two, or three operations."""
    if count not in {1, 2, 3}:
        raise ValueError("AMO compatibility stream supports one to three operations")
    base = stage_lrsc_compat(output)
    source = Path(base["path"]) / "pygen_src/riscv_amo_instr_lib.py"
    content = source.read_text()
    edits = (
        ("        self.num_amo in vsc.rangelist(vsc.rng(1, 10))",
         f"        self.num_amo == {count}"),
        ("        self.num_mixed_instr in vsc.rangelist(vsc.rng(0, self.num_amo))",
         "        self.num_mixed_instr == 0"),
        ("include_category=[riscv_instr_category_t.AMO]",
         "include_category=[riscv_instr_category_t.AMO.name]"),
        ("                self.amo_instr[i].rs1.inside(vsc.rangelist(self.rs1_reg))\n", ""),
        ("                self.amo_instr[i].rd.inside(vsc.rangelist(self.rs1_reg))\n", ""),
        ("            self.instr_list.insert(0, self.amo_instr[i])",
         "            self.amo_instr[i].rs1 = self.rs1_reg[0]\n"
         "            self.instr_list.insert(0, self.amo_instr[i])"),
    )
    for before, after in edits:
        if content.count(before) != 1:
            raise ValueError(f"pinned AMO compatibility marker changed: {before.strip()}")
        content = content.replace(before, after, 1)
    if count >= 2:
        before = "            self.amo_instr[i].rs1 = self.rs1_reg[0]"
        after = ("            if self.amo_instr[i].rd == self.rs1_reg[0]:\n"
                 "                self.amo_instr[i].rd = (riscv_reg_t.T0 if self.rs1_reg[0] != riscv_reg_t.T0\n"
                 "                                         else riscv_reg_t.T1)\n" + before)
        if content.count(before) != 1:
            raise ValueError("pinned AMO pair destination marker changed")
        content = content.replace(before, after, 1)
    overlay = output / ("pyflow_amo_pair_compat" if count == 2 else
                        "pyflow_amo_triple_compat" if count == 3 else "pyflow_amo_compat")
    staged = overlay / "pygen_src/riscv_amo_instr_lib.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(content)
    factory = Path(base["path"]) / "pygen_src/isa/riscv_instr.py"
    factory_content = factory.read_text()
    before = "idx = random.randrange(0, len(allowed_instr) - 1)"
    if factory_content.count(before) != 1:
        raise ValueError("pinned AMO instruction factory selection marker changed")
    factory_staged = overlay / "pygen_src/isa/riscv_instr.py"
    factory_staged.parent.mkdir(parents=True, exist_ok=True)
    factory_staged.write_text(factory_content.replace(
        before, "idx = random.randrange(0, len(allowed_instr))", 1))
    return {"kind": "isolated_amo_pair_stream_fix" if count == 2 else
                    "isolated_amo_triple_stream_fix" if count == 3 else "isolated_amo_stream_fix",
            "path": str(overlay),
            "module_sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
            "instruction_factory_sha256": hashlib.sha256(factory_staged.read_bytes()).hexdigest(),
            "changes": ["repair pinned AMO list and one-page selection",
                        "bind AMO base register and select from the AMO category",
                        ("generate one aligned AMO without mixed memory operations"
                         if count == 1 else
                         f"generate {count} aligned AMOs without mixed memory operations")]}


ABI_REGISTERS = ("zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2", "s0", "s1",
                 "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "s2", "s3",
                 "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11", "t3", "t4",
                 "t5", "t6")


def register_number(name: str) -> int:
    if re.fullmatch(r"x(?:[0-9]|[12][0-9]|3[01])", name):
        return int(name[1:])
    if name == "fp":
        return 8
    if name in ABI_REGISTERS:
        return ABI_REGISTERS.index(name)
    raise ValueError(f"unknown generated register: {name}")


def relocate_lrsc_to_done(source: str) -> tuple[str, int]:
    """Place one invariant LR/SC pair immediately before the completion jump."""
    lines = source.splitlines(keepends=True)
    markers = [i for i, line in enumerate(lines) if "#start riscv_lr_sc_instr_stream_" in line]
    if len(markers) != 1 or markers[0] + 2 >= len(lines):
        raise ValueError("LR/SC profile requires exactly one three-instruction stream")
    start = markers[0]
    head = lines[start]
    main_label = re.match(r"^\s*main:\s*", head)
    if main_label:
        head = "                  " + head[main_label.end():]
    address = re.fullmatch(r"\s*la\s+(\w+),\s*(amo_\d+)\+(\d+)\s*#start riscv_lr_sc_instr_stream_0\s*", head)
    lr = re.fullmatch(r"\s*lr\.(w|d)(?:\.[a-z]+)?\s+(\w+),\s*\((\w+)\)\s*", lines[start + 1])
    sc = re.fullmatch(r"\s*sc\.(w|d)(?:\.[a-z]+)?\s+(\w+),\s*(\w+),\s*\((\w+)\)\s*#end riscv_lr_sc_instr_stream_0\s*", lines[start + 2])
    if (not address or not lr or not sc or lr.group(1) != sc.group(1)
            or lr.group(3) != address.group(1) or sc.group(4) != address.group(1)
            or sc.group(3) != lr.group(2) or register_number(lr.group(2)) == 0
            or register_number(lr.group(2)) == register_number(address.group(1))
            or int(address.group(3)) % (4 if lr.group(1) == "w" else 8)):
        raise ValueError("generated LR/SC stream has an unsupported address or data dependency")
    result_register = register_number(sc.group(2))
    if result_register == 0:
        raise ValueError("LR/SC result register must not be x0")
    if len(re.findall(r"(?m)^\s*(?:lr|sc|amo[a-z]+)\.(?:w|d)", source)) != 2:
        raise ValueError("LR/SC profile generated unexpected atomic instructions")
    block = [head, *lines[start + 1:start + 3]]
    if main_label:
        lines[start] = "main:\n"
        del lines[start + 1:start + 3]
    else:
        del lines[start:start + 3]
    jumps = [i for i, line in enumerate(lines)
             if re.fullmatch(r"\s*la\s+x\d+,\s*test_done\s*", line)]
    if len(jumps) != 1:
        raise ValueError("LR/SC profile lacks one completion jump")
    lines[jumps[0]:jumps[0]] = block
    return "".join(lines), result_register


def relocate_amo_stream_to_done(source: str, *, count: int) -> tuple[str, list[str]]:
    """Place one to three upstream AMOs immediately before completion."""
    if count not in {1, 2, 3}:
        raise ValueError("AMO stream count must be one to three")
    lines = source.splitlines(keepends=True)
    markers = [i for i, line in enumerate(lines) if "#start riscv_amo_instr_stream_" in line]
    if len(markers) != 1 or markers[0] + count >= len(lines):
        raise ValueError("AMO profile requires exactly one bounded stream")
    start = markers[0]
    head = lines[start]
    main_label = re.match(r"^\s*main:\s*", head)
    if main_label:
        head = "                  " + head[main_label.end():]
    address = re.fullmatch(r"\s*la\s+(\w+),\s*(amo_\d+)\+(\d+)\s*#start riscv_amo_instr_stream_0\s*", head)
    if not address:
        raise ValueError("generated AMO stream has an unsupported address")
    operations = []
    for index in range(count):
        suffix = (r"\s*#end riscv_amo_instr_stream_0" if index == count - 1 else "")
        operation = re.fullmatch(
            r"\s*(amo(?:swap|add|and|or|xor|min|max|minu|maxu))\.(w|d)(?:\.[a-z]+)?"
            r"\s+(\w+),\s*(\w+),\s*\((\w+)\)" + suffix + r"\s*",
            lines[start + 1 + index])
        if (not operation or operation.group(5) != address.group(1)
                or int(address.group(3)) % (4 if operation.group(2) == "w" else 8)
                or (count >= 2 and register_number(operation.group(3)) ==
                    register_number(address.group(1)))):
            raise ValueError("generated AMO stream has an unsupported operation or dependency")
        operations.append(operation.group(1) + "." + operation.group(2))
    if len(re.findall(r"(?m)^\s*(?:lr|sc|amo[a-z]+)\.(?:w|d)", source)) != count:
        raise ValueError("AMO profile generated unexpected atomic instructions")
    block = [head, *lines[start + 1:start + 1 + count]]
    if main_label:
        lines[start] = "main:\n"
        del lines[start + 1:start + 1 + count]
    else:
        del lines[start:start + 1 + count]
    jumps = [i for i, line in enumerate(lines)
             if re.fullmatch(r"\s*la\s+x\d+,\s*test_done\s*", line)]
    if len(jumps) != 1:
        raise ValueError("AMO profile lacks one completion jump")
    lines[jumps[0]:jumps[0]] = block
    return "".join(lines), operations


def relocate_amo_to_done(source: str) -> tuple[str, str]:
    adapted, operations = relocate_amo_stream_to_done(source, count=1)
    return adapted, operations[0]


def stage_user_target(output: Path, *, settings: bytes, isa: str,
                      target: str, load_store: bool) -> dict:
    """Stage a supplied PyFlow target after checking package-critical settings."""
    try:
        tree = ast.parse(settings.decode("utf-8"))
    except (SyntaxError, UnicodeError) as exc:
        raise ValueError(f"invalid target settings Python: {exc}") from exc
    base_target = {"rv32im": "rv32imc", "rv64i": "rv64imc",
                   "rv64im": "rv64imc", "rv64imfdc": "rv64imafdc",
                   "rv64ima": "rv64imafdc"}.get(isa, target)
    baseline = ast.parse((UPSTREAM / f"pygen/pygen_src/target/{base_target}/riscv_core_setting.py").read_text())
    allowed_names = {statement.targets[0].id for statement in baseline.body
                     if isinstance(statement, ast.Assign) and len(statement.targets) == 1
                     and isinstance(statement.targets[0], ast.Name)}
    baseline_imports = [ast.dump(statement) for statement in baseline.body
                        if isinstance(statement, (ast.Import, ast.ImportFrom))]
    supplied_imports = [ast.dump(statement) for statement in tree.body
                        if isinstance(statement, (ast.Import, ast.ImportFrom))]
    if supplied_imports != baseline_imports:
        raise ValueError("target settings imports must match the pinned target")
    safe_value_nodes = (ast.Constant, ast.List, ast.Tuple, ast.Attribute,
                        ast.Name, ast.Load, ast.UnaryOp, ast.USub, ast.UAdd)
    for statement in tree.body:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) \
                and isinstance(statement.value.value, str):
            continue
        if (not isinstance(statement, ast.Assign) or len(statement.targets) != 1
                or not isinstance(statement.targets[0], ast.Name)
                or statement.targets[0].id not in allowed_names):
            raise ValueError("target settings may contain only pinned imports and configuration assignments")
        key = statement.targets[0].id
        if key == "VELEN":
            original = next(item.value for item in baseline.body
                            if isinstance(item, ast.Assign) and
                            isinstance(item.targets[0], ast.Name) and item.targets[0].id == "VELEN")
            if ast.dump(statement.value) != ast.dump(original):
                raise ValueError("target settings VELEN formula must match the pinned target")
        elif any(not isinstance(node, safe_value_nodes) for node in ast.walk(statement.value)):
            raise ValueError(f"target settings {key} contains executable expressions")
    names: dict[str, ast.expr] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            destination = statement.targets[0]
            if isinstance(destination, ast.Name):
                if destination.id in names:
                    raise ValueError(f"duplicate target setting: {destination.id}")
                names[destination.id] = statement.value

    def member(node: ast.AST, family: str) -> str | None:
        return (node.attr if isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name) and node.value.id == family else None)

    xlen = names.get("XLEN")
    if not isinstance(xlen, ast.Constant) or xlen.value != int(isa[2:4]):
        raise ValueError("target settings XLEN differs from selected ISA")
    groups = names.get("supported_isa")
    parsed = ([member(node, "riscv_instr_group_t") for node in groups.elts]
              if isinstance(groups, ast.List) else None)
    if parsed is None or len(parsed) != len(set(parsed)) or set(parsed) != EXPECTED_TARGET_GROUPS[isa]:
        raise ValueError("target settings supported_isa must match selected ISA exactly")
    privilege = names.get("supported_privileged_mode")
    if (not isinstance(privilege, ast.List) or
            [member(node, "privileged_mode_t") for node in privilege.elts] != ["MACHINE_MODE"] or
            member(names.get("SATP_MODE"), "satp_mode_t") != "BARE"):
        raise ValueError("target settings require bare machine mode only")
    for key, expected in (("NUM_HARTS", 1), ("VECTOR_EXTENSION_ENABLE", 0)):
        value = names.get(key)
        if not isinstance(value, ast.Constant) or value.value != expected:
            raise ValueError(f"target settings require {key}={expected}")
    if load_store:
        value = names.get("support_unaligned_load_store")
        if not isinstance(value, ast.Constant) or value.value != 1:
            raise ValueError("load/store profile needs target support_unaligned_load_store=1")
    overlay = output / "pyflow_user_target"
    staged = overlay / f"pygen_src/target/{target}/riscv_core_setting.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_bytes(settings)
    return {"kind": "user_target", "path": str(overlay),
            "settings_sha256": hashlib.sha256(settings).hexdigest(),
            "supported_isa": sorted(EXPECTED_TARGET_GROUPS[isa])}


def stage_csr_generator(output: Path) -> dict:
    """Adapt the pinned directed CSR generator to bitstring 5 in isolation."""
    source = UPSTREAM / "scripts/gen_csr_test.py"
    original = source.read_text()
    edits = (
        ("csr_val.overwrite(self.mask_bitarray & val_slice, self.pos[0])",
         "csr_val.overwrite(self.pos[0], self.mask_bitarray & val_slice)", 2),
        ("csr_read_mask.overwrite(mask_bitarray, xlen - 1 - field_msb)",
         "csr_read_mask.overwrite(xlen - 1 - field_msb, mask_bitarray)", 1),
        ("csr_value.overwrite(val_bitarray, xlen - 1 - field_msb)",
         "csr_value.overwrite(xlen - 1 - field_msb, val_bitarray)", 1),
        ("csr_val.len", "len(csr_val)", 1),
    )
    adapted = original
    for before, after, count in edits:
        if adapted.count(before) != count:
            raise ValueError(f"pinned CSR generator marker changed: {before}")
        adapted = adapted.replace(before, after)
    staged = output / "csr_compat/gen_csr_test.py"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(adapted)
    return {"kind": "pinned_bitstring5_compatibility",
            "path": str(staged),
            "upstream_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "staged_sha256": hashlib.sha256(staged.read_bytes()).hexdigest()}


def validate_mscratch_map(raw: bytes, *, xlen: int) -> list[str]:
    """Allow only predictable writable machine CSRs in the directed profile."""
    import yaml
    try:
        entries = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid CSR map YAML: {exc}") from exc
    if not isinstance(entries, list) or not 1 <= len(entries) <= 2:
        raise ValueError("CSR profile needs one or two bounded map entries")
    names = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) - {"csr", "address", "privilege_mode", "rv32", "rv64"}:
            raise ValueError("CSR map entry has unsupported fields")
        name = entry.get("csr")
        if (name not in {"mscratch", "mepc"} or name in names or
                entry.get("address") != {"mscratch": 0x340, "mepc": 0x341}[name] or
                entry.get("privilege_mode") != "M"):
            raise ValueError("CSR profile supports unique machine-mode mscratch and mepc only")
        fields = entry.get(f"rv{xlen}")
        expected = {"field_name": "value", "type": "WARL", "reset_val": 0,
                    "msb": xlen - 1, "lsb": 0 if name == "mscratch" else 2}
        if not isinstance(fields, list) or fields != [expected]:
            raise ValueError(f"{name} map must describe its bounded writable field")
        names.append(name)
    if names not in (["mscratch"], ["mscratch", "mepc"]):
        raise ValueError("CSR profile requires mscratch, optionally followed by mepc")
    return names


def floating_state_at_done(trace: Path, *, done: int) -> tuple[list[int], int]:
    """Read committed FPRs and floating CSRs before the raw program completes."""
    registers: list[int | None] = [None] * 32
    frm = 0
    fflags = 0
    completed = False
    with trace.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            fetch = FETCH.match(line)
            if fetch and int(fetch.group(1), 16) == done:
                completed = True
                break
            if not COMMIT.match(line):
                continue
            for number, value in re.findall(r"\bf(\d{1,2})\s+0x([0-9a-f]+)", line, re.I):
                if int(number) < 32:
                    registers[int(number)] = int(value, 16)
            for csr, value in re.findall(r"\bc\d+_(fflags|frm|fcsr)\s+0x([0-9a-f]+)", line, re.I):
                number = int(value, 16)
                if csr == "fflags":
                    fflags = number & 0x1f
                elif csr == "frm":
                    frm = number & 7
                else:
                    frm, fflags = (number >> 5) & 7, number & 0x1f
    if not completed or any(value is None for value in registers):
        raise RuntimeError("Spike floating trace lacks test_done or an initialized FPR")
    return [int(value) for value in registers], (frm << 5) | fflags


def parse_spike_trace(trace: Path, *, done: int, tohost: int,
                      memory_base: int, memory_size: int) -> tuple[list[int], dict[int, int]]:
    """Extract state independently from Spike commits before test_done.

    A committed store supplies its actual address and value. The preceding
    fetch supplies its width; load commits also mention memory and are ignored.
    Unknown memory operations are rejected instead of silently omitted.
    """
    registers = [0] * 32
    at_done: list[int] | None = None
    written: dict[int, int] = {}
    fetch_names: dict[int, str] = {}
    passed = False
    with trace.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            exception = EXCEPTION.match(line)
            if exception and at_done is None:
                raise ReferenceTrap(exception.group(1), int(exception.group(2), 16))
            fetch = FETCH.match(line)
            if fetch:
                pc = int(fetch.group(1), 16)
                fetch_names[pc] = fetch.group(2).lower()
                if pc == done and at_done is None:
                    at_done = registers.copy()
            commit = COMMIT.match(line)
            gpr = GPR_COMMIT.search(line) if commit else None
            if gpr and int(gpr.group(1)) < 32:
                registers[int(gpr.group(1))] = int(gpr.group(2), 16)
            store = STORE.search(line)
            if store and int(store.group(1), 16) == tohost:
                passed = int(store.group(2), 16) == 1
                break
            if commit and at_done is None and MEMORY_ACCESS.search(line):
                name = fetch_names.get(int(commit.group(1), 16))
                if name in LOAD_NAMES or (name and name.startswith("lr.")) or (
                        name and VECTOR_LOAD.fullmatch(name)):
                    continue
                vector_store = VECTOR_STORE_WIDTH.fullmatch(name or "")
                if vector_store:
                    width = int(vector_store.group(1)) // 8
                    for address_text, value_text in STORE.findall(line):
                        address = int(address_text, 16)
                        if address < memory_base or address + width > memory_base + memory_size:
                            raise RuntimeError(f"reference vector store [{address:#x}, {address + width:#x}) outside selected RAM")
                        value = int(value_text, 16)
                        for offset in range(width):
                            written[address + offset] = (value >> (8 * offset)) & 0xff
                    continue
                atomic = (name is not None and
                          (name.startswith("amo") or name.startswith("sc.")))
                match = ATOMIC_WIDTH.search(name) if atomic else None
                width = (4 if match.group(1) == "w" else 8) if match else STORE_WIDTHS.get(name)
                if width is None or store is None:
                    raise RuntimeError(f"unsupported memory operation in Spike trace: {line.strip()}")
                address = int(store.group(1), 16)
                if address < memory_base or address + width > memory_base + memory_size:
                    raise RuntimeError(f"reference store [{address:#x}, {address + width:#x}) outside selected RAM")
                value = int(store.group(2), 16)
                for offset in range(width):
                    written[address + offset] = (value >> (8 * offset)) & 0xff
    if at_done is None or not passed:
        raise RuntimeError(f"Spike did not reach test_done and write tohost=1; see {trace}")
    return at_done, written


def reference_memory_accesses(trace: Path, *, entry: int, done: int) -> dict:
    """Count committed program accesses before the generated completion code."""
    names: dict[int, str] = {}
    result = {"loads": 0, "stores": 0, "misaligned_wide": 0,
              "misaligned_by_instruction": {}}
    in_program = False
    with trace.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            fetch = FETCH.match(line)
            if fetch:
                pc = int(fetch.group(1), 16)
                if pc == entry:
                    in_program = True
                if pc == done:
                    break
                if in_program:
                    names[pc] = fetch.group(2).lower()
            if not in_program:
                continue
            commit = COMMIT.match(line)
            memory = MEMORY_ADDRESS.search(line)
            if not commit or not memory:
                continue
            name = names.get(int(commit.group(1), 16))
            width = LOAD_WIDTHS.get(name)
            if name and name.startswith("lr."):
                match = ATOMIC_WIDTH.search(name)
                width = (4 if match.group(1) == "w" else 8) if match else None
            if width is not None:
                result["loads"] += 1
            else:
                width = STORE_WIDTHS.get(name)
                if name and (name.startswith("amo") or name.startswith("sc.")):
                    match = ATOMIC_WIDTH.search(name)
                    width = (4 if match.group(1) == "w" else 8) if match else None
                if width is None:
                    continue
                result["stores"] += 1
            if width > 1 and int(memory.group(1), 16) % width:
                result["misaligned_wide"] += 1
                by_instruction = result["misaligned_by_instruction"]
                by_instruction[name] = by_instruction.get(name, 0) + 1
    return result


def reference_instruction_count(trace: Path, *, entry: int, done: int,
                                names: set[str]) -> int:
    """Count selected program instructions before the generated completion."""
    count = 0
    in_program = False
    with trace.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            fetch = FETCH.match(line)
            if not fetch:
                continue
            pc = int(fetch.group(1), 16)
            if pc == entry:
                in_program = True
            if pc == done:
                break
            if in_program and fetch.group(2).lower() in names:
                count += 1
    return count


def reference_jump_count(trace: Path, *, entry: int, done: int) -> int:
    return reference_instruction_count(trace, entry=entry, done=done, names=JUMP_NAMES)


def trace_reference(elf: Path, *, spike: str, isa: str, nm: str,
                    budget: int, trace: Path, misaligned: bool = False,
                    memory_base: int = 0, memory_size: int = 0x80000) -> tuple[list[int], dict[int, int]]:
    done = symbol(elf, nm, "test_done")
    tohost = symbol(elf, nm, "tohost")
    command([spike, "-l", "--log-commits", f"--instructions={budget}",
             f"--isa={isa}_zicsr_zifencei", "--priv=m",
             f"-m{memory_base:#x}:{memory_size:#x}",
             *(["--misaligned"] if misaligned else []), str(elf)],
            timeout=90, log=trace)
    try:
        return parse_spike_trace(trace, done=done, tohost=tohost,
                                 memory_base=memory_base, memory_size=memory_size)
    except ReferenceTrap:
        raise
    except RuntimeError as exc:
        raise RuntimeError(f"{exc}; instruction budget {budget}") from exc


def select_memory_signature(written: dict[int, int], limit: int = MEMORY_SIGNATURE_LIMIT) -> dict[int, int]:
    """Choose up to ``limit`` written bytes evenly across address order."""
    if not 1 <= limit <= 1024:
        raise ValueError("memory signature limit must be 1 to 1024 bytes")
    addresses = sorted(written)
    if len(addresses) > limit:
        addresses = ([addresses[0]] if limit == 1 else
                     [addresses[i * (len(addresses) - 1) // (limit - 1)]
                      for i in range(limit)])
    return {address: written[address] for address in addresses}


def verify_saved_package(directory: Path, *, expected_manifest_sha256: str | None = None) -> tuple[dict, str]:
    """Check a saved riscv-dv manifest and its companion artifacts before reuse."""
    manifest = directory / "manifest.json"
    raw = manifest.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_manifest_sha256 is not None and digest != expected_manifest_sha256:
        raise ValueError(f"manifest SHA-256 mismatch: {manifest}")
    package = json.loads(raw)
    if not isinstance(package, dict) or package.get("test_source") != "riscv-dv":
        raise ValueError("saved package is not a riscv-dv manifest")
    initial_memory(package, supported_isa={package.get("isa", "")})
    layout = package.get("memory_layout")
    if layout is not None:
        if not isinstance(layout, dict):
            raise ValueError("invalid package memory layout")
        if layout.get("mode") == "shared_flat":
            base, size = layout.get("base"), layout.get("size")
            if (type(base) is not int or type(size) is not int or base < 0 or
                    base % 4096 or size < 4096 or size % 4096 or base + size > 1 << 32
                    or flat_memory_fit(package, base=base, size=size,
                                       reset_pc=package["entry"],
                                       supported_isa={package["isa"]})):
                raise ValueError("saved package does not fit its shared memory layout")
        elif layout.get("mode") == "split_disjoint":
            base, instruction_size, data_base, data_size = (
                layout.get(key) for key in ("instruction_base", "instruction_size",
                                            "data_base", "data_size"))
            if (any(type(value) is not int for value in
                    (base, instruction_size, data_base, data_size)) or
                    base < 0 or instruction_size <= 0 or data_size <= 0 or
                    base % 4096 or instruction_size % 4096 or data_size % 4096 or
                    base + instruction_size != data_base or
                    data_base + data_size > 1 << 32 or
                    not base <= package["entry"] < data_base or
                    not data_base <= package["oracle"]["address"] or
                    package["oracle"]["address"] + 8 > data_base + data_size):
                raise ValueError("invalid split memory layout")
            try:
                check_split_segments(package["segments"], memory_base=base,
                                     data_base=data_base, memory_end=data_base + data_size)
            except RuntimeError as exc:
                raise ValueError(f"invalid split memory layout: {exc}") from exc
        else:
            raise ValueError("unknown package memory layout")
    provenance = package.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("saved package lacks provenance hashes")
    for filename, key in (("generated.S", "assembly_sha256"),
                          ("program.elf", "elf_sha256"),
                          ("imem.hex", "imem_sha256"),
                          ("dmem.hex", "dmem_sha256")):
        expected = provenance.get(key)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError(f"saved package lacks {key}")
        actual = hashlib.sha256((directory / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"{filename} SHA-256 mismatch")
    upstream_hash = provenance.get("upstream_assembly_sha256")
    if upstream_hash is not None:
        if hashlib.sha256((directory / "upstream-generated.S").read_bytes()).hexdigest() != upstream_hash:
            raise ValueError("upstream-generated.S SHA-256 mismatch")
    coverage = package.get("reference_coverage")
    if coverage is not None:
        if not isinstance(coverage, dict) or coverage.get("kind") != "spike_reference_execution":
            raise ValueError("invalid reference coverage metadata")
        report = directory / "coverage/upstream/CoverageReport.txt"
        if hashlib.sha256(report.read_bytes()).hexdigest() != coverage.get("report_sha256"):
            raise ValueError("reference coverage report SHA-256 mismatch")
    startup_hash = package.get("generation", {}).get("floating_startup_sha256")
    if startup_hash is not None:
        if hashlib.sha256((directory / "user_init.s").read_bytes()).hexdigest() != startup_hash:
            raise ValueError("floating startup SHA-256 mismatch")
    input_testlist_hash = package.get("generation", {}).get("input_testlist_sha256")
    if input_testlist_hash is not None:
        if hashlib.sha256((directory / "input-testlist.yaml").read_bytes()).hexdigest() != input_testlist_hash:
            raise ValueError("custom test list SHA-256 mismatch")
    input_target_hash = package.get("generation", {}).get("input_target_sha256")
    if input_target_hash is not None:
        if input_target_hash != package.get("generation", {}).get("pyflow_target", {}).get("settings_sha256"):
            raise ValueError("custom target metadata digest mismatch")
        if hashlib.sha256((directory / "input-target.py").read_bytes()).hexdigest() != input_target_hash:
            raise ValueError("custom target SHA-256 mismatch")
    csr_map_hash = package.get("generation", {}).get("csr_map_sha256")
    if csr_map_hash is not None:
        if hashlib.sha256((directory / "input-csr-map.yaml").read_bytes()).hexdigest() != csr_map_hash:
            raise ValueError("CSR map SHA-256 mismatch")
        compatibility = package["generation"].get("csr_generator_compatibility", {})
        if (compatibility.get("kind") != "pinned_bitstring5_compatibility" or
                hashlib.sha256((directory / "csr-generator.py").read_bytes()).hexdigest()
                != compatibility.get("staged_sha256")):
            raise ValueError("CSR generator compatibility SHA-256 mismatch")
    atomic_profile = package.get("generation", {}).get("profile")
    if atomic_profile in {"riscv_lr_sc_test", "riscv_amo_test", "riscv_amo_pair_test", "riscv_amo_triple_test"}:
        target = package["generation"].get("pyflow_target", {})
        compatibility = package["generation"].get("pyflow_compatibility", {})
        stem = ("lrsc" if atomic_profile == "riscv_lr_sc_test" else
                "amo-pair" if atomic_profile == "riscv_amo_pair_test" else
                "amo-triple" if atomic_profile == "riscv_amo_triple_test" else "amo")
        for filename, expected in (("target-settings.py", target.get("settings_sha256")),
                                   (f"{stem}-generator.py", compatibility.get("module_sha256")),
                                   (f"{stem}-instruction-factory.py", compatibility.get("instruction_factory_sha256"))):
            if (not isinstance(expected, str) or
                    hashlib.sha256((directory / filename).read_bytes()).hexdigest() != expected):
                raise ValueError(f"{filename} SHA-256 mismatch")
    if package.get("isa") == "rv32imc_zbb_zicsr_zifencei":
        target = package.get("generation", {}).get("pyflow_target", {})
        if (target.get("kind") != "filtered_rv32imc_zbb_target" or
                hashlib.sha256((directory / "target-settings.py").read_bytes()).hexdigest()
                != target.get("settings_sha256")):
            raise ValueError("Zbb target-settings.py SHA-256 mismatch")
    return package, digest


def collect_reference_coverage(directory: Path, *, raw_elf: Path, nm: str,
                               target: str, python: str,
                               environment: dict[str, str]) -> dict:
    """Run upstream PyFlow coverage on the executed raw program before test_done."""
    trace = directory / "reference.trace"
    entry = symbol(raw_elf, nm, "_start")
    done = symbol(raw_elf, nm, "test_done")
    lines = trace.read_text().splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines)
                  if (match := FETCH.match(line)) and int(match.group(1), 16) == entry), None)
    if start is None:
        raise RuntimeError("reference coverage trace lacks program entry")
    stop = next((i for i, line in enumerate(lines[start:], start)
                 if (match := FETCH.match(line)) and int(match.group(1), 16) == done), None)
    if stop is None or stop <= start:
        raise RuntimeError("reference coverage trace lacks test_done")
    coverage = directory / "coverage"
    inputs = coverage / "input"
    inputs.mkdir(parents=True, exist_ok=True)
    # Upstream's Spike converter ignores everything until PC 0x1010. This
    # marker is skipped; the retained trace starts at the generated entry.
    normalized = inputs / "reference.log"
    normalized.write_text("core   0: 0x00001010 (0x00000013) nop\n" +
                          "".join(lines[start:stop]))
    output_name = "processorci_cov_" + uuid.uuid4().hex
    temporary = UPSTREAM / output_name
    saved = coverage / "upstream"
    if saved.exists():
        shutil.rmtree(saved)
    try:
        command([python, str(UPSTREAM / "cov.py"), "--dir", str(inputs.resolve()),
                 "--simulator", "pyflow", "--target", target,
                 "--output", output_name], cwd=UPSTREAM, env=environment,
                timeout=180, log=coverage / "coverage.log")
    finally:
        if temporary.exists():
            shutil.move(str(temporary), str(saved))
    report = saved / "CoverageReport.txt"
    if not report.is_file():
        raise RuntimeError("upstream PyFlow produced no coverage report")
    report_text = report.read_text()
    groups = re.search(r"Total groups in report: (\d+)", report_text)
    model_logs = list(saved.glob("sim_riscv_instr_cov_test_*.log"))
    processed = (re.search(r"Finished processing 1 trace CSV, (\d+) instructions",
                           model_logs[0].read_text()) if len(model_logs) == 1 else None)
    csv_path = normalized.with_suffix(".csv")
    if not groups or not processed or not csv_path.is_file():
        raise RuntimeError("upstream PyFlow coverage output is incomplete")
    converted = max(0, len(csv_path.read_text().splitlines()) - 1)
    sampled = int(processed.group(1))
    if converted == 0 or sampled == 0:
        raise RuntimeError("upstream PyFlow sampled no reference instructions")
    return {"kind": "spike_reference_execution", "converted_instructions": converted,
            "model_processed_instructions": sampled,
            "coverage_groups_reported": int(groups.group(1)),
            "report": "coverage/upstream/CoverageReport.txt",
            "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            "source_trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest(),
            "dut_coverage": False}


def instrument(source: str, registers: list[int], xlen: int,
               memory_signature: dict[int, int] | None = None,
               floating_signature: tuple[list[int], int] | None = None,
               ignored_registers: set[int] | None = None) -> str:
    if source.count("test_done:") != 1:
        raise ValueError("generated assembly lacks one test_done label")
    matches = re.findall(r"\bla\s+x(\d+),\s*test_done\b", source)
    if len(matches) != 1 or not 1 <= int(matches[0]) <= 31:
        raise ValueError("generated assembly lacks one identifiable test_done jump scratch register")
    scratch = int(matches[0])
    checks = []
    for number in range(1, 32):
        if number == scratch or number in (ignored_registers or set()):
            continue
        checks += [f"    li x{scratch}, 0x{registers[number] & ((1 << xlen) - 1):x}",
                   f"    bne x{number}, x{scratch}, processorci_fail"]
    if memory_signature:
        temporary = 2 if scratch == 1 else 1
        checks.append("    # ProcessorCI Spike-derived memory byte checks")
        for address, value in sorted(memory_signature.items()):
            checks += [f"    li x{scratch}, 0x{address:x}",
                       f"    lbu x{temporary}, 0(x{scratch})",
                       f"    li x{scratch}, 0x{value:x}",
                       f"    bne x{temporary}, x{scratch}, processorci_fail"]
    if floating_signature is not None:
        if xlen != 64 or len(floating_signature[0]) != 32:
            raise ValueError("F/D signature requires 32 RV64 floating registers")
        temporary = 2 if scratch == 1 else 1
        checks.append("    # ProcessorCI Spike-derived FPR and fcsr checks")
        for number, value in enumerate(floating_signature[0]):
            checks += [f"    fmv.x.d x{temporary}, f{number}",
                       f"    li x{scratch}, 0x{value:x}",
                       f"    bne x{temporary}, x{scratch}, processorci_fail"]
        checks += [f"    csrr x{temporary}, fcsr",
                   f"    li x{scratch}, 0x{floating_signature[1]:x}",
                   f"    bne x{temporary}, x{scratch}, processorci_fail"]
    body = source.replace("test_done:", "test_done:\n" + "\n".join(checks), 1)
    return body + "\n.section .text\nprocessorci_fail:\n    li gp, 3\n    j write_tohost\n"


def image(segments: list[dict], output: Path, executable: bool) -> None:
    with output.open("w", encoding="ascii") as stream:
        for segment in segments:
            if bool(segment["flags"] & 1) != executable:
                continue
            data = bytes.fromhex(segment["hex"]) + bytes(segment["memory_size"] - segment["file_size"])
            for offset in range(0, len(data), 16):
                stream.write(f"@{segment['address'] + offset:016x} " +
                             " ".join(f"{byte:02x}" for byte in data[offset:offset + 16]) + "\n")


def check_split_segments(segments: list[dict], *, memory_base: int,
                         data_base: int, memory_end: int) -> None:
    """Require distinct executable and data LOAD regions in a flat reference map."""
    has_instruction = has_data = False
    for segment in segments:
        start = segment["address"]
        end = start + segment["memory_size"]
        executable = bool(segment["flags"] & 1)
        if segment["flags"] & 3 == 3:
            raise RuntimeError("split memory cannot route a writable executable LOAD segment")
        if executable:
            has_instruction = True
            if start < memory_base or end > data_base:
                raise RuntimeError(f"instruction LOAD [{start:#x}, {end:#x}) outside instruction region")
        else:
            has_data = True
            if start < data_base or end > memory_end:
                raise RuntimeError(f"data LOAD [{start:#x}, {end:#x}) outside data region")
    if not has_instruction or not has_data:
        raise RuntimeError("split memory needs executable and data LOAD segments")


def write_reports(output: Path, report: dict) -> None:
    report["failed"] = sum(row["status"] in ("failed", "unsupported")
                           for row in report["results"])
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    suite = ET.Element("testsuite", name="riscv-dv", tests=str(len(report["results"])),
                       failures=str(report["failed"]))
    for row in report["results"]:
        case = ET.SubElement(suite, "testcase", name=row["test_id"],
                             time=str(row.get("seconds", 0)))
        if "error" in row:
            ET.SubElement(case, "failure", message=row["error"]).text = row["error"]
    ET.ElementTree(suite).write(output / "report.junit.xml", encoding="unicode",
                                xml_declaration=True)


class HostMock:
    """Exercise the real sparse serial loader and stop/readback contract."""
    def __init__(self):
        self.words: dict[int, int] = {}
        self.address = 0
        self.stop_address = 0

    def stop_clk(self) -> None:
        pass

    def load_msb_accumulator(self, value: int) -> None:
        self.address = value << 8

    def load_lsb_accumulator(self, value: int) -> None:
        self.address |= value

    def write_from_accumulator(self, count: int, words: list[int]) -> None:
        if count != len(words):
            raise RuntimeError("mock load count differs from words")
        self.words.update({self.address + 4 * i: word for i, word in enumerate(words)})

    def set_timeout(self, cycles: int) -> None:
        self.cycles = cycles

    def set_execution_end_address(self, address: int) -> None:
        self.stop_address = address << 2

    def execute_until_stop(self, host_timeout: float) -> bytes:
        if self.stop_address not in self.words:
            raise RuntimeError("mock stop address was not loaded")
        self.words[self.stop_address] = 1
        return b"luck" + (3).to_bytes(4, "big")

    def read_memory(self, address: int) -> bytes:
        return self.words[address].to_bytes(4, "big")


def generate_csr(args: argparse.Namespace) -> dict:
    """Package the pinned directed CSR generator's self-checking mscratch test."""
    if args.isa not in {"rv32i", "rv64i"}:
        raise ValueError("riscv_csr_test currently supports RV32I and RV64I only")
    if (args.load_store or args.single_hart_no_csr or args.testlist is not None
            or args.target_settings is not None or args.upstream_option
            or args.reference_coverage):
        raise ValueError("riscv_csr_test uses its own CSR map and bare machine-mode runtime")
    if args.backend != "pyflow":
        raise ValueError("riscv_csr_test uses the pinned Python CSR generator")
    if args.target and args.target != ISAS[args.isa][0]:
        raise ValueError("CSR target differs from selected ISA")
    if args.tests < 1 or args.seed < 0 or args.max_cycles < 1 or args.max_cycles > 0xffffff:
        raise ValueError("CSR tests, seed, or controller cycle limit out of range")
    if (args.memory_base < 0 or args.memory_base % 4096 or args.memory_size < 0x3000
            or args.memory_size > 16 * 1024 * 1024 or args.memory_size % 4096
            or args.memory_base + args.memory_size > 1 << 32):
        raise ValueError("CSR profile needs 4 KiB-aligned RAM of at least 12 KiB within 32-bit addresses")
    if (args.reset_pc < args.memory_base or args.reset_pc % 4 or
            args.reset_pc >= args.memory_base + args.memory_size):
        raise ValueError("CSR reset PC must be word-aligned within selected RAM")
    tohost_base = args.data_base if args.data_base is not None else args.memory_base + 0x2000
    if (tohost_base % 4096 or tohost_base <= args.reset_pc or
            tohost_base + 8 > args.memory_base + args.memory_size):
        raise ValueError("CSR tohost base must be 4 KiB-aligned above reset PC and inside RAM")
    if not (UPSTREAM / "scripts/gen_csr_test.py").is_file():
        raise ValueError("pinned riscv-dv CSR generator missing")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=UPSTREAM, text=True).strip()
    if revision != PIN:
        raise ValueError(f"riscv-dv revision {revision} differs from pinned {PIN}")
    target, abi, default_prefix = ISAS[args.isa]
    prefix = args.toolchain_prefix or default_prefix
    for tool in (prefix + "gcc", prefix + "nm", args.spike):
        if not shutil.which(tool):
            raise ValueError(f"required tool unavailable: {tool}")
    if importlib.util.find_spec("yaml") is None or importlib.util.find_spec("bitstring") is None:
        raise ValueError("CSR generator needs PyYAML and bitstring from requirements-riscv-dv.txt")
    csr_map = args.csr_map or ROOT / "examples/riscv-dv/csr-mscratch.yaml"
    csr_bytes = csr_map.read_bytes()
    csr_names = validate_mscratch_map(csr_bytes, xlen=int(args.isa[2:4]))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    compatibility = stage_csr_generator(output)
    environment = os.environ.copy()
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
    environment["PYTHONPATH"] = (str(UPSTREAM / "scripts") + os.pathsep +
                                 environment.get("PYTHONPATH", ""))
    required_isa = f"{args.isa}_zicsr_zifencei"
    report = {"tool": "riscv-dv", "revision": revision, "backend": "directed_csr_python",
              "isa": args.isa, "profile": args.profile, "requested": args.tests,
              "generated": 0, "compiled": 0, "spike_validated": 0,
              "package_validated": 0, "host_mock_validated": 0,
              "reference_coverage_validated": 0, "hardware_validated": 0,
              "csr_map_sha256": hashlib.sha256(csr_bytes).hexdigest(),
              "csrs": csr_names,
              "csr_generator_compatibility": {k: v for k, v in compatibility.items() if k != "path"},
              "results": []}
    sys.path.insert(0, str(ROOT / "tools"))
    from build_advanced import elf_segments
    for offset in range(args.tests):
        seed = args.seed + offset
        name = f"riscv_csr_test-{args.isa}-{seed}"
        directory = output / name
        directory.mkdir(exist_ok=True)
        row = {"test_id": name, "seed": seed, "status": "failed"}
        report["results"].append(row)
        reproduce = [sys.executable, "-m", "riscv_test_runner.cli", "--tool", "riscv-dv",
                     "--isa", args.isa, "--profile", args.profile, "--seed", str(seed),
                     "--tests", "1", "--csr-map", str(directory / "input-csr-map.yaml"),
                     "--memory-base", hex(args.memory_base), "--memory-size", hex(args.memory_size),
                     "--reset-pc", hex(args.reset_pc), "--max-cycles", str(args.max_cycles),
                     "--spike", args.spike, "--output", str(output)]
        if args.data_base is not None:
            reproduce += ["--data-base", hex(args.data_base)]
        if args.toolchain_prefix:
            reproduce += ["--toolchain-prefix", args.toolchain_prefix]
        row["reproduction_command"] = shlex.join(reproduce)
        started = time.monotonic()
        try:
            (directory / "input-csr-map.yaml").write_bytes(csr_bytes)
            shutil.copy2(compatibility["path"], directory / "csr-generator.py")
            upstream_dir = directory / "upstream/asm_test"
            upstream_dir.mkdir(parents=True, exist_ok=True)
            command([sys.executable, str(directory / "csr-generator.py"), "--csr_file",
                     str(directory / "input-csr-map.yaml"), "--xlen", args.isa[2:4],
                     "--iterations", "1", "--out", str(upstream_dir),
                     "--end_signature_addr", f"{tohost_base:x}", "--seed", str(seed)],
                    cwd=UPSTREAM, env=environment, timeout=args.generator_timeout,
                    log=directory / "generation.log")
            upstream_source = directory / "upstream-generated.S"
            shutil.copy2(upstream_dir / "riscv_csr_test_0.S", upstream_source)
            generated = upstream_source.read_text()
            if generated.count(".org 0x80") != 1 or generated.count("\ncsr_pass:\n") != 1:
                raise RuntimeError("pinned CSR generator output layout changed")
            generated = generated.replace(".org 0x80", ".org 0x0", 1)
            generated = generated.replace("\ncsr_pass:\n", "\ntest_done:\ncsr_pass:\n", 1)
            generated += "\n.section .tohost,\"aw\",@progbits\n.align 3\n.globl tohost\ntohost: .dword 0\n"
            source = directory / "generated.S"
            source.write_text(generated)
            (directory / "checked.S").write_text(generated)
            report["generated"] += 1
            row["status"] = "generated"
            linker = directory / "link.ld"
            linker_text = (UPSTREAM / "scripts/link.ld").read_text()
            linker_text = linker_text.replace("0x80000000", f"0x{args.reset_pc:x}", 1)
            linker_text = linker_text.replace("*(.text) }", "*(.text.init) *(.text) }", 1)
            linker_text = linker_text.replace("  . = ALIGN(0x1000);\n  .tohost",
                                              f"  . = 0x{tohost_base:x};\n  .tohost", 1)
            linker.write_text(linker_text)
            elf = directory / "program.elf"
            command([prefix + "gcc", "-static", "-mcmodel=medany", "-nostdlib",
                     "-nostartfiles", "-Wl,--no-relax", "-Wl,--build-id=none",
                     "-T", str(linker), f"-march={required_isa}", f"-mabi={abi}",
                     str(source), "-o", str(elf)], timeout=60, log=directory / "compile.log")
            report["compiled"] += 1
            row["status"] = "compiled"
            entry, segments = elf_segments(elf)
            tohost = symbol(elf, prefix + "nm", "tohost")
            if entry != args.reset_pc or tohost != tohost_base:
                raise RuntimeError("CSR ELF entry or tohost differs from configured addresses")
            if args.data_base is not None:
                check_split_segments(segments, memory_base=args.memory_base,
                                     data_base=args.data_base,
                                     memory_end=args.memory_base + args.memory_size)
            _, written = trace_reference(elf, spike=args.spike, isa=args.isa,
                                         nm=prefix + "nm", budget=10000,
                                         trace=directory / "reference.trace",
                                         memory_base=args.memory_base,
                                         memory_size=args.memory_size)
            if written:
                raise RuntimeError("CSR profile unexpectedly committed data stores before completion")
            report["spike_validated"] += 1
            row["status"] = "spike_validated"
            package = {"schema_version": 1, "test_source": "riscv-dv", "test_id": name,
                       "isa": required_isa, "entry": entry, "segments": segments,
                       "oracle": {"type": "selfcheck_tohost", "address": tohost,
                                  "pass_value": 1, "failure_rule": "odd value greater than 1"},
                       "completion": {"type": "tohost_write", "max_cycles": args.max_cycles},
                       "linker_layout": {"mode": "fixed_tohost", "tohost_base": f"0x{tohost:x}"},
                       "memory_layout": ({"mode": "split_disjoint",
                                          "instruction_base": args.memory_base,
                                          "instruction_size": args.data_base - args.memory_base,
                                          "data_base": args.data_base,
                                          "data_size": args.memory_base + args.memory_size - args.data_base}
                                         if args.data_base is not None else
                                         {"mode": "shared_flat", "base": args.memory_base,
                                          "size": args.memory_size}),
                       "register_signature": {}, "memory_signature": {},
                       "memory_signature_total_written_bytes": 0,
                       "signature_policy": ("upstream directed " + ", ".join(csr_names) +
                                            " read/write self-check; Spike pass tohost=1"),
                       "generation": {"profile": args.profile, "seed": seed,
                                      "backend": "directed_csr_python",
                                      "csr_map_sha256": hashlib.sha256(csr_bytes).hexdigest(),
                                      "csrs": csr_names,
                                      "csr_generator_compatibility": {k: v for k, v in compatibility.items() if k != "path"}},
                       "core_requirements": {"machine_mode": True, "zicsr": True,
                                             "zifencei": True, "mscratch": "mscratch" in csr_names,
                                             "mepc": "mepc" in csr_names,
                                             **({"mepc_writable_bits": [int(args.isa[2:4]) - 1, 2]}
                                                if "mepc" in csr_names else {}),
                                             "single_hart": True,
                                             "memory_base": args.memory_base,
                                             "memory_size": args.memory_size,
                                             "reset_pc": args.reset_pc,
                                             "split_memory": args.data_base is not None,
                                             "misaligned_load_store": False},
                       "provenance": {"upstream": "https://github.com/chipsalliance/riscv-dv",
                                      "revision": revision,
                                      "assembly_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                      "upstream_assembly_sha256": hashlib.sha256(upstream_source.read_bytes()).hexdigest(),
                                      "elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest()},
                       "reference_model": "Spike", "reference_validated": True,
                       "hardware_execution": "pending"}
            reasons = flat_memory_fit(package, base=args.memory_base,
                                      size=args.memory_size, reset_pc=args.reset_pc,
                                      supported_isa={required_isa})
            if reasons:
                raise RuntimeError("CSR package does not fit selected memory: " + "; ".join(reasons))
            initial = initial_memory(package, supported_isa={required_isa})
            image(segments, directory / "imem.hex", True)
            image(segments, directory / "dmem.hex", False)
            package["provenance"]["imem_sha256"] = hashlib.sha256((directory / "imem.hex").read_bytes()).hexdigest()
            package["provenance"]["dmem_sha256"] = hashlib.sha256((directory / "dmem.hex").read_bytes()).hexdigest()
            (directory / "manifest.json").write_text(json.dumps(package, indent=2) + "\n")
            package, digest = verify_saved_package(directory)
            row["manifest_sha256"] = digest
            report["package_validated"] += 1
            observed = dict(initial)
            observed[tohost] = 1
            observed[tohost + 1] = 1
            if outcome(package, observed, stopped=True) != "SELF_CHECK_FAILURE":
                raise RuntimeError("CSR host oracle did not reject failing status")
            used_end = max(segment["address"] + segment["memory_size"] for segment in segments)
            mock_size = (used_end - args.memory_base + 3) & ~3
            result = run_package(HostMock(), package, supported_isa={required_isa},
                                 memory_base=args.memory_base, memory_size=mock_size,
                                 reset_pc=args.reset_pc)
            if result["outcome"] != "PASS":
                raise RuntimeError(f"CSR host mock rejected package: {result['outcome']}")
            report["host_mock_validated"] += 1
            row.update(status="host_mock_validated", manifest=str(directory / "manifest.json"),
                       elf_sha256=package["provenance"]["elf_sha256"])
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired,
                subprocess.CalledProcessError) as exc:
            row["error"] = str(exc)
            row["failed_stage"] = row["status"]
            row["status"] = "failed"
        row["seconds"] = round(time.monotonic() - started, 3)
        write_reports(output, report)
        if "error" in row and args.stop_on_error:
            break
    return report


def generate(args: argparse.Namespace) -> dict:
    if args.profile == "riscv_csr_test":
        return generate_csr(args)
    lrsc = args.profile == "riscv_lr_sc_test"
    amo_count = {"riscv_amo_test": 1, "riscv_amo_pair_test": 2,
                 "riscv_amo_triple_test": 3}.get(args.profile, 0)
    amo = amo_count > 0
    atomic = lrsc or amo
    zbb = args.isa == "rv32imc_zbb"
    if args.isa not in ISAS:
        raise ValueError(f"unsupported ISA: {args.isa}")
    if args.profile not in PROFILES:
        raise ValueError(f"unsupported profile: {args.profile}")
    if atomic and args.isa != "rv64ima":
        raise ValueError("bounded atomic profiles currently require RV64IMA")
    if args.isa == "rv64ima" and not atomic:
        raise ValueError("RV64IMA currently supports only bounded LR/SC and AMO profiles")
    if zbb and (args.profile != "riscv_arithmetic_basic_test" or args.load_store or
                args.testlist or args.target_settings or args.single_hart_no_csr or
                args.upstream_option):
        raise ValueError("RV32IMC_Zbb currently requires the bounded arithmetic profile and built-in target")
    if atomic and (args.load_store or args.testlist or
                   args.single_hart_no_csr or args.reference_coverage or args.upstream_option):
        raise ValueError("atomic profiles control their stream, target, runtime, and oracle options")
    if args.csr_map is not None:
        raise ValueError("--csr-map requires riscv_csr_test")
    floating = args.isa == "rv64imfdc"
    if args.single_hart_no_csr and floating:
        raise ValueError("single-hart CSR-free startup is unavailable for floating-point programs")
    if floating and (args.profile not in {"riscv_rand_instr_test", "riscv_arithmetic_basic_test",
                                          "riscv_jump_stress_test"}
                     or args.load_store):
        raise ValueError("RV64IMFDC requires random, arithmetic, or jump profile without load/store streams")
    if not UPSTREAM.joinpath("run.py").is_file():
        raise ValueError("riscv-dv missing; run git submodule update --init third_party_repositories/riscv-dv")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=UPSTREAM, text=True).strip()
    if revision != PIN:
        raise ValueError(f"riscv-dv revision {revision} differs from pinned {PIN}")
    if args.backend != "pyflow":
        raise ValueError("only the validated pyflow backend is available")
    if args.tests < 1 or args.instr_count < 1 or args.seed < 0 or args.max_cycles < 1:
        raise ValueError("tests, instruction count, and cycle limit must be positive; seed must be nonnegative")
    if not 1 <= args.memory_signature_limit <= 1024:
        raise ValueError("memory signature limit must be 1 to 1024 bytes")
    if args.max_cycles > 0xffffff:
        raise ValueError("cycle limit exceeds ProcessorCI controller's 24-bit timeout")
    if any(not OPTION.fullmatch(option) for option in args.upstream_option):
        raise ValueError("upstream options must have safe +name=value syntax")
    controlled = [option.split("=", 1)[0][1:] for option in args.upstream_option
                  if option.split("=", 1)[0][1:] in CONTROLLED_OPTIONS]
    if controlled:
        raise ValueError("ProcessorCI controls upstream options: " + ", ".join(controlled))
    unknown = [option.split("=", 1)[0][1:] for option in args.upstream_option
               if option.split("=", 1)[0][1:] not in SAFE_OPTIONS]
    if unknown:
        raise ValueError("unvalidated upstream options for FPGA packages: " + ", ".join(unknown))
    if args.single_hart_no_csr and any(
            option.startswith("+no_fence=") and option != "+no_fence=1"
            for option in args.upstream_option):
        raise ValueError("single-hart CSR-free startup requires no_fence=1")
    if floating and any(option.split("=", 1)[0][1:] in
                        {"no_directed_instr", "no_load_store"} for option in args.upstream_option):
        raise ValueError("RV64IMFDC controls directed and load/store stream options")
    if floating and args.profile == "riscv_jump_stress_test" and any(
            option.startswith("+no_branch_jump=") for option in args.upstream_option):
        raise ValueError("RV64IMFDC jump profile controls no_branch_jump")
    target, abi, default_prefix = ISAS[args.isa]
    required_isa = args.isa if args.single_hart_no_csr else f"{args.isa}_zicsr_zifencei"
    prefix = args.toolchain_prefix or default_prefix
    if args.target and args.target != target:
        raise ValueError(f"ISA {args.isa} requires validated upstream target {target}")
    if (args.memory_base < 0 or args.memory_base % 4096 or
            args.memory_size < 4096 or args.memory_size > 16 * 1024 * 1024 or
            args.memory_size % 4096 or args.memory_base + args.memory_size > 1 << 32):
        raise ValueError("controller RAM needs a 4 KiB-aligned base and size, up to 16 MiB within 32-bit addresses")
    if (args.reset_pc < args.memory_base or args.reset_pc >= args.memory_base + args.memory_size
            or args.reset_pc % 4):
        raise ValueError("reset PC must be word-aligned and inside selected RAM")
    if args.data_base is not None and (args.data_base % 4096 or
            args.data_base <= args.reset_pc or
            args.data_base >= args.memory_base + args.memory_size):
        raise ValueError("data base must be 4 KiB-aligned, above reset PC, and inside selected RAM")
    if args.load_store and args.profile != "riscv_rand_instr_test":
        raise ValueError("--load-store requires riscv_rand_instr_test")
    misaligned = args.load_store or args.profile == "riscv_unaligned_load_store_test"
    for tool in (prefix + "gcc", prefix + "nm", args.spike):
        if not shutil.which(tool):
            raise ValueError(f"required tool unavailable: {tool}")
    for module in ("yaml", "vsc", "bitstring", "pandas", "tabulate"):
        if importlib.util.find_spec(module) is None:
            raise ValueError(f"PyFlow dependency unavailable: {module}; install requirements-riscv-dv.txt")
    try:
        import yaml
    except ImportError as exc:
        raise ValueError("PyYAML is required in the selected Python environment") from exc
    profiles = yaml.safe_load((UPSTREAM / "yaml/base_testlist.yaml").read_text())
    upstream_profile = ({"test": args.profile, "gen_test": "riscv_instr_base_test",
                         "gen_opts": "+num_of_sub_program=0 +no_fence=1 +no_branch_jump=1 "
                                     "+no_load_store=1 +disable_compressed_instr=1 "
                                     f"+directed_instr_0={'riscv_lr_sc_instr_stream' if lrsc else 'riscv_amo_instr_stream'},1"}
                        if atomic else
                        next((p for p in profiles if p.get("test") == args.profile), None))
    if upstream_profile is None:
        raise ValueError(f"upstream profile unavailable: {args.profile}")
    profile, testlist_hash = (custom_profile(args.testlist, args.profile,
                                            load_store=args.load_store, floating=floating)
                              if args.testlist is not None else (upstream_profile, None))
    input_testlist_bytes = args.testlist.read_bytes() if testlist_hash is not None else None
    if (input_testlist_bytes is not None and
            hashlib.sha256(input_testlist_bytes).hexdigest() != testlist_hash):
        raise ValueError("custom test list changed while selecting its profile")
    input_target_bytes = args.target_settings.read_bytes() if args.target_settings is not None else None
    sys.path.insert(0, str(ROOT / "tools"))
    from build_advanced import elf_segments
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {"tool": "riscv-dv", "revision": revision, "backend": args.backend,
              "isa": args.isa, "profile": args.profile, "requested": args.tests,
              "generated": 0, "compiled": 0, "spike_validated": 0,
              "package_validated": 0, "host_mock_validated": 0,
              "reference_coverage_validated": 0,
              "hardware_validated": 0, "results": [],
              "python": sys.version.split()[0],
              "toolchain": subprocess.check_output([prefix + "gcc", "--version"], text=True).splitlines()[0],
              "spike": " ".join(subprocess.run([args.spike, "--help"], capture_output=True,
                                                  text=True).stderr.splitlines()[:1])}
    if testlist_hash:
        report["input_testlist_sha256"] = testlist_hash
    xlen = int(args.isa[2:4])
    python = sys.executable
    environment = os.environ.copy()
    environment["PATH"] = str(Path(python).parent) + os.pathsep + environment.get("PATH", "")
    custom_target = (stage_user_target(output, settings=input_target_bytes,
                                       isa=args.isa, target=target,
                                       load_store=misaligned)
                     if input_target_bytes is not None else
                     stage_rv32imc_zbb_target(output) if zbb else
                     stage_rv64i_target(output) if args.isa == "rv64i" else
                     stage_rv64ima_target(output) if atomic else
                     stage_rv64imfdc_target(output) if floating else None)
    if custom_target:
        environment["PYTHONPATH"] = (custom_target["path"] + os.pathsep +
                                     environment.get("PYTHONPATH", ""))
        report["pyflow_target"] = custom_target
    compatibility = (stage_pyflow_compat(output)
                     if args.load_store or args.profile == "riscv_unaligned_load_store_test"
                     else stage_lrsc_compat(output) if lrsc
                     else stage_amo_compat(output, count=amo_count) if amo
                     else None)
    if compatibility:
        environment["PYTHONPATH"] = (compatibility["path"] + os.pathsep +
                                     environment.get("PYTHONPATH", ""))
        report["pyflow_compatibility"] = compatibility
    # The selected upstream profile or vetted custom entry is copied per seed.
    opts = re.sub(r"\+instr_cnt=\d+", "", profile.get("gen_opts", ""))
    profile_limitations = []
    if args.profile == "riscv_rand_instr_test":
        # Several upstream directed streams are not registered in PyFlow.
        # Keep the upstream jump stream. Load/store is optional because this
        # PyFlow revision can emit misaligned accesses despite its default.
        if testlist_hash is None:
            opts = re.sub(r"\+directed_instr_\d+=[^\s]+", "", opts)
            opts += " +num_of_sub_program=0 +directed_instr_0=riscv_jal_instr,1"
            if args.load_store:
                opts += " +directed_instr_1=riscv_load_store_rand_instr_stream,1"
        elif "+num_of_sub_program=0" not in opts:
            opts += " +num_of_sub_program=0"
        if floating:
            opts += " +enable_floating_point=1 +no_directed_instr=1 +no_load_store=1"
            profile_limitations.append("RV64IMFDC random profile excludes directed and load/store streams pending F/D and A stream validation")
        if args.load_store:
            profile_limitations.append("ProcessorCI stages isolated pinned PyFlow load/store compatibility fixes")
        profile_limitations.append("PyFlow uses vetted directed streams; unsupported upstream stress streams are excluded")
    elif args.profile == "riscv_arithmetic_basic_test" and floating:
        opts = re.sub(r"\+directed_instr_\d+=[^\s]+", "", opts)
        opts += " +enable_floating_point=1 +no_directed_instr=1 +no_load_store=1"
        profile_limitations.append("RV64IMFDC arithmetic profile excludes directed and load/store streams pending separate F/D stream validation")
    elif args.profile == "riscv_arithmetic_basic_test" and zbb:
        opts = re.sub(r"\+directed_instr_\d+=[^\s]+", "", opts)
        opts += " +enable_b_extension=1 +no_directed_instr=1 +no_load_store=1 +no_branch_jump=1"
        profile_limitations.append("Only 12 ratified Zbb mnemonics are enabled from pinned draft RV32B; directed and load/store streams are excluded")
    elif args.profile == "riscv_jump_stress_test":
        # This pinned PyFlow revision lacks callstack_gen for subprograms.
        opts = re.sub(r"\+num_of_sub_program=\d+", "+num_of_sub_program=0", opts)
        if "+num_of_sub_program=0" not in opts:
            opts += " +num_of_sub_program=0"
        profile_limitations.append("PyFlow subprogram call-stack generation is unavailable; subprogram count forced to zero")
        if floating:
            opts += " +enable_floating_point=1 +no_load_store=1 +no_branch_jump=1"
            profile_limitations.append("RV64IMFDC jump profile keeps the upstream directed jump stream and excludes random branches and load/store streams")
    elif args.profile == "riscv_unaligned_load_store_test":
        # Keep the two registered upstream load/store streams. PyFlow's
        # factory lacks the multi-page and memory-region stress streams.
        if testlist_hash is None:
            opts = re.sub(r"\+directed_instr_[23]=[^\s]+", "", opts)
        opts = re.sub(r"\+num_of_sub_program=\d+", "+num_of_sub_program=0", opts)
        if "+num_of_sub_program=0" not in opts:
            opts += " +num_of_sub_program=0"
        if "+enable_unaligned_load_store=1" not in opts:
            opts += " +enable_unaligned_load_store=1"
        opts += " +disable_compressed_instr=1"
        profile_limitations.append("PyFlow lacks upstream multi-page and memory-region stress streams; subprograms disabled")
        profile_limitations.append("ProcessorCI stages isolated pinned PyFlow load/store compatibility fixes")
        profile_limitations.append("Compressed instruction generation disabled for this PyFlow load/store profile")
    elif lrsc:
        profile_limitations.extend([
            "One adjacent LR/SC pair on aligned RAM; no other generated memory operations",
            "Single-hart completion allows either SC success or failure; SC destination is not a fixed signature",
            "ProcessorCI stages isolated pinned LR/SC PyFlow fixes and relocates the pair before completion",
        ])
    elif amo:
        profile_limitations.extend([
            f"{amo_count} aligned AMOs on single-hart RAM; no other generated memory operations",
            "ProcessorCI stages isolated pinned AMO PyFlow fixes and relocates the operations before completion",
        ])
    opts += (f" +instr_cnt={args.instr_count} +bare_program_mode=1"
             " +no_csr_instr=1 +no_ebreak=1 +no_wfi=1")
    if args.single_hart_no_csr:
        opts += " +no_fence=1"
        profile_limitations.append("Single-hart startup substitutes zero for upstream mhartid and excludes CSR/fence instructions")
    if args.isa in ("rv32im", "rv64im") and args.profile != "riscv_unaligned_load_store_test":
        opts += " +disable_compressed_instr=1"
    opts += " " + " ".join(args.upstream_option)
    opts = " ".join(opts.split())
    if args.isa in {"rv64i", "rv64ima"}:
        # Pinned run.py appends its own --disable_compressed_instr for ISA
        # strings without C and omits a separator before the appended option.
        opts += " "
    selected = {"test": args.profile, "gen_test": profile["gen_test"],
                "iterations": 1, "gen_opts": opts}
    for offset in range(args.tests):
        seed = args.seed + offset
        name = f"{args.profile}-{args.isa}-{seed}"
        directory = output / name
        directory.mkdir(exist_ok=True)
        row = {"test_id": name, "seed": seed, "status": "failed"}
        reproduce = [python, "-m", "riscv_test_runner.cli", "--tool", "riscv-dv",
                     "--isa", args.isa, "--profile", args.profile, "--tests", "1",
                     "--seed", str(seed), "--instr-count", str(args.instr_count),
                     "--spike", args.spike, "--memory-base", hex(args.memory_base),
                     "--memory-size", hex(args.memory_size), "--reset-pc", hex(args.reset_pc),
                     "--memory-signature-limit", str(args.memory_signature_limit),
                     "--max-cycles", str(args.max_cycles),
                     "--generator-timeout", str(args.generator_timeout),
                     "--backend", args.backend, "--target", target, "--output", str(output)]
        if args.toolchain_prefix:
            reproduce += ["--toolchain-prefix", args.toolchain_prefix]
        if args.load_store:
            reproduce.append("--load-store")
        if args.reference_coverage:
            reproduce.append("--reference-coverage")
        if args.experimental_profile:
            reproduce.append("--experimental-profile")
        if args.single_hart_no_csr:
            reproduce.append("--single-hart-no-csr")
        if args.data_base is not None:
            reproduce += ["--data-base", hex(args.data_base)]
        if args.testlist is not None:
            reproduce += ["--testlist", str(directory / "input-testlist.yaml")]
        if args.target_settings is not None:
            reproduce += ["--target-settings", str(directory / "input-target.py")]
        for option in args.upstream_option:
            reproduce += ["--upstream-option", option]
        row["reproduction_command"] = shlex.join(reproduce)
        report["results"].append(row)
        started = time.monotonic()
        try:
            if input_testlist_bytes is not None:
                (directory / "input-testlist.yaml").write_bytes(input_testlist_bytes)
            if input_target_bytes is not None:
                (directory / "input-target.py").write_bytes(input_target_bytes)
            if atomic:
                stem = "lrsc" if lrsc else "amo-pair" if amo_count == 2 else "amo-triple" if amo_count == 3 else "amo"
                shutil.copy2(Path(custom_target["path"]) / f"pygen_src/target/{target}/riscv_core_setting.py",
                             directory / "target-settings.py")
                shutil.copy2(Path(compatibility["path"]) / "pygen_src/riscv_amo_instr_lib.py",
                             directory / f"{stem}-generator.py")
                shutil.copy2(Path(compatibility["path"]) / "pygen_src/isa/riscv_instr.py",
                             directory / f"{stem}-instruction-factory.py")
            if zbb:
                shutil.copy2(Path(custom_target["path"]) /
                             "pygen_src/target/rv32imcb/riscv_core_setting.py",
                             directory / "target-settings.py")
            testlist = directory / "testlist.yaml"
            testlist.write_text(yaml.safe_dump([selected], sort_keys=False))
            # Pinned run.py detects C with a substring search on --isa and
            # appends an unconverted plusarg for plain rv64i. Keep its
            # generation spelling; the ELF is still compiled for the exact
            # CSR-free ISA selected above.
            generator_isa = (f"{args.isa}_zicsr_zifencei"
                             if custom_target and args.single_hart_no_csr else required_isa)
            command([python, str(UPSTREAM / "run.py"), "--target", target,
                     *(["--custom_target", str(Path(custom_target["path"]) / f"pygen_src/target/{target}")]
                       if custom_target else []),
                     *(["--isa", generator_isa, "--mabi", abi] if custom_target else []),
                     "--testlist", str(testlist), "--test", args.profile,
                     "--simulator", "pyflow", "--steps", "gen", "--iterations", "1",
                     "--seed", str(seed), "--output", str(directory / "upstream")],
                    cwd=UPSTREAM, env=environment, timeout=args.generator_timeout,
                    log=directory / "generation.log")
            source = directory / "upstream/asm_test" / f"{args.profile}_0.S"
            if not source.is_file():
                raise RuntimeError("PyFlow produced no assembly")
            source_copy = directory / "generated.S"
            shutil.copy2(source, source_copy)
            upstream_source_hash = None
            atomic_sc_register: int | None = None
            amo_operation: str | None = None
            amo_operations: list[str] | None = None
            if atomic:
                upstream_source = directory / "upstream-generated.S"
                shutil.copy2(source_copy, upstream_source)
                upstream_source_hash = hashlib.sha256(upstream_source.read_bytes()).hexdigest()
                if lrsc:
                    adapted, atomic_sc_register = relocate_lrsc_to_done(source_copy.read_text())
                elif amo_count >= 2:
                    adapted, amo_operations = relocate_amo_stream_to_done(source_copy.read_text(), count=amo_count)
                else:
                    adapted, amo_operation = relocate_amo_to_done(source_copy.read_text())
                    amo_operations = [amo_operation]
                source_copy.write_text(adapted)
            if args.single_hart_no_csr:
                upstream_source = directory / "upstream-generated.S"
                shutil.copy2(source_copy, upstream_source)
                upstream_source_hash = hashlib.sha256(upstream_source.read_bytes()).hexdigest()
                adapted, substitutions = re.subn(
                    r"(?m)^([ \t]*)csrr[ \t]+x5,[ \t]*0xf14[ \t]*$",
                    r"\1li x5, 0", source_copy.read_text(), count=1)
                if substitutions != 1 or re.search(
                        r"(?mi)^[ \t]*(?:csrr?\w*|mret|sret|wfi|fence(?:\.i)?)(?:[ \t]|$)",
                        adapted):
                    raise RuntimeError("CSR-free startup requires exactly one mhartid read and no privileged or fence instructions")
                source_copy.write_text(adapted)
            if floating:
                (directory / "user_init.s").write_text("li t0, 0x6000\ncsrs mstatus, t0\n")
            report["generated"] += 1
            row["status"] = "generated"
            # The upstream runtime is retained. Only the linker address is configured.
            linker = directory / "link.ld"
            linker_text = (UPSTREAM / "scripts/link.ld").read_text().replace(
                "0x80000000", f"0x{args.reset_pc:x}", 1)
            tohost_marker = "  . = ALIGN(0x1000);\n  .tohost"
            if args.data_base is not None:
                linker_text = linker_text.replace(
                    tohost_marker, f"  . = 0x{args.data_base:x};\n  .tohost", 1)
                tohost_marker = f"  . = 0x{args.data_base:x};\n  .tohost"
            linker.write_text(linker_text)
            def compile_asm(assembly: Path, elf: Path) -> None:
                command([prefix + "gcc", "-static", "-mcmodel=medany", "-fvisibility=hidden",
                         "-nostdlib", "-nostartfiles", "-Wl,--no-relax", "-Wl,--build-id=none",
                         "-I", str(directory), "-I", str(UPSTREAM / "user_extension"),
                         "-T", str(linker),
                         f"-march={required_isa}", f"-mabi={abi}",
                         str(assembly), "-o", str(elf)], timeout=60)
            raw_elf = directory / "reference.elf"
            compile_asm(source_copy, raw_elf)
            report["compiled"] += 1
            row["status"] = "compiled"
            budget = max(3000, args.instr_count * 20)
            checked_source = directory / "checked.S"
            original_text = source_copy.read_text()
            scratch = int(re.findall(r"\bla\s+x(\d+),\s*test_done\b", original_text)[0])
            elf = directory / "program.elf"
            fixed_tohost_base: int | None = None
            for layout_attempt in range(3):
                raw_entry, raw_segments = elf_segments(raw_elf)
                if raw_entry != args.reset_pc:
                    raise RuntimeError(f"linked entry {raw_entry:#x} differs from reset PC {args.reset_pc:#x}")
                for segment in raw_segments:
                    start = segment["address"]
                    end = start + segment["memory_size"]
                    if start < args.memory_base or end > args.memory_base + args.memory_size:
                        raise RuntimeError(f"raw ELF LOAD segment [{start:#x}, {end:#x}) exceeds selected memory")
                if args.data_base is not None:
                    check_split_segments(raw_segments, memory_base=args.memory_base,
                                         data_base=args.data_base,
                                         memory_end=args.memory_base + args.memory_size)
                expected, written = trace_reference(raw_elf, spike=args.spike,
                                                    isa=args.isa, nm=prefix + "nm",
                                                    budget=budget,
                                                    trace=directory / "reference.trace",
                                                    misaligned=misaligned,
                                                    memory_base=args.memory_base,
                                                    memory_size=args.memory_size)
                jump_count = (reference_jump_count(
                    directory / "reference.trace", entry=args.reset_pc,
                    done=symbol(raw_elf, prefix + "nm", "test_done"))
                    if floating and args.profile == "riscv_jump_stress_test" else None)
                if jump_count is not None and jump_count < 1:
                    raise RuntimeError("RV64IMFDC jump profile executed no jump before completion")
                zbb_count = (reference_instruction_count(
                    directory / "reference.trace", entry=args.reset_pc,
                    done=symbol(raw_elf, prefix + "nm", "test_done"), names=ZBB_NAMES)
                    if zbb else None)
                if zbb_count is not None and zbb_count < 1:
                    raise RuntimeError("RV32IMC_Zbb profile executed no Zbb instruction before completion")
                if lrsc:
                    if len(written) not in {0, 4, 8}:
                        raise RuntimeError("LR/SC reference wrote unexpected memory bytes")
                    raw_bytes = {segment["address"] + i: byte
                                 for segment in raw_segments
                                 for i, byte in enumerate(bytes.fromhex(segment["hex"]) +
                                                          bytes(segment["memory_size"] - segment["file_size"]))}
                    if any(raw_bytes.get(address) != value for address, value in written.items()):
                        raise RuntimeError("LR/SC success would change RAM; no fixed memory oracle is valid")
                floating_signature = (floating_state_at_done(
                    directory / "reference.trace",
                    done=symbol(raw_elf, prefix + "nm", "test_done")) if floating else None)
                memory_signature = select_memory_signature(
                    written, limit=args.memory_signature_limit)
                checked_source.write_text(instrument(original_text, expected, xlen,
                                                     memory_signature,
                                                     floating_signature,
                                                     {atomic_sc_register} if lrsc else None))
                compile_asm(checked_source, elf)
                raw_tohost = symbol(raw_elf, prefix + "nm", "tohost")
                checked_tohost = symbol(elf, prefix + "nm", "tohost")
                if raw_tohost == checked_tohost:
                    break
                if layout_attempt == 2:
                    raise RuntimeError("raw and checked ELF data layouts did not stabilize")
                # Checks can push .text across a page boundary. Fix the
                # following data layout, then obtain a fresh Spike reference.
                fixed_tohost_base = (max(raw_tohost, checked_tohost) + 0x1000) & ~0xfff
                if fixed_tohost_base >= args.memory_base + args.memory_size:
                    raise RuntimeError("no room for stable raw/checked ELF data layout")
                linker.write_text(linker_text.replace(
                    tohost_marker,
                    f"  . = 0x{fixed_tohost_base:x};\n  .tohost", 1))
                compile_asm(source_copy, raw_elf)
            trace_reference(elf, spike=args.spike, isa=args.isa, nm=prefix + "nm",
                            budget=budget + 300, trace=directory / "checked.trace",
                            misaligned=misaligned,
                            memory_base=args.memory_base,
                            memory_size=args.memory_size)
            reference_accesses = (reference_memory_accesses(
                directory / "reference.trace", entry=args.reset_pc,
                done=symbol(raw_elf, prefix + "nm", "test_done"))
                if args.profile == "riscv_unaligned_load_store_test" or atomic else None)
            if lrsc and (reference_accesses["loads"] != 1 or
                           reference_accesses["stores"] not in {0, 1}):
                raise RuntimeError("LR/SC reference executed unexpected memory operations")
            if amo and (reference_accesses["loads"] != 0 or
                        reference_accesses["stores"] != len(amo_operations) or
                        len(written) != max(4 if operation.endswith(".w") else 8
                                            for operation in amo_operations)):
                raise RuntimeError("AMO reference did not execute the expected atomic stores")
            report["spike_validated"] += 1
            row["status"] = "spike_validated"
            coverage_record = None
            if args.reference_coverage:
                coverage_record = collect_reference_coverage(
                    directory, raw_elf=raw_elf, nm=prefix + "nm", target=target,
                    python=python, environment=environment)
                report["reference_coverage_validated"] += 1
                row["reference_coverage"] = coverage_record
            entry, segments = elf_segments(elf)
            if args.data_base is not None:
                check_split_segments(segments, memory_base=args.memory_base,
                                     data_base=args.data_base,
                                     memory_end=args.memory_base + args.memory_size)
            tohost = symbol(elf, prefix + "nm", "tohost")
            package = {"schema_version": 1, "test_source": "riscv-dv", "test_id": name,
                       "isa": required_isa, "entry": entry, "segments": segments,
                       "oracle": {"type": "selfcheck_tohost", "address": tohost,
                                  "pass_value": 1, "failure_rule": "odd value greater than 1"},
                       "completion": {"type": "tohost_write", "max_cycles": args.max_cycles},
                       "linker_layout": {"mode": ("fixed_tohost" if fixed_tohost_base is not None
                                                  else "upstream_aligned"),
                                         "tohost_base": f"0x{tohost:x}"},
                       "memory_layout": ({"mode": "split_disjoint",
                                          "instruction_base": args.memory_base,
                                          "instruction_size": args.data_base - args.memory_base,
                                          "data_base": args.data_base,
                                          "data_size": args.memory_base + args.memory_size - args.data_base}
                                         if args.data_base is not None else
                                         {"mode": "shared_flat", "base": args.memory_base,
                                          "size": args.memory_size}),
                       "register_signature": {f"x{i}": f"0x{expected[i]:x}" for i in range(1, 32)
                                              if i != scratch and i != atomic_sc_register},
                       **({"floating_signature": {"registers": {f"f{i}": f"0x{value:016x}"
                                                                   for i, value in enumerate(floating_signature[0])},
                                                  "fcsr": f"0x{floating_signature[1]:x}"}}
                          if floating_signature else {}),
                       "memory_signature": {f"0x{address:x}": f"0x{value:02x}"
                                            for address, value in memory_signature.items()},
                       "memory_signature_total_written_bytes": len(written),
                       "memory_signature_limit": args.memory_signature_limit,
                       **({"atomic_outcome": {"sc_destination": f"x{atomic_sc_register}",
                                               "spike_sc_success": reference_accesses["stores"] == 1,
                                               "permitted_sc_results": ["zero on success", "nonzero on failure"],
                                               "permitted_memory_effect": "unchanged RAM"}}
                          if lrsc else
                          {"atomic_outcome": {**({"operations": amo_operations} if amo_count >= 2 else
                                                {"operation": amo_operation}),
                                              "single_hart_deterministic": True}}
                          if amo else {}),
                       "signature_policy": (f"Spike-derived GPRs"
                                            f"{', 32 FPRs and fcsr' if floating else ''}, "
                                            f"and up to {args.memory_signature_limit} written memory bytes "
                                            f"at test_done; x{scratch} is upstream jump scratch"
                                            + (f"; x{atomic_sc_register} holds permitted SC success/failure, "
                                               "and the SC data equals the LR value so both outcomes leave RAM unchanged"
                                               if lrsc else "")),
                       "generation": {"profile": args.profile, "seed": seed, "backend": "pyflow",
                                      "instruction_count": args.instr_count, "target": target,
                                      "options": opts.split(),
                                      "profile_limitations": profile_limitations,
                                      **({"input_testlist_sha256": testlist_hash}
                                         if testlist_hash is not None else {}),
                                      **({"input_target_sha256": custom_target["settings_sha256"]}
                                         if input_target_bytes is not None else {}),
                                      **({"floating_startup_sha256": hashlib.sha256(
                                          (directory / "user_init.s").read_bytes()).hexdigest()}
                                         if floating else {}),
                                      **({"pyflow_target": {key: value for key, value in custom_target.items()
                                                          if key != "path"}}
                                         if custom_target else {}),
                                      **({"pyflow_compatibility": {key: value for key, value in compatibility.items()
                                                                   if key != "path"}}
                                         if compatibility else {})},
                       "core_requirements": {"machine_mode": not args.single_hart_no_csr,
                                             "zicsr": not args.single_hart_no_csr,
                                             "zifencei": not args.single_hart_no_csr,
                                             "single_hart": args.single_hart_no_csr or atomic,
                                             "mhartid": not args.single_hart_no_csr,
                                             "memory_base": args.memory_base,
                                             "memory_size": args.memory_size,
                                             "split_memory": args.data_base is not None,
                                             "reset_pc": args.reset_pc,
                                             "misaligned_load_store": misaligned,
                                             "floating_point_state": floating,
                                             "zbb": zbb,
                                             "atomic": atomic},
                       "provenance": {"upstream": "https://github.com/chipsalliance/riscv-dv",
                                      "revision": revision,
                                      "assembly_sha256": hashlib.sha256(source_copy.read_bytes()).hexdigest(),
                                      **({"upstream_assembly_sha256": upstream_source_hash}
                                         if upstream_source_hash else {}),
                                      "elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest()},
                       "reference_model": "Spike", "reference_validated": True,
                       **({"reference_jump_instructions": jump_count}
                          if jump_count is not None else {}),
                       **({"reference_zbb_instructions": zbb_count}
                          if zbb_count is not None else {}),
                       **({"reference_memory_accesses": reference_accesses}
                          if reference_accesses else {}),
                       **({"reference_coverage": coverage_record} if coverage_record else {}),
                       "hardware_execution": "pending"}
            reasons = flat_memory_fit(package, base=args.memory_base,
                                      size=args.memory_size, reset_pc=args.reset_pc,
                                      supported_isa={required_isa})
            if reasons:
                raise RuntimeError("package does not fit selected memory: " + "; ".join(reasons))
            initial = initial_memory(package, supported_isa={required_isa})
            if any(initial[tohost + i] for i in range(8)):
                raise RuntimeError("tohost is nonzero before execution")
            image(segments, directory / "imem.hex", True)
            image(segments, directory / "dmem.hex", False)
            package["provenance"]["imem_sha256"] = hashlib.sha256((directory / "imem.hex").read_bytes()).hexdigest()
            package["provenance"]["dmem_sha256"] = hashlib.sha256((directory / "dmem.hex").read_bytes()).hexdigest()
            manifest = directory / "manifest.json"
            manifest.write_text(json.dumps(package, indent=2) + "\n")
            package, manifest_sha256 = verify_saved_package(directory)
            row["manifest_sha256"] = manifest_sha256
            report["package_validated"] += 1
            observed = dict(initial)
            observed[tohost] = 3
            if outcome(package, observed, stopped=True) != "SELF_CHECK_FAILURE":
                raise RuntimeError("host oracle did not reject failing status")
            used_end = max(segment["address"] + segment["memory_size"] for segment in segments)
            mock_size = (used_end - args.memory_base + 3) & ~3
            mock_result = run_package(HostMock(), package, supported_isa={required_isa},
                                      memory_base=args.memory_base, memory_size=mock_size,
                                      reset_pc=args.reset_pc)
            if mock_result["outcome"] != "PASS":
                raise RuntimeError(f"serial host mock rejected package: {mock_result['outcome']}")
            report["host_mock_validated"] += 1
            row.update(status="host_mock_validated", manifest=str(manifest),
                       elf_sha256=package["provenance"]["elf_sha256"],
                       **({"reference_jump_instructions": jump_count}
                          if jump_count is not None else {}),
                       **({"reference_zbb_instructions": zbb_count}
                          if zbb_count is not None else {}),
                       **({"reference_memory_accesses": reference_accesses}
                          if reference_accesses else {}))
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired,
                subprocess.CalledProcessError) as exc:
            row["error"] = str(exc)
            if isinstance(exc, ReferenceTrap):
                row["reference_exception"] = {"cause": exc.cause,
                                              "epc": f"0x{exc.epc:x}"}
            row["failed_stage"] = row["status"]
            row["status"] = "failed"
        row["seconds"] = round(time.monotonic() - started, 3)
        write_reports(output, report)
        if "error" in row and args.stop_on_error:
            break
    return report


def run_matrix(args: argparse.Namespace) -> dict:
    """Run named configuration rows and retain failures without dropping seeds."""
    matrix = json.loads(args.matrix.read_text())
    if not isinstance(matrix, dict) or not isinstance(matrix.get("configurations"), list):
        raise ValueError("matrix must contain a configurations list")
    configs = matrix["configurations"]
    if not configs or len(configs) > 128:
        raise ValueError("matrix must contain 1 to 128 configurations")
    names: set[str] = set()
    for config in configs:
        if (not isinstance(config, dict) or not isinstance(config.get("name"), str)
                or not MATRIX_NAME.fullmatch(config["name"])):
            raise ValueError("each matrix configuration needs a safe name")
        name = config["name"]
        if name in names:
            raise ValueError(f"duplicate matrix configuration name: {name}")
        names.add(name)
        unknown = set(config) - MATRIX_FIELDS - {"name"}
        if unknown:
            raise ValueError(f"unknown matrix fields for {name}: {', '.join(sorted(unknown))}")
        if "upstream_option" in config and (not isinstance(config["upstream_option"], list)
                                             or not all(isinstance(x, str) for x in config["upstream_option"])):
            raise ValueError(f"{name}: upstream_option must be a list of strings")
        for field in ("isa", "profile", "backend", "spike"):
            if field in config and not isinstance(config[field], str):
                raise ValueError(f"{name}: {field} must be a string")
        for field in ("target", "toolchain_prefix", "testlist", "target_settings", "csr_map"):
            if field in config and config[field] is not None and not isinstance(config[field], str):
                raise ValueError(f"{name}: {field} must be a string or null")
        for field in ("tests", "seed", "instr_count", "memory_base", "memory_size", "reset_pc",
                      "data_base",
                      "max_cycles", "generator_timeout", "memory_signature_limit"):
            if field in config and (not isinstance(config[field], int)
                                    or isinstance(config[field], bool)):
                raise ValueError(f"{name}: {field} must be an integer")
        for field in ("load_store", "stop_on_error", "reference_coverage",
                      "experimental_profile", "single_hart_no_csr"):
            if field in config and not isinstance(config[field], bool):
                raise ValueError(f"{name}: {field} must be a boolean")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    aggregate = {"tool": "riscv-dv-matrix", "matrix": str(args.matrix.resolve()),
                 "configurations": len(configs), "requested": 0,
                 "generated": 0, "compiled": 0, "spike_validated": 0,
                 "package_validated": 0, "host_mock_validated": 0,
                 "reference_coverage_validated": 0,
                 "hardware_validated": 0, "results": []}
    for config in configs:
        name = config["name"]
        selected = argparse.Namespace(**{**vars(args), **{key: value for key, value in config.items()
                                                   if key != "name"}, "matrix": None,
                                          "output": output / name})
        if selected.testlist is not None:
            selected.testlist = Path(selected.testlist)
        if selected.target_settings is not None:
            selected.target_settings = Path(selected.target_settings)
        if selected.csr_map is not None:
            selected.csr_map = Path(selected.csr_map)
        row = {"test_id": name, "configuration": config, "status": "unsupported",
               "report": str(selected.output / "report.json")}
        aggregate["results"].append(row)
        aggregate["requested"] += max(0, selected.tests)
        try:
            result = generate(selected)
        except (ValueError, OSError) as exc:
            row["error"] = str(exc)
        else:
            for key in ("generated", "compiled", "spike_validated", "package_validated",
                        "host_mock_validated", "reference_coverage_validated",
                        "hardware_validated"):
                aggregate[key] += result.get(key, 0)
            row["status"] = ("passed" if result["failed"] == 0 and
                             result["package_validated"] == result["requested"] else "failed")
            row["generated"] = result["generated"]
            row["package_validated"] = result["package_validated"]
            if row["status"] == "failed":
                row["error"] = (f"{result['package_validated']} of {result['requested']} "
                                f"seeds packaged; {result['failed']} failed; see {row['report']}")
        write_reports(output, aggregate)
    return aggregate


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Spike-validated riscv-dv ProcessorCI packages")
    parser.add_argument("--isa", choices=ISAS, default="rv32i")
    parser.add_argument("--profile", choices=PROFILES, default=PROFILES[0])
    parser.add_argument("--tests", type=int, default=1)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--instr-count", type=int, default=100)
    parser.add_argument("--load-store", action="store_true",
                        help="Include upstream load/store stream; requires a DUT with misaligned access support")
    parser.add_argument("--reference-coverage", action="store_true",
                        help="collect upstream PyFlow coverage from Spike reference execution")
    parser.add_argument("--experimental-profile", action="store_true",
                        help="accepted for historical experimental matrices; current unaligned profile needs no flag")
    parser.add_argument("--output", type=Path, default=ROOT / "build/riscv-dv")
    parser.add_argument("--backend", default="pyflow")
    parser.add_argument("--target", help="Upstream target; must match the validated ISA mapping")
    parser.add_argument("--testlist", type=Path,
                        help="YAML test list with a vetted entry for the selected profile")
    parser.add_argument("--target-settings", type=Path,
                        help="PyFlow riscv_core_setting.py matching the selected ISA and bare single-hart runtime")
    parser.add_argument("--csr-map", type=Path,
                        help="bounded mscratch CSR map for the directed riscv_csr_test profile")
    parser.add_argument("--toolchain-prefix", help="Cross-toolchain prefix, such as riscv32-unknown-elf-")
    parser.add_argument("--spike", default="spike")
    parser.add_argument("--memory-base", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--memory-size", type=lambda value: int(value, 0), default=0x80000)
    parser.add_argument("--data-base", type=lambda value: int(value, 0),
                        help="separate data and tohost region, with a disjoint physical address range")
    parser.add_argument("--single-hart-no-csr", action="store_true",
                        help="replace upstream mhartid read with zero and compile without Zicsr/Zifencei")
    parser.add_argument("--memory-signature-limit", type=int, default=MEMORY_SIGNATURE_LIMIT,
                        help="maximum committed memory bytes checked at test_done (1 to 1024)")
    parser.add_argument("--reset-pc", type=lambda value: int(value, 0), default=0,
                        help="core reset PC within the selected RAM address range")
    parser.add_argument("--max-cycles", type=int, default=100000)
    parser.add_argument("--generator-timeout", type=int, default=180)
    parser.add_argument("--upstream-option", action="append", default=[])
    parser.add_argument("--stop-on-error", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--matrix", type=Path,
                      help="JSON file with named configurations; each runs in its own output directory")
    mode.add_argument("--verify-package", type=Path,
                      help="read-only verification of a saved riscv-dv package directory")
    parser.add_argument("--expected-manifest-sha256",
                        help="expected per-seed report digest for --verify-package")
    args = parser.parse_args(argv)
    if args.expected_manifest_sha256 and not args.verify_package:
        parser.error("--expected-manifest-sha256 requires --verify-package")
    try:
        if args.verify_package:
            package, digest = verify_saved_package(
                args.verify_package, expected_manifest_sha256=args.expected_manifest_sha256)
            print(json.dumps({"test_id": package["test_id"], "isa": package["isa"],
                              "manifest_sha256": digest, "verified": True}, indent=2))
            return
        report = run_matrix(args) if args.matrix else generate(args)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
    if report["failed"] or report["package_validated"] != report["requested"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
