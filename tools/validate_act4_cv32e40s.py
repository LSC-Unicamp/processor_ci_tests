"""Directly replay staged ACT 4.1 CV32E40S ELFs with Sail and host oracle."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from build_act4 import LOCAL_SAIL, REVISION, ROOT

sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import initial_memory, outcome


def validate(build: Path, report_path: Path) -> dict:
    summary = json.loads((build / "summary.json").read_text())
    if summary.get("act_revision") != REVISION or summary.get("core") != "RV-Bench CV32E40S":
        raise RuntimeError("unexpected ACT or DUT build summary")
    sail_config = build / "dut_config/sail.json"
    rows = []
    for test in summary["tests"]:
        package = json.loads(Path(test["package"]).read_text())
        if package["test_id"] != Path(test["elf"]).stem:
            raise RuntimeError(f"ELF/package mismatch: {test}")
        run = subprocess.run([str(LOCAL_SAIL), "--config", str(sail_config), test["elf"]],
                             capture_output=True, text=True, timeout=30)
        if run.returncode or "SUCCESS" not in run.stdout:
            raise RuntimeError(f"Sail failed for {package['test_id']}: {run.stdout} {run.stderr}")
        memory = initial_memory(package, supported_isa={"rv32i", "rv32im"})
        status = package["oracle"]["address"]
        if outcome(package, memory, stopped=False) != "INCONCLUSIVE":
            raise RuntimeError(f"unexpected initialized status: {package['test_id']}")
        memory[status] = 1
        if outcome(package, memory, stopped=True) != "PASS":
            raise RuntimeError(f"host PASS classification failed: {package['test_id']}")
        memory[status] = 3
        if outcome(package, memory, stopped=True) != "SELF_CHECK_FAILURE":
            raise RuntimeError(f"host FAIL classification failed: {package['test_id']}")
        rows.append(package["test_id"])
    report = {"act_release": "4.1.0", "core": "RV-Bench CV32E40S",
              "profile": "provisional upstream UDB/Sail with ProcessorCI tohost macros",
              "generated_elfs": len(rows), "direct_sail_passes": len(rows),
              "host_oracle_checks": len(rows),
              "controller_cases": 0, "fpga_cases": 0, "test_ids": rows}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=ROOT / "build/act4-cv32e40s")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/act4-cv32e40s-software.json")
    args = parser.parse_args()
    result = validate(args.build.resolve(), args.report.resolve())
    print(f"CV32E40S ACT 4.1: {result['direct_sail_passes']} Sail passes and host checks")
