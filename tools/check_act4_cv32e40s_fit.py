"""Check staged CV32E40S ACT packages against the current controller RAM."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_dut_package_fit import ROOT, board_memory_bytes
from build_act4_cv32e40s import ACT_DIAGNOSTIC_BYTES

CONTROLLER_DATA_BYTES = 4096  # processor_ci_controller/rtl/controller.sv


def check(build: Path, board: str, output: Path, *, shared_memory_bytes: int | None = None) -> dict:
    summary = json.loads((build / "summary.json").read_text())
    if shared_memory_bytes is not None and (shared_memory_bytes <= ACT_DIAGNOSTIC_BYTES or shared_memory_bytes % 4):
        raise ValueError("shared memory must exceed the diagnostic window and be word aligned")
    primary = (shared_memory_bytes - ACT_DIAGNOSTIC_BYTES if shared_memory_bytes is not None else
               board_memory_bytes(board, ROOT.parent / "processor_ci"))
    data = 0 if shared_memory_bytes is not None else CONTROLLER_DATA_BYTES
    rows = []
    for test in summary["tests"]:
        package = json.loads(Path(test["package"]).read_text())
        status = package["oracle"]["address"]
        load_file = sum(segment["file_size"] for segment in package["segments"])
        high = max(segment["address"] + segment["memory_size"] for segment in package["segments"])
        reasons = []
        if load_file > primary + data:
            reasons.append(f"{load_file} initialized bytes exceed {primary + data} total controller bytes")
        if high > primary:
            bank = "shared" if shared_memory_bytes is not None else "primary"
            reasons.append(f"instruction-visible ELF span ends at {high:#x}, beyond {primary:#x} {bank} RAM")
        if shared_memory_bytes is not None:
            if status + 8 > primary:
                reasons.append(f"tohost at {status:#x} is beyond {primary:#x} shared RAM")
        elif status + 8 > data:
            reasons.append(f"tohost at {status:#x} is beyond {data:#x} data RAM")
        rows.append({"test_id": package["test_id"], "load_file_bytes": load_file,
                     "load_span_high": high, "tohost": status,
                     "fits": not reasons, "reasons": reasons})
    report = {"core": "RV-Bench CV32E40S",
              "board": "shared RTL memory" if shared_memory_bytes is not None else board,
              "memory_mode": "shared" if shared_memory_bytes is not None else "split",
              "physical_memory_bytes": shared_memory_bytes if shared_memory_bytes is not None else None,
              "reserved_diagnostic_bytes": ACT_DIAGNOSTIC_BYTES if shared_memory_bytes is not None else 0,
              "primary_memory_bytes": primary, "data_memory_bytes": data,
              "checked": len(rows), "fit": sum(row["fits"] for row in rows),
              "minimum_load_file_bytes": min(row["load_file_bytes"] for row in rows),
              "minimum_load_span_high": min(row["load_span_high"] for row in rows),
              "tests": rows, "fpga_execution_ready": False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=ROOT / "build/act4-cv32e40s")
    parser.add_argument("--board", default="digilent_nexys4_ddr")
    parser.add_argument("--shared-memory-bytes", type=int,
                        help="check one shared RTL memory instead of the current FPGA board")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/act4-cv32e40s-fit.json")
    args = parser.parse_args()
    result = check(args.build.resolve(), args.board, args.output.resolve(),
                   shared_memory_bytes=args.shared_memory_bytes)
    print(f"CV32E40S ACT fit: {result['fit']}/{result['checked']} on {result['board']}")
