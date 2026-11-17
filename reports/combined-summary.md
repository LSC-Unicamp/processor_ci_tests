# ProcessorCI software verification summary

Counts come from the basic inventory and execution reports. ACT host checks are separate from ISA coverage.

- Basic ISA: 602 inventoried; 599 ordinary Sail validated; 3 exceptional encodings Sail validated.
- Vector inventory scope: 371/371 applicable RV32 full-V opcode forms and 4/4 RV64-only forms validated across named Zve groups; parameter combinations are sampled.
- Vector VLEN128 replay: 375 basic and 14 advanced cases passed full-V and matching named-Zve Sail configurations; DUT validation pending.
- Nonzero-vstart arithmetic: QEMU and a permissive Sail profile resumed successfully; the pinned strict Sail profile traps by configuration. This is a conditional probe, outside the advanced PASS count.
- Invalid suite: 19 Sail validated, including 16 operations outside the basic inventory.
- Trap self-check status: 3=EXPECTED_TRAP_MISSING, 5=UNEXPECTED_TRAP, 7=ARCHITECTURAL_MISMATCH.
- Advanced: 59 scenarios passed QEMU and Sail.
- ACT 4.1.0: 39 ELFs, 39 packages, 39 Sail executions, 39 host checks in the recorded build; DUT runs pending.
- ACT 4.1.0 RV64 I: 51 ELFs, 51 packages, 51 Sail executions, 51 host checks; DUT runs pending.
- ACT 4.1.0 RV32 I/M/C software request: 47 ELFs, 47 Sail executions, 47 host checks; I=39, M=8, C=0. This is a software sample, not the selected DUT run.
- RV-Bench CV32E40S ACT candidate: 47 I/M ELFs passed Sail and host checks; 47 passed core/controller RTL, 47 passed full UART segment loading and execution; serial negatives self_check_failure, timeout, unexpected_trap; shared 512 KiB fit 47/47; source/profile audit current; ACT DUT scope I/M only, C=0 upstream test sources; legacy board profile fit 0/47; FPGA synthesis and execution pending.
- ACT package artifacts available in this checkout: yes.
- riscv-dv: integration absent from this checkout.
- FPGA: execution pending.

## Basic ISA by group

| Group | Inventoried | Ordinary Sail | Expected trap | Packages |
|---|---:|---:|---:|---:|
| RV32A | 11 | 11 | 0 | 11 |
| RV32C | 35 | 34 | 1 | 34 |
| RV32D | 26 | 26 | 0 | 26 |
| RV32F | 26 | 26 | 0 | 26 |
| RV32I | 40 | 38 | 2 | 38 |
| RV32M | 8 | 8 | 0 | 8 |
| RV32Zba | 3 | 3 | 0 | 3 |
| RV32Zbb | 18 | 18 | 0 | 18 |
| RV32Zbc | 3 | 3 | 0 | 3 |
| RV32Zbkb | 5 | 5 | 0 | 5 |
| RV32Zbs | 8 | 8 | 0 | 8 |
| RV32Zicsr | 6 | 6 | 0 | 6 |
| RV32Zve32f | 66 | 66 | 0 | 66 |
| RV32Zve32x | 259 | 259 | 0 | 259 |
| RV32Zve64d | 29 | 29 | 0 | 29 |
| RV32Zve64f | 6 | 6 | 0 | 6 |
| RV32Zve64x | 11 | 11 | 0 | 11 |
| RV64A | 11 | 11 | 0 | 11 |
| RV64D | 6 | 6 | 0 | 6 |
| RV64F | 4 | 4 | 0 | 4 |
| RV64I | 12 | 12 | 0 | 12 |
| RV64M | 5 | 5 | 0 | 5 |
| RV64Zve64x | 4 | 4 | 0 | 4 |

B 1.0 is split into Zba/Zbb/Zbs; Zbc and selected unique Zbkb forms are tracked separately.
Zve32x has 259/259 applicable RV32 opcode forms validated; parameter combinations are sampled.
Zve64x has 11/11 additional RV32 opcode forms validated; four indexed EEW64 forms were validated separately under RV64.
Zve32f has 66/66 additional FP32 opcode forms validated.
Zve64f has 6/6 additional FP32/EEW64 opcode forms validated.
Zve64d has 29/29 additional FP64 opcode forms validated.
RV64Zve64x has 4/4 indexed EEW64 forms validated separately.
P is excluded from the configured suite while its specification is a developing draft.

## Pinned V opcode-form catalog

All pinned forms have dedicated Sail-validated cases across RV32 and RV64 software profiles; core-specific hardware coverage remains pending.

| Family | Catalog | Selected | Unselected |
|---|---:|---:|---:|
| configuration | 3 | 3 | 0 |
| memory | 58 | 58 | 0 |
| integer mask fixed point permutation | 213 | 213 | 0 |
| floating point | 101 | 101 | 0 |

Minimum Zve profile for an applicable opcode form: Zve32x 259, Zve32f 66, Zve64x 15, Zve64f 6, Zve64d 29. The four EEW64 indexed memory forms were validated under RV64.
