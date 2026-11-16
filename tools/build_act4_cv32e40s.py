"""Build ACT 4.1 CV32E40S sample tests with ProcessorCI tohost completion.

The upstream UDB and Sail model remain provisional for the exact RV-Bench
source revision. This builder does not claim DUT execution or certification.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

from act4_package import convert
from build_act4 import LOCAL_SAIL, REVISION, ROOT, UPSTREAM

SOURCE = UPSTREAM / "config/cores/cve4/cv32e40s-rv32imc"
RV_BENCH = ROOT.parent / "RV-Bench"
CORE_REVISION = "9d9cae78b01a11458953133d1173c61933a2ba86"
ACT_MEMORY_BYTES = 512 * 1024
ACT_DIAGNOSTIC_BYTES = 4096
ACT_PROGRAM_BYTES = ACT_MEMORY_BYTES - ACT_DIAGNOSTIC_BYTES

DATA_SECTION = r"""#define RVMODEL_DATA_SECTION \
  .pushsection .tohost,"aw",@progbits; \
  .balign 8; .global tohost; tohost: .dword 0; \
  .balign 8; .global fromhost; fromhost: .dword 0; \
  .popsection"""

HALT_PASS = r"""#define RVMODEL_HALT_PASS \
  li x1, 1 ; \
  la x2, tohost ; \
  sw x1, 0(x2) ; \
  sw zero, 4(x2) ; \
1: j 1b"""

HALT_FAIL = r"""#define RVMODEL_HALT_FAIL \
  li x1, 3 ; \
  la x2, tohost ; \
  sw x1, 0(x2) ; \
  sw zero, 4(x2) ; \
1: j 1b"""


def stage(output: Path) -> Path:
    actual_act = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip()
    actual_core = subprocess.check_output(["git", "-C", str(RV_BENCH / "cores/cv32e40s"), "rev-parse", "HEAD"], text=True).strip()
    if actual_act != REVISION or actual_core != CORE_REVISION:
        raise RuntimeError("ACT or CV32E40S source revision differs from the selected pinned revision")
    config_dir = output / "dut_config"
    config_dir.mkdir(parents=True, exist_ok=True)
    for name in ("cv32e40s-rv32imc.yaml", "sail.json", "link.ld", "rvmodel_macros.h"):
        shutil.copyfile(SOURCE / name, config_dir / name)

    linker = (config_dir / "link.ld").read_text()
    if linker.count("TEST_BASE = 0x00000080;") != 1:
        raise RuntimeError("upstream CV32E40S linker entry changed; review reset mapping")
    if linker.count("RAM_LENGTH = 0x2000000;") != 1:
        raise RuntimeError("upstream CV32E40S RAM length changed; review hardware map")
    linker = linker.replace("TEST_BASE = 0x00000080;", "TEST_BASE = 0x00000000;")
    linker = linker.replace("RAM_LENGTH = 0x2000000;", f"RAM_LENGTH = {ACT_PROGRAM_BYTES:#x};")
    (config_dir / "link.ld").write_text(linker)

    sail_config = (config_dir / "sail.json").read_text()
    main_region = '"base": { "len": 64, "value": "0x0" },\n        "size": { "len": 64, "value": "0x2000000" }'
    if sail_config.count(main_region) != 1:
        raise RuntimeError("upstream Sail main-memory region changed; review hardware map")
    sail_config = sail_config.replace(main_region, main_region.replace("0x2000000", f"{ACT_PROGRAM_BYTES:#x}"))
    (config_dir / "sail.json").write_text(sail_config)

    macros = (config_dir / "rvmodel_macros.h").read_text()
    for pattern, replacement in (
        (r"#define RVMODEL_DATA_SECTION", DATA_SECTION),
        (r"#define RVMODEL_HALT_PASS\s*\\\n.*?(?=\n# Terminate test with a fail indication\.)", HALT_PASS + "\n\n"),
        (r"#define RVMODEL_HALT_FAIL\s*\\\n.*?(?=\n##### IO #####)", HALT_FAIL + "\n\n"),
    ):
        macros, count = re.subn(pattern, lambda _: replacement, macros, count=1, flags=re.S)
        if count != 1:
            raise RuntimeError(f"upstream CV32E40S macro layout changed: {pattern}")
    (config_dir / "rvmodel_macros.h").write_text(macros)
    return config_dir


def build(output: Path, *, extensions: str = "I") -> dict:
    selected = tuple(part.strip().upper() for part in extensions.split(","))
    if not selected or any(part not in {"I", "M"} for part in selected):
        raise ValueError("this CV32E40S bring-up supports I and M ACT sources")
    output = output.resolve()
    config_dir = stage(output)
    gcc = next((name for name in ("riscv64-elf-gcc", "riscv64-unknown-elf-gcc") if shutil.which(name)), None)
    sail = str(LOCAL_SAIL) if LOCAL_SAIL.is_file() else "sail_riscv_sim"
    for executable in (gcc, sail, "bundle", "act"):
        if not executable or not shutil.which(executable):
            raise RuntimeError(f"missing ACT build prerequisite: {executable}")
    objdump = gcc.removesuffix("gcc") + "objdump"
    if not shutil.which(objdump):
        raise RuntimeError(f"missing {objdump}")
    config = config_dir / "test_config.yaml"
    config.write_text("\n".join((
        "name: processorci-cv32e40s-rv32imc",
        f"compiler_exe: {Path(shutil.which(gcc)).resolve()}",
        f"objdump_exe: {Path(shutil.which(objdump)).resolve()}",
        f"ref_model_exe: {Path(shutil.which(sail)).resolve()}",
        f"udb_config: {config_dir / 'cv32e40s-rv32imc.yaml'}",
        f"linker_script: {config_dir / 'link.ld'}",
        f"dut_include_dir: {config_dir}",
    )) + "\n")
    work = output / "upstream_work"
    env = os.environ.copy()
    ruby_home = output / "ruby-gems"
    ruby_home.mkdir(exist_ok=True)
    env["GEM_HOME"] = str(ruby_home)
    shared_bundle = ROOT / "build/act4/bundle"
    env["BUNDLE_PATH"] = str(shared_bundle if shared_bundle.is_dir() else output / "bundle")
    env["BUNDLE_USER_HOME"] = str(output / "bundle-home")
    user_gems = Path.home() / ".local/share/gem/ruby/3.4.0/gems"
    erb_libs = sorted(user_gems.glob("erb-*/lib"))
    if erb_libs:
        env["RUBYLIB"] = os.pathsep.join([str(erb_libs[-1]), env.get("RUBYLIB", "")]).rstrip(os.pathsep)
    command = ["act", str(config), "--test-dir", str(UPSTREAM / "tests"),
               "--coverpoint-dir", str(UPSTREAM / "coverpoints"), "--workdir", str(work),
               "--extensions", ",".join(selected), "--jobs", "2"]
    subprocess.run(command, cwd=UPSTREAM, env=env, check=True)
    elfs = sorted(path for path in work.rglob("*.elf") if "elfs" in path.parts)
    if not elfs:
        raise RuntimeError("ACT generated no CV32E40S ELF files")
    packages = output / "packages"
    packages.mkdir(exist_ok=True)
    counts: Counter[str] = Counter()
    rows = []
    for elf in elfs:
        marker = elf.parts.index("elfs")
        extension = elf.parts[marker + 2]
        if extension not in selected:
            raise RuntimeError(f"unexpected ACT extension: {elf}")
        package = convert(elf, isa="rv32i" + {"I": "", "M": "m"}[extension], revision=REVISION)
        target = packages / (elf.stem + ".json")
        target.write_text(json.dumps(package, indent=2) + "\n")
        counts[extension] += 1
        addresses = [(segment["address"], segment["address"] + segment["memory_size"]) for segment in package["segments"]]
        rows.append({"elf": str(elf), "package": str(target), "extension": extension,
                     "entry": package["entry"], "tohost": package["oracle"]["address"],
                     "load_file_bytes": sum(segment["file_size"] for segment in package["segments"]),
                     "load_span": [min(start for start, _ in addresses), max(end for _, end in addresses)]})
    summary = {"release": "ACT 4.1.0", "act_revision": REVISION,
               "core": "RV-Bench CV32E40S", "core_revision": CORE_REVISION,
               "profile": "provisional upstream CV32E40S UDB/Sail with ProcessorCI tohost and reset-zero linker",
               "extensions": list(selected), "extension_counts": dict(counts),
               "elfs": len(rows), "hardware_execution": "pending", "tests": rows}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/act4-cv32e40s")
    parser.add_argument("--extensions", default="I")
    args = parser.parse_args()
    try:
        result = build(args.output, extensions=args.extensions)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"CV32E40S ACT 4.1: {result['elfs']} ELFs, {result['extension_counts']}")
