# Basic ISA audit

Legacy asset presence is separate from Sail-validated package tests. Expected traps are tracked separately.

| Group | Inventory | Source present | Legacy built | Legacy image matches | Legacy reference matches Sail | Package compiled | Sail validated | Expected trap | Missing basic source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RV32A | 11 | 11 | 11 | 11 | 0 | 11 | 11 | 0 | 0 |
| RV32C | 35 | 34 | 20 | 20 | 20 | 34 | 34 | 1 | 1 |
| RV32D | 26 | 26 | 0 | 0 | 0 | 26 | 26 | 0 | 0 |
| RV32F | 26 | 26 | 0 | 0 | 0 | 26 | 26 | 0 | 0 |
| RV32I | 40 | 38 | 37 | 37 | 37 | 38 | 38 | 2 | 2 |
| RV32M | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 0 | 0 |
| RV32Zba | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0 | 0 |
| RV32Zbb | 18 | 18 | 0 | 0 | 0 | 18 | 18 | 0 | 0 |
| RV32Zbc | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0 | 0 |
| RV32Zbkb | 5 | 5 | 0 | 0 | 0 | 5 | 5 | 0 | 0 |
| RV32Zbs | 8 | 8 | 0 | 0 | 0 | 8 | 8 | 0 | 0 |
| RV32Zicsr | 6 | 6 | 0 | 0 | 0 | 6 | 6 | 0 | 0 |
| RV32Zve32f | 66 | 66 | 0 | 0 | 0 | 66 | 66 | 0 | 0 |
| RV32Zve32x | 259 | 259 | 0 | 0 | 0 | 259 | 259 | 0 | 0 |
| RV32Zve64d | 29 | 29 | 0 | 0 | 0 | 29 | 29 | 0 | 0 |
| RV32Zve64f | 6 | 6 | 0 | 0 | 0 | 6 | 6 | 0 | 0 |
| RV32Zve64x | 11 | 11 | 0 | 0 | 0 | 11 | 11 | 0 | 0 |
| RV64A | 11 | 11 | 0 | 0 | 0 | 11 | 11 | 0 | 0 |
| RV64D | 6 | 6 | 0 | 0 | 0 | 6 | 6 | 0 | 0 |
| RV64F | 4 | 4 | 0 | 0 | 0 | 4 | 4 | 0 | 0 |
| RV64I | 12 | 12 | 0 | 0 | 0 | 12 | 12 | 0 | 0 |
| RV64M | 5 | 5 | 0 | 0 | 0 | 5 | 5 | 0 | 0 |
| RV64Zve64x | 4 | 4 | 0 | 0 | 0 | 4 | 4 | 0 | 0 |

## Legacy basic reference audit

Nonempty comment-only hex files are placeholders. Per-source details and Sail replay results are in `legacy_basic_assets.json` and `legacy_basic_sail.json`.

| Sources | With instructions | Numeric memory images | Numeric references | Reference placeholders | Sail reference matches |
|---:|---:|---:|---:|---:|---:|
| 166 | 79 | 79 | 71 | 95 | 67 |

| Legacy group | Sources | Instruction bodies | Numeric memory images | Numeric references | Reference placeholders |
|---|---:|---:|---:|---:|---:|
| RV32A | 11 | 11 | 11 | 0 | 11 |
| RV32C | 20 | 20 | 20 | 20 | 0 |
| RV32D | 20 | 0 | 0 | 0 | 20 |
| RV32F | 20 | 0 | 0 | 0 | 20 |
| RV32I | 43 | 40 | 40 | 43 | 0 |
| RV32M | 8 | 8 | 8 | 8 | 0 |
| RV32Zicsr | 6 | 0 | 0 | 0 | 6 |
| RV64A | 11 | 0 | 0 | 0 | 11 |
| RV64D | 6 | 0 | 0 | 0 | 6 |
| RV64F | 4 | 0 | 0 | 0 | 4 |
| RV64I | 12 | 0 | 0 | 0 | 12 |
| RV64M | 5 | 0 | 0 | 0 | 5 |

## All legacy category assets

| Category | Sources | With instructions | Memory files | Reference files |
|---|---:|---:|---:|---:|
| basic | 166 | 79 | 79 | 166 |
| advanced | 83 | 83 | 83 | 83 |
| invalid | 0 | 0 | 0 | 0 |

The legacy B, P and V profiles were removed. B coverage uses ratified Zba/Zbb/Zbs (B 1.0), optional Zbc and selected unique Zbkb forms.
RV32Zve32x has 259/259 applicable V 1.0 opcode forms Sail-validated at selected legal SEW/VL settings; this does not represent exhaustive vector parameter coverage.
The pinned V opcode catalog has 375 forms; 371/371 RV32 full-V opcode forms have dedicated Sail-validated cases across five named Zve groups. 0 RV32 forms remain untested; 4/4 indexed EEW64 forms were validated under RV64.
P remains outside the configured suite while its specification is a developing draft.
F/D instructions require FP state initialization; C floating instructions depend on F/D.
ECALL, EBREAK and C.EBREAK are validated as expected M-mode traps in the separate invalid suite.
ACT submodule migrated from RISCOF 241b1fe294567751bd3ae6f338b1dbfc40c41a20 to ACT 4.1.0 6e8a45123f14cebfb3df151a0e7b849b4389b33b.
ACT 4.1.0: 39 software-target packages host-mock validated. RV64 I sample: 51 packages host-mock validated. RV32 I/M/C request: 47 packages host-mock validated; extension counts {'I': 39, 'M': 8, 'C': 0}.
Hardware validation: pending.
