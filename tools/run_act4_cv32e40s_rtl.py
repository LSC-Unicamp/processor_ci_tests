"""Execute one real ACT 4.1 ELF through RV-Bench's CV32E40S wrapper in RTL.

The simulation memory is larger than ProcessorCI's controller RAM. This is
core/wrapper execution evidence, not a controller or FPGA result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

from build_act4_cv32e40s import ROOT, RV_BENCH as BENCH

CONFIG = BENCH / "config/cores/cv32e40s.json"
CORE = BENCH / "cores/cv32e40s"
INTERNAL = BENCH / "tools/wrappers/internal"
WRAPPER = BENCH / "overlay/cv32e40s/wrappers/cv32e40s.sv"

sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import initial_memory, outcome

MEMORY_BYTES = 512 * 1024

COHERENT_MEMORY = r"""
  logic [31:0] shared_words [0:131071];
  initial $readmemh("processor_ci_connector/internal/memory.hex", shared_words);
  assign core_data_in = (core_cyc && core_stb && !core_we) ? shared_words[core_addr[18:2]] : 32'b0;
  assign core_ack = core_cyc && core_stb;
  assign data_mem_data_in = (data_mem_cyc && data_mem_stb && !data_mem_we) ?
      shared_words[data_mem_addr[18:2]] : 32'b0;
  assign data_mem_ack = data_mem_cyc && data_mem_stb;
  always_ff @(posedge clk) begin
    if (data_mem_cyc && data_mem_stb && data_mem_we) begin
      if (data_mem_sel[0]) shared_words[data_mem_addr[18:2]][7:0] <= data_mem_data_out[7:0];
      if (data_mem_sel[1]) shared_words[data_mem_addr[18:2]][15:8] <= data_mem_data_out[15:8];
      if (data_mem_sel[2]) shared_words[data_mem_addr[18:2]][23:16] <= data_mem_data_out[23:16];
      if (data_mem_sel[3]) shared_words[data_mem_addr[18:2]][31:24] <= data_mem_data_out[31:24];
    end
  end
"""

MAIN_CPP = r"""
#include <verilated.h>
#include "Vverification_top.h"
#include <cstdio>
#include <cstdlib>
int main(int argc, char **argv) {
  Verilated::commandArgs(argc, argv);
  Vverification_top top;
  top.clk = 0;
  top.rst_n = 0;
  unsigned instr_count = 0, data_count = 0, last_pc = 0;
  unsigned recent_if[16] = {};
  unsigned recent_data[16] = {};
  for (int cycle = 0; cycle < 2000000; ++cycle) {
    top.clk = !top.clk;
    if (cycle == 10) top.rst_n = 1;
    top.eval();
    if (top.clk && top.rst_n && top.instr_req_mon) {
      last_pc = top.instr_addr_mon;
      recent_if[instr_count % 16] = last_pc;
      if (instr_count < 15) std::printf("IF:%08X,%d\n", last_pc, cycle);
      ++instr_count;
    }
    if (top.clk && top.rst_n && top.cyc && top.stb) {
      recent_data[data_count % 16] = top.addr;
      if (data_count < 15) std::printf("DATA:%c,%08X,%08X,%d\n",
        top.we ? 'W' : 'R', top.addr, top.data_out, cycle);
      ++data_count;
    }
    if (top.clk && top.rst_n && top.cyc && top.stb && top.we && top.addr == TARGET_ADDR) {
      std::printf("0x%08X,0x%08X,%d\n", top.addr, top.data_out, cycle);
      return 0;
    }
  }
  std::printf("RESULT:TIMEOUT IF=%u DATA=%u LAST_PC=%08X\n", instr_count, data_count, last_pc);
  std::printf("CORE_PC=%08X\n", top.core_pc_mon);
  std::printf("RECENT_IF:");
  for (int i = 0; i < 16; ++i) std::printf(" %08X", recent_if[(instr_count + i) % 16]);
  std::puts("");
  std::printf("RECENT_DATA:");
  for (int i = 0; i < 16; ++i) std::printf(" %08X", recent_data[(data_count + i) % 16]);
  std::puts("");
  return 0;
}
"""


def run(package_path: Path, *, output: Path, coherent_memory: bool = False,
        inject_addi_failure: bool = False) -> dict:
    package = json.loads(package_path.read_text())
    if package["test_source"] != "ACT4" or package["entry"] != 0:
        raise ValueError("expected reset-zero CV32E40S ACT package")
    memory = initial_memory(package, supported_isa={"rv32i", "rv32im"})
    expected_status = 1
    if inject_addi_failure:
        if package["test_id"] != "I-addi-00":
            raise ValueError("the directed mutation is defined only for ACT I-addi-00")
        address = 0x88
        original = int.from_bytes(bytes(memory[address + offset] for offset in range(4)), "little")
        if original != 0x2FC00413:
            raise RuntimeError(f"ACT I-addi-00 first check changed: {original:#x}")
        mutated = (0x2FD00413).to_bytes(4, "little")
        for offset, byte in enumerate(mutated):
            memory[address + offset] = byte
        expected_status = 3
    high = max(memory) + 1
    status_addr = package["oracle"]["address"]
    if high > MEMORY_BYTES or status_addr + 8 > MEMORY_BYTES:
        raise ValueError(f"ACT package needs {high} bytes; simulation memory is {MEMORY_BYTES}")
    words = [int.from_bytes(bytes(memory.get(address + offset, 0) for offset in range(4)), "little")
             for address in range(0, MEMORY_BYTES, 4)]
    with tempfile.TemporaryDirectory(prefix="cv32e40s-act4-rtl-") as temp:
        work = Path(temp)
        internal = work / "internal"
        shutil.copytree(INTERNAL, internal)
        (internal / "memory.hex").write_text("".join(f"{word:08x}\n" for word in words))
        top = (internal / "verification_top.sv").read_text()
        if coherent_memory:
            marker = "// Instância da primeira memória"
            if top.count(marker) != 1:
                raise RuntimeError("RV-Bench memory instantiation changed")
            top = top.split(marker)[0] + COHERENT_MEMORY + "\nendmodule\n"
        else:
            if top.count(".MEMORY_SIZE (4096)") != 2:
                raise RuntimeError("RV-Bench wrapper simulation memory layout changed")
            top = top.replace(".MEMORY_SIZE (4096)", f".MEMORY_SIZE ({MEMORY_BYTES})")
            if top.count('.MEMORY_FILE ("")') != 1:
                raise RuntimeError("RV-Bench second memory initialization changed")
            top = top.replace('.MEMORY_FILE ("")', '.MEMORY_FILE ("processor_ci_connector/internal/memory.hex")')
        if top.count("output logic [31:0] data_in") != 1:
            raise RuntimeError("RV-Bench wrapper simulation top changed")
        top = top.replace("output logic [31:0] data_in", "output logic [31:0] data_in,\n    output logic instr_req_mon,\n    output logic [31:0] instr_addr_mon,\n    output logic [31:0] core_pc_mon")
        top = top.replace("endmodule", "assign instr_req_mon = core_cyc && core_stb;\nassign instr_addr_mon = core_addr;\nassign core_pc_mon = ptop.Processor.pc_if;\nendmodule")
        (internal / "verification_top.sv").write_text(top)
        (internal / "soc_main.cpp").write_text(MAIN_CPP.replace("TARGET_ADDR", str(status_addr)))
        package_module = types.ModuleType("core")
        package_module.__path__ = [str(BENCH / "tools/wrappers/core")]
        package_module.BUILD_DIR = str(work / "build")
        package_module.INTERNAL_DIR = str(internal)
        sys.modules["core"] = package_module
        sys.path.insert(0, str(BENCH / "tools/wrappers"))
        from core import hdl_process
        hdl_process.EXPECTED_SIGNATURE = (status_addr, expected_status)

        config = json.loads(CONFIG.read_text())
        files = [str(CORE / name) for name in (config.get("sim_files") or config["files"])]
        include = [f"-I{CORE}"] + [f"-I{CORE / name}" for name in config["include_dirs"]]
        result = hdl_process.validate_wrapper_simulation(
            "cv32e40s", files, include, wrapper_path=WRAPPER, config_path=CONFIG,
            second_memory=True, build_dir=work / "build", simulation_cycles=2000000,
            timeout=300)
    observed = None
    for line in result["stdout_tail"].splitlines():
        fields = line.split(",")
        if len(fields) == 3 and fields[0] == f"0x{status_addr:08X}":
            observed = int(fields[1], 16)
    classified = "INCONCLUSIVE"
    if observed is not None:
        observed_memory = dict(memory)
        for offset, byte in enumerate(observed.to_bytes(4, "little")):
            observed_memory[status_addr + offset] = byte
        classified = outcome(package, observed_memory, stopped=True)
    report = {"test_id": package["test_id"], "package": str(package_path),
              "core": "RV-Bench CV32E40S", "wrapper": str(WRAPPER.relative_to(BENCH)),
              "wrapper_sha256": hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
              "coherent_simulation_memory": coherent_memory,
              "simulation_memory_bytes_per_bus": MEMORY_BYTES,
              "load_high_address": high, "tohost_address": status_addr,
              "tohost_observed": observed,
              "tohost_expected": expected_status,
              "classified_outcome": classified,
              "injected_addi_fault": inject_addi_failure,
              "rtl_result": result["status"], "stage": result["stage"],
              "reason": result["reason"], "stdout_tail": result["stdout_tail"],
              "stderr_tail": result["stderr_tail"],
              "controller_execution": False, "fpga_execution": False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    if observed != expected_status or result["status"] != "pass":
        raise RuntimeError(f"ACT RTL execution did not report expected status: {report}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path,
                        default=ROOT / "build/act4-cv32e40s/packages/I-addi-00.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/act4-cv32e40s-rtl-addi.json")
    parser.add_argument("--coherent-memory", action="store_true",
                        help="use one shared instruction/data memory in the private simulation harness")
    parser.add_argument("--inject-addi-failure", action="store_true",
                        help="mutate ACT I-addi-00 after reference generation to require self-check FAIL")
    args = parser.parse_args()
    if args.inject_addi_failure and args.output == ROOT / "reports/act4-cv32e40s-rtl-addi.json":
        args.output = ROOT / "reports/act4-cv32e40s-rtl-addi-induced-fail.json"
    result = run(args.package.resolve(), output=args.output.resolve(),
                 coherent_memory=args.coherent_memory,
                 inject_addi_failure=args.inject_addi_failure)
    print(f"{result['test_id']}: RTL tohost={result['tohost_observed']} after {result['load_high_address']} bytes")
