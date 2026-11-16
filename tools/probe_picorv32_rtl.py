"""Exercise the ProcessorCI picorv32 wrapper against RV-Bench's pinned RTL.

This is a small RTL capability probe, not an ACT result or FPGA run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CORE = WORKSPACE / "RV-Bench/cores/picorv32"
WRAPPER = WORKSPACE / "processor_ci/rtl/picorv32.sv"

PROGRAMS = {
    "rv32i_add_branch": ("rv32i", """
        .option norvc
        li t0, 2
        addi t0, t0, 3
        li t1, 5
        bne t0, t1, fail
        j pass
    """),
    "rv32m_mul_div": ("rv32im", """
        .option norvc
        li t0, 7
        li t1, 6
        mul t2, t0, t1
        li t3, 42
        bne t2, t3, fail
        div t2, t3, t1
        bne t2, t0, fail
        j pass
    """),
    "rv32c_c_addi": ("rv32ic", """
        .option rvc
        li t0, 1
        c.addi t0, 2
        li t1, 3
        bne t0, t1, fail
        j pass
    """),
    "machine_csr_mstatus": ("rv32i_zicsr", """
        .option norvc
        csrr t0, mstatus
        j pass
    """),
    "machine_csr_mtvec": ("rv32i_zicsr", """
        .option norvc
        csrw mtvec, zero
        j pass
    """),
    "ecall": ("rv32i", """
        .option norvc
        ecall
        j pass
    """),
}

BENCH = r"""
`timescale 1ns/1ps
module tb;
  reg clk = 0;
  always #5 clk = ~clk;
  reg rst_n = 0;
  wire core_cyc, core_stb, core_we;
  wire [3:0] core_wstrb;
  wire [31:0] core_addr, core_data_out;
  reg [31:0] memory [0:2047];
  wire [31:0] core_data_in = memory[core_addr[12:2]];
  wire core_ack = core_cyc && core_addr < 8192;
  integer cycle;
  processorci_top dut (
    .sys_clk(clk), .rst_n(rst_n), .core_cyc(core_cyc),
    .core_stb(core_stb), .core_we(core_we), .core_wstrb(core_wstrb),
    .core_addr(core_addr), .core_data_out(core_data_out),
    .core_data_in(core_data_in), .core_ack(core_ack)
  );
  initial begin
    $readmemh("program.hex", memory);
    repeat (5) @(posedge clk);
    @(negedge clk) rst_n = 1;
    for (cycle = 0; cycle < 2000; cycle = cycle + 1) begin
      @(posedge clk);
      if (dut.cpu.trap) begin
        $display("RESULT TRAP cycle=%0d", cycle);
        $finish;
      end
      if (core_cyc && core_ack && core_we && core_addr == 32'h100) begin
        $display("RESULT STATUS value=%0d cycle=%0d", core_data_out, cycle);
        $finish;
      end
    end
    $display("RESULT TIMEOUT");
    $finish;
  end
endmodule
"""


def run() -> dict:
    for executable in ("iverilog", "vvp", "riscv64-elf-gcc", "riscv64-elf-objcopy", "git"):
        if not shutil.which(executable):
            raise RuntimeError(f"missing {executable}")
    revision = subprocess.check_output(["git", "-C", str(CORE), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(["git", "-C", str(CORE), "status", "--porcelain"], text=True).strip():
        raise RuntimeError("picorv32 source checkout is modified")
    report = {"core": "picorv32", "source_revision": revision,
              "source_sha256": hashlib.sha256((CORE / "picorv32.v").read_bytes()).hexdigest(),
              "wrapper": str(WRAPPER.relative_to(WORKSPACE)),
              "wrapper_sha256": hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
              "memory_model": "8192 bytes at address zero; one-cycle acknowledged bus",
              "cases": {}}
    with tempfile.TemporaryDirectory(prefix="picorv32-probe-") as tmp:
        work = Path(tmp)
        (work / "tb.sv").write_text(BENCH)
        subprocess.run(["iverilog", "-g2012", "-DSIMULATION", "-s", "tb",
                        "-o", str(work / "sim.vvp"), str(work / "tb.sv"),
                        str(WRAPPER), str(CORE / "picorv32.v")],
                       check=True, capture_output=True, text=True)
        for name, (march, body) in PROGRAMS.items():
            assembly = f".globl _start\n_start:\n{body}\npass:\n li a0, 1\n j done\nfail:\n li a0, 3\ndone:\n li t0, 256\n sw a0, 0(t0)\n1: j 1b\n"
            (work / "program.S").write_text(assembly)
            subprocess.run(["riscv64-elf-gcc", "-nostdlib", "-nostartfiles", "-static",
                            "-Wl,--build-id=none", "-Wl,-Ttext=0", "-Wl,--no-relax",
                            "-Wl,-e,_start", f"-march={march}", "-mabi=ilp32",
                            str(work / "program.S"), "-o", str(work / "program.elf")],
                           check=True, capture_output=True, text=True)
            subprocess.run(["riscv64-elf-objcopy", "-O", "binary", str(work / "program.elf"),
                            str(work / "program.bin")], check=True, capture_output=True, text=True)
            binary = (work / "program.bin").read_bytes()
            if len(binary) > 256:
                raise RuntimeError(f"{name} code overlaps status word")
            padded = binary + bytes((-len(binary)) % 4)
            (work / "program.hex").write_text("".join(
                f"{int.from_bytes(padded[i:i+4], 'little'):08x}\n"
                for i in range(0, len(padded), 4)))
            result = subprocess.run(["vvp", str(work / "sim.vvp")], cwd=work,
                                    capture_output=True, text=True, timeout=30, check=True)
            line = next((line for line in result.stdout.splitlines() if line.startswith("RESULT ")), None)
            if line is None:
                raise RuntimeError(f"{name}: missing result: {result.stdout} {result.stderr}")
            expected = "RESULT TRAP" if name.startswith("machine_csr_") or name == "ecall" else "RESULT STATUS value=1"
            if not line.startswith(expected):
                raise RuntimeError(f"{name}: expected {expected!r}, got {line!r}")
            report["cases"][name] = {"march": march, "rtl_result": line}
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/picorv32-rtl-probe.json")
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
