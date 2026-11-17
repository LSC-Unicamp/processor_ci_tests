# Core corpus for riscv-dv validation

The first selected core is CV32E40S. Its ProcessorCI Controller RTL has
executed saved RV32I and RV32IMC packages, including load/store and UART-loaded
cases. [Ibex RTL](../reports/riscv-dv-ibex-controller-rtl.json) has now passed
five additional packages at reset PC `0x80`. No physical FPGA run is claimed.
The current software priority is portability and richer profiles/oracles;
additional device evidence is deferred to later RV-Bench work.

| Priority | Core | Why it adds useful coverage | Package work before a new validation claim |
| --- | --- | --- | --- |
| 1 | [CV32E40S](https://docs.openhwgroup.org/projects/cv32e40s-user-manual/en/latest/intro.html) | Current RV32I/M/C, Zicsr, and Zifencei RTL baseline, with a working Controller harness. | Expand seeds and test the exact memory and exception policy of each new profile. |
| 2 | [Ibex](https://github.com/lowRISC/ibex/blob/master/doc/02_user/configuration.rst) | Independent RV32IMC implementation. A simulation-staged wrapper and Controller stop path passed arithmetic, random, jump, and load/store packages, with seven checked memory bytes in the load/store case. | Extend seed coverage, test a physical implementation, and validate any bit manipulation or PMP profile separately. |
| 3 | [CV64A6_MMU](https://docs.openhwgroup.org/projects/cva6-user-manual/01_cva6_user/Introduction.html) | Adds RV64IMC and machine, supervisor, and user privilege levels. | Add an RTL memory and completion adapter; keep load/store tests aligned because [CVA6 does not support nonaligned memory access](https://docs.openhwgroup.org/projects/cva6-user-manual/01_cva6_user/Programmer_View.html). Privileged profiles need trap and CSR oracles. |
| 4 | [PicoRV32](https://github.com/YosysHQ/picorv32/blob/main/README.md) | Small RV32I design with optional M and C, useful for testing portability across a very different memory interface. | The CSR-free single-hart package path now passes software validation. Confirm the exact configured ISA, memory interface, and completion stop before a core replay claim. |
| 5 | [CVA6 with Ara](https://github.com/pulp-platform/ara) | Candidate for RISC-V Vector 1.0 after scalar RV64 is stable. | First validate an exact vector-capable core configuration, compiler, Spike, and F/V architectural signature. |

This ordering broadens the corpus without treating core capability as proof
that a riscv-dv profile is supported. Each combination still needs actual
generation, compilation, Spike execution, package checking, and core replay.
The RV64IMFDC random, arithmetic, and jump F/D profiles have passed software
validation; an FPU core replay and other F/D configurations remain open.
Bounded RV64IMA LR/SC and one-, two-, and three-AMO profiles, RV32I/RV64I
`mscratch`/`mepc` CSR tests, and filtered RV32IMC_Zbb arithmetic now pass
software validation. Multi-hart A, trap/MMU behavior, V generation, and
other specialized Z profiles remain open in the [integration checklist](riscv-dv-checklist.md).
