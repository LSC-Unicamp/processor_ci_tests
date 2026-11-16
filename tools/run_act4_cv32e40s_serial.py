"""Select ACT 4.1 CV32E40S packages for the 512 KiB ProcessorCI UART target."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from build_act4_cv32e40s import ACT_DIAGNOSTIC_BYTES, ACT_MEMORY_BYTES, ACT_PROGRAM_BYTES, ROOT

sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import flat_memory_fit
from riscv_test_runner.core.serial_package import run_package

ISA = {"rv32i", "rv32im"}
DIAGNOSTIC_BASE = ACT_PROGRAM_BYTES


def select(paths: list[Path]) -> list[tuple[Path, dict]]:
    selected = []
    for path in paths:
        package = json.loads(path.read_text())
        if package.get("test_source") != "ACT4":
            raise ValueError(f"{path} is not an ACT package")
        reasons = flat_memory_fit(package, base=0, size=ACT_PROGRAM_BYTES,
                                  reset_pc=0, supported_isa=ISA)
        if reasons:
            raise ValueError(f"{path.name} does not fit CV32E40S: {'; '.join(reasons)}")
        selected.append((path, package))
    if not selected:
        raise ValueError("no ACT packages selected")
    return selected


def execute(selected: list[tuple[Path, dict]], *, port: str, baudrate: int,
            expected_id: bytes | None, host_timeout: float) -> list[dict]:
    sys.path.insert(0, str(ROOT.parent))
    from processor_ci_communication.core.serial import ProcessorCIInterface

    device = ProcessorCIInterface(port, baudrate, 5)
    try:
        observed_id = device.get_module_id()
        if expected_id is not None and observed_id != expected_id:
            raise RuntimeError(f"controller ID {observed_id.hex()} differs from {expected_id.hex()}")
        results = []
        for path, package in selected:
            result = run_package(device, package, supported_isa=ISA,
                                 memory_base=0, memory_size=ACT_PROGRAM_BYTES,
                                 reset_pc=0, host_timeout=host_timeout,
                                 diagnostic_base=DIAGNOSTIC_BASE)
            results.append({"test_id": package["test_id"], "package": str(path), **result})
            print(f"{package['test_id']}: {result['outcome']}", flush=True)
        return results
    finally:
        device.close()


def write_report(path: Path, results: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"act_release": "4.1.0", "core": "RV-Bench CV32E40S",
                                "memory_bytes": ACT_MEMORY_BYTES,
                                "program_bytes": ACT_PROGRAM_BYTES,
                                "diagnostic_bytes": ACT_DIAGNOSTIC_BYTES,
                                "device_runs": results}, indent=2) + "\n")
    suite = ET.Element("testsuite", name="act4.cv32e40s.device", tests=str(len(results)),
                       failures=str(sum(row["outcome"] != "PASS" for row in results)))
    for row in results:
        case = ET.SubElement(suite, "testcase", name=row["test_id"])
        if row["outcome"] != "PASS":
            failure = ET.SubElement(case, "failure", message=row["outcome"])
            failure.text = (row.get("diagnostics") or {}).get("text") or row["outcome"]
    ET.indent(suite)
    ET.ElementTree(suite).write(path.with_suffix(".junit.xml"), encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="validate package fit without a device")
    parser.add_argument("--port", help="serial device path; required for execution")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--expected-id", help="optional four-byte controller ID as eight hex digits")
    parser.add_argument("--host-timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/act4-cv32e40s-device.json")
    args = parser.parse_args()
    if args.all and args.package:
        parser.error("choose --all or --package")
    paths = (sorted((ROOT / "build/act4-cv32e40s/packages").glob("*.json")) if args.all else
             args.package or [ROOT / "build/act4-cv32e40s/packages/I-addi-00.json"])
    selected = select([path.resolve() for path in paths])
    if args.dry_run:
        print(f"{len(selected)} ACT packages fit the {ACT_PROGRAM_BYTES}-byte program RAM")
        raise SystemExit(0)
    if not args.port:
        parser.error("--port is required unless --dry-run is selected")
    if args.expected_id and (len(args.expected_id) != 8 or any(ch not in "0123456789abcdefABCDEF" for ch in args.expected_id)):
        parser.error("--expected-id must be eight hex digits")
    write_report(args.output.resolve(), execute(selected, port=args.port, baudrate=args.baudrate,
                                                 expected_id=bytes.fromhex(args.expected_id) if args.expected_id else None,
                                                 host_timeout=args.host_timeout))
