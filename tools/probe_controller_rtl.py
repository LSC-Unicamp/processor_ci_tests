"""Exercise RV-Bench's selected ProcessorCI controller RTL without FPGA hardware."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT.parent / "RV-Bench/tools/controller"


def probe(output: Path = ROOT / "reports/controller-rtl-protocol.json") -> dict:
    if not CONTROLLER.is_dir() or not shutil.which("iverilog") or not shutil.which("verilator"):
        raise RuntimeError("RV-Bench controller checkout, Icarus and Verilator are required")
    rtl = CONTROLLER / "rtl"
    interpreter = rtl / "interpreter.sv"
    controller = rtl / "controller.sv"
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        icarus = temp / "interpreter.vvp"
        subprocess.run(["iverilog", "-g2012", "-s", "interpreter_protocol_tb", "-o", str(icarus),
                        str(interpreter), str(ROOT / "validation_tests/rtl/interpreter_protocol_tb.sv")],
                       check=True, capture_output=True, text=True)
        interpreter_run = subprocess.run(["vvp", str(icarus)], check=True, capture_output=True, text=True)
        if "RTL_PROTOCOL_PASS" not in interpreter_run.stdout:
            raise RuntimeError("interpreter protocol test did not report PASS")
        files = [rtl / name for name in ("controller.sv", "interpreter.sv", "memory.sv", "clk_divider.sv", "timer.sv")]
        for split in (False, True):
            obj = temp / ("obj_split" if split else "obj_flat")
            subprocess.run(["verilator", "--binary", "--timing", "-Wno-fatal",
                            *(["-DENABLE_SECOND_MEMORY"] if split else []),
                            "--top-module", "controller_stop_probe_tb", "--Mdir", str(obj),
                            *(str(path) for path in files),
                            str(ROOT / "validation_tests/rtl/controller_stop_probe_tb.sv")],
                           check=True, capture_output=True, text=True, timeout=120)
            controller_run = subprocess.run([str(obj / "Vcontroller_stop_probe_tb")],
                                            check=True, capture_output=True, text=True)
            expected = "RTL_DATA_WRITE_QUALIFIED_FINISH" if split else "RTL_PRIMARY_WRITE_QUALIFIED_FINISH"
            if expected not in controller_run.stdout:
                raise RuntimeError(f"controller {('split' if split else 'flat')} probe did not verify {expected}")
        shared_obj = temp / "obj_shared"
        subprocess.run(["verilator", "--binary", "--timing", "-Wno-fatal",
                        "-DENABLE_SECOND_MEMORY", "-DENABLE_BYTE_SELECT",
                        "--top-module", "controller_shared_memory_tb", "--Mdir", str(shared_obj),
                        *(str(path) for path in files),
                        str(ROOT / "validation_tests/rtl/controller_stop_probe_tb.sv"),
                        str(ROOT / "validation_tests/rtl/controller_shared_memory_tb.sv")],
                       check=True, capture_output=True, text=True, timeout=120)
        shared_run = subprocess.run([str(shared_obj / "Vcontroller_shared_memory_tb")],
                                    check=True, capture_output=True, text=True)
        if "RTL_SHARED_MEMORY_PASS" not in shared_run.stdout:
            raise RuntimeError("512 KiB shared-memory probe did not report PASS")
    result = {"interpreter_sha256": hashlib.sha256(interpreter.read_bytes()).hexdigest(),
              "controller_sha256": hashlib.sha256(controller.read_bytes()).hexdigest(),
              "interpreter_protocol": "passed",
              "burst_write_read": "passed in RV-Bench interpreter testbench",
              "early_completion": "passed in RV-Bench interpreter testbench",
              "timeout_reply": "passed in RV-Bench interpreter testbench",
              "idle_address_triggers_finish": False,
              "primary_write_qualified_finish": True,
              "data_write_qualified_finish": True,
              "shared_512k_memory": "passed: serial write, byte/halfword stores, cross-port read, bounds, diagnostics",
              "decoded_trap_cause_available": False,
              "act_diagnostic_window_serial_readable": True,
              "fpga_validated": False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    print(probe())
