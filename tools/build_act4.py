"""Build ACT 4.1 self-checking I tests with an official Sail software config.

The sample Sail DUT configuration is a software integration target, not an
assertion about any ProcessorCI FPGA core's implemented capabilities.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from collections import Counter
from pathlib import Path

from act4_package import convert

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "third_party_repositories" / "riscv-arch-test"
REVISION = "6e8a45123f14cebfb3df151a0e7b849b4389b33b"
DEFAULT_CONFIG = UPSTREAM / "config" / "sail" / "sail-RVI20U32" / "test_config.yaml"
SAMPLE_ISAS = {"sail-RVI20U32": "rv32i", "sail-RVI20U64": "rv64i",
               "sail-rv32-max": "rv32imc"}
LOCAL_SAIL = Path.home() / ".local" / "processorci-sail-0.13.1" / "bin" / "sail_riscv_sim"


def build(*, config: Path, output: Path, act_exe: str = "act", gcc: str | None = None,
          sail_exe: str | None = None, extensions: str = "I") -> dict:
    actual = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip()
    if actual != REVISION:
        raise RuntimeError(f"ACT checkout {actual} differs from pinned 4.1.0 revision {REVISION}")
    gcc = gcc or next((name for name in ("riscv64-unknown-elf-gcc", "riscv64-elf-gcc", "riscv64-linux-gnu-gcc") if shutil.which(name)), "riscv64-unknown-elf-gcc")
    sail_exe = sail_exe or (str(LOCAL_SAIL) if LOCAL_SAIL.is_file() else "sail_riscv_sim")
    objdump = gcc.removesuffix("gcc") + "objdump"
    missing = [exe for exe in (act_exe, sail_exe, gcc, objdump) if not shutil.which(exe)]
    if not shutil.which("bundle"):
        missing.append("bundle")
    if missing:
        raise RuntimeError("ACT 4.1 build prerequisites missing: " + ", ".join(missing))
    act_exe = str(Path(shutil.which(act_exe)).resolve())
    if not config.is_file():
        raise FileNotFoundError(config)
    sample = config.resolve().parent
    if config.name != "test_config.yaml" or sample.name not in SAMPLE_ISAS or sample.parent != (UPSTREAM / "config/sail").resolve():
        raise ValueError("only the official ACT 4.1 Sail RVI20U32/U64 or RV32 max sample configs are supported")
    isa = SAMPLE_ISAS[sample.name]
    selected = tuple(part.strip().upper() for part in extensions.split(","))
    if not selected or any(part not in {"I", "M", "C"} for part in selected):
        raise ValueError("this software build currently supports only I, M, C ACT extensions")
    if sample.name != "sail-rv32-max" and selected != ("I",):
        raise ValueError("I/M/C builds require the official Sail RV32 max software sample")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Keep the official sample UDB, memory map and macros together. Only tool
    # paths change in this generated config; upstream sources stay untouched.
    generated = output / "test_config.yaml"
    keys = {
        "compiler_exe": str(Path(shutil.which(gcc)).resolve()),
        "objdump_exe": str(Path(shutil.which(objdump)).resolve()),
        "ref_model_exe": str(Path(shutil.which(sail_exe)).resolve()),
        "udb_config": str(sample / f"{sample.name}.yaml"),
        "linker_script": str(sample / "link.ld"),
        "dut_include_dir": str(sample),
    }
    lines = [f"{key}: {keys[key]}" if key in keys else line for line in config.read_text().splitlines() for key in [line.split(":", 1)[0]]]
    generated.write_text("\n".join(lines) + "\n")
    work = output / "upstream_work"
    ruby_home = output / "ruby-gems"
    ruby_home.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["GEM_HOME"] = str(ruby_home.resolve())
    shared_bundle = ROOT / "build/act4/bundle"
    env["BUNDLE_PATH"] = str(shared_bundle if shared_bundle.is_dir() else output / "bundle")
    env["BUNDLE_USER_HOME"] = str((output / "bundle-home").resolve())
    # Arch splits ERB from Ruby. A user-installed erb gem can be supplied via
    # RUBYLIB when the ruby-erb system package is unavailable.
    user_gems = Path.home() / ".local" / "share" / "gem" / "ruby" / "3.4.0" / "gems"
    erb_libs = sorted(user_gems.glob("erb-*/lib"))
    if erb_libs:
        env["RUBYLIB"] = os.pathsep.join([str(erb_libs[-1]), env.get("RUBYLIB", "")]).rstrip(os.pathsep)
    command = [act_exe, str(generated), "--test-dir", str(UPSTREAM / "tests"),
               "--coverpoint-dir", str(UPSTREAM / "coverpoints"), "--workdir", str(work),
               "--extensions", ",".join(selected), "--jobs", "2"]
    subprocess.run(command, cwd=UPSTREAM, env=env, check=True)
    elfs = sorted(p for p in work.rglob("*.elf") if "elfs" in p.parts)
    if not elfs:
        raise RuntimeError("ACT 4.1 produced no ELF files")
    packages = output / "packages"
    packages.mkdir(exist_ok=True)
    converted = []
    seen_ids = set()
    extension_counts: Counter[str] = Counter()
    for elf in elfs:
        marker = elf.parts.index("elfs")
        isa_dir = elf.parts[marker + 1]
        extension = elf.parts[marker + 2]
        if not isa_dir.startswith("rv32") and not isa_dir.startswith("rv64"):
            raise RuntimeError(f"ACT ELF has no ISA directory: {elf}")
        if extension not in selected:
            raise RuntimeError(f"ACT ELF has unexpected extension directory: {elf}")
        package = convert(elf, isa=isa_dir + {"I": "", "M": "m", "C": "c"}[extension], revision=REVISION)
        target = packages / (elf.stem + ".json")
        if elf.stem in seen_ids:
            raise RuntimeError(f"duplicate ACT test ID: {elf.stem}")
        seen_ids.add(elf.stem)
        extension_counts[extension] += 1
        target.write_text(json.dumps(package, indent=2) + "\n")
        converted.append({"elf": str(elf), "package": str(target)})
    summary = {"release": "4.1.0", "revision": REVISION, "config": str(config),
               "sample": sample.name, "isa": isa, "extensions": selected,
               "extension_counts": {extension: extension_counts[extension] for extension in selected},
               "reference": "ACT4 Sail-generated self-checks", "elfs": len(elfs),
               "converted": len(converted), "packages": converted,
               "hardware_execution": "pending"}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "act4")
    parser.add_argument("--act-exe", default="act")
    parser.add_argument("--gcc", help="RISC-V GCC executable (Arch uses riscv64-elf-gcc)")
    parser.add_argument("--sail-exe", help="Sail 0.13.1 executable")
    parser.add_argument("--extensions", default="I", help="ACT extension list; I,M,C for Sail RV32 max")
    args = parser.parse_args()
    try:
        result = build(config=args.config, output=args.output, act_exe=args.act_exe,
                       gcc=args.gcc, sail_exe=args.sail_exe, extensions=args.extensions)
    except (RuntimeError, FileNotFoundError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"ACT 4.1: {result['elfs']} ELFs, {result['converted']} packages")
