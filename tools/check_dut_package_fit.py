"""Static ACT package compatibility check for a ProcessorCI core and board."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import InvalidPackage, flat_memory_fit


def board_memory_bytes(board: str, processor_ci: Path) -> int:
    definitions = processor_ci / "core/board_defines.py"
    spec = importlib.util.spec_from_file_location("processorci_board_defines", definitions)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot read board definitions: {definitions}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if board not in module.DEFINES_BY_BOARD:
        raise ValueError(f"unknown board: {board}")
    match = re.search(r"^`define MEMORY_SIZE (\d+)$", module.DEFINES_BY_BOARD[board], re.M)
    if not match:
        raise ValueError(f"board {board} has no memory size")
    return int(match[1])


def check(core: str, board: str, packages: Path, *, processor_ci: Path,
          base: int, reset_pc: int) -> dict:
    config = json.loads((processor_ci / "config" / f"{core}.json").read_text())
    size = board_memory_bytes(board, processor_ci)
    paths = sorted(packages.glob("*.json"))
    if not paths:
        raise ValueError(f"no packages in {packages}")
    results = []
    for path in paths:
        package = json.loads(path.read_text())
        try:
            reasons = flat_memory_fit(package, base=base, size=size, reset_pc=reset_pc,
                                      supported_isa={config["march"]})
            file_bytes = sum(segment["file_size"] for segment in package["segments"])
            memory_bytes = sum(segment["memory_size"] for segment in package["segments"])
        except InvalidPackage as exc:
            reasons = [str(exc)]
            file_bytes = memory_bytes = None
        label = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        results.append({"package": label,
                        "load_file_bytes": file_bytes, "load_memory_bytes": memory_bytes,
                        "fits": not reasons, "reasons": reasons})
    return {"core": core, "board": board, "advertised_isa": config["march"],
            "memory_base": base, "memory_bytes": size, "reset_pc": reset_pc,
            "checked": len(results), "fit": sum(row["fits"] for row in results),
            "smallest_load_file_bytes": min((row["load_file_bytes"] for row in results if row["load_file_bytes"] is not None), default=None),
            "smallest_load_memory_bytes": min((row["load_memory_bytes"] for row in results if row["load_memory_bytes"] is not None), default=None),
            "hardware_validated": False, "results": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", default="picorv32")
    parser.add_argument("--board", default="digilent_nexys4_ddr")
    parser.add_argument("--packages", type=Path, default=ROOT / "build/act4/packages")
    parser.add_argument("--processor-ci", type=Path, default=ROOT.parent / "processor_ci")
    parser.add_argument("--base", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--reset-pc", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/act4-picorv32-nexys4-fit.json")
    args = parser.parse_args()
    result = check(args.core, args.board, args.packages, processor_ci=args.processor_ci,
                   base=args.base, reset_pc=args.reset_pc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"ACT package fit: {result['fit']}/{result['checked']} packages fit {args.core} on {args.board}")
