"""Exercise ACT4 package loading and result classification without hardware."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import initial_memory, outcome
from build_act4 import SAMPLE_ISAS
from build_basic_sail import SAIL
from riscv_test_runner.core.selection import isa_compatible

DEFAULT_OUTPUT = ROOT / "build" / "act4"
DEFAULT_REPORT = ROOT / "reports" / "act4-summary.json"


def validate(output: Path = DEFAULT_OUTPUT, report_path: Path = DEFAULT_REPORT) -> dict:
    summary_path = output / "summary.json"
    if not summary_path.is_file():
        raise RuntimeError(f"ACT4 build summary missing: {summary_path}")
    summary = json.loads(summary_path.read_text())
    sample = summary.get("sample", "sail-RVI20U32")
    isa = summary.get("isa", SAMPLE_ISAS.get(sample))
    if sample not in SAMPLE_ISAS or isa != SAMPLE_ISAS[sample]:
        raise RuntimeError(f"unsupported ACT4 sample/ISA pair: {sample}/{isa}")
    config = ROOT / "third_party_repositories/riscv-arch-test/config/sail" / sample / "sail.json"
    records = summary["packages"]
    if not records:
        raise RuntimeError("no ACT4 packages built")
    extension_counts = summary.get("extension_counts")
    if extension_counts and sum(extension_counts.values()) != len(records):
        raise RuntimeError("ACT extension counts disagree with built packages")
    if not SAIL.is_file() or not config.is_file():
        raise RuntimeError("Sail 0.13.1 and the ACT 4.1 configuration are required")
    results = []
    for record in records:
        path, elf = Path(record["package"]), Path(record["elf"])
        if path.parent != (output / "packages").resolve():
            raise RuntimeError(f"ACT package outside selected output: {path}")
        if not path.is_file():
            raise RuntimeError(f"missing ACT package: {path}")
        package = json.loads(path.read_text())
        if not isa_compatible(package["isa"], isa):
            raise RuntimeError(f"ACT package ISA mismatch: {path}")
        if not elf.is_file():
            raise RuntimeError(f"missing ACT ELF: {elf}")
        run = subprocess.run([str(SAIL), "--config", str(config), str(elf)],
                             capture_output=True, text=True, timeout=30)
        if run.returncode or "RVCP-SUMMARY: TEST PASSED" not in run.stdout or "SUCCESS" not in run.stdout:
            raise RuntimeError(f"ACT Sail execution failed for {path.stem}: {run.stdout} {run.stderr}")
        memory = initial_memory(package, supported_isa={isa})
        initial = outcome(package, memory, stopped=False)
        address = package["oracle"]["address"]
        memory[address] = 1
        passed = outcome(package, memory, stopped=True)
        memory[address] = 3
        failed = outcome(package, memory, stopped=True)
        timeout = outcome(package, memory, stopped=True, timed_out=True)
        if (initial, passed, failed, timeout) != ("INCONCLUSIVE", "PASS", "SELF_CHECK_FAILURE", "TIMEOUT"):
            raise RuntimeError(f"host oracle mismatch: {path.name}")
        results.append(package["test_id"])
    report = {"act_release": "4.1.0", "sample": sample, "isa": isa,
              "extension_counts": extension_counts or {"I": len(results)},
              "generated_elfs": len(results),
              "converted_packages": len(results), "sail_validated": len(results),
              "host_mock_validated": len(results),
              "hardware_validated": 0, "test_ids": results}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    result = validate(args.output.resolve(), args.report)
    print(f"ACT 4.1: {result['sail_validated']} Sail executions, {result['host_mock_validated']} host checks")
