# Named Z extensions and vector coverage

The legacy `RV32B`, `RV32P` and `RV32V` directories and configuration entries
have been removed. Bitmanip and integer-vector tests live under named Z groups.

| Group | Basis | Dedicated Sail cases | Coverage limit |
|---|---|---:|---|
| RV32Zba | B 1.0 address generation | 3 | Full RV32 mnemonic set |
| RV32Zbb | B 1.0 basic bitmanip | 18 | Full RV32 mnemonic set |
| RV32Zbs | B 1.0 single-bit | 8 | Full RV32 mnemonic set |
| RV32Zbc | Optional carry-less multiply | 3 | Full RV32 mnemonic set |
| RV32Zbkb | Scalar crypto bitmanip | 5 | Unique RV32 forms; overlapping Zbb forms counted under Zbb |
| RV32Zve32x | V 1.0 integer vector | 259 | All applicable RV32 opcode forms validated for the Zve32x/Zvl128b test profile; parameter combinations sampled |
| RV32Zve64x | V 1.0 integer vector EEW64 | 11 | All additional RV32 forms first enabled by Zve64x validated under Zvl128b; four indexed EEW64 forms require RV64 |
| RV32Zve32f | V 1.0 FP32 vector | 66 | All additional RV32 forms first enabled by Zve32f validated; parameter combinations sampled |
| RV32Zve64f | V 1.0 FP32 to EEW64 | 6 | All additional RV32 forms first enabled by Zve64f validated; parameter combinations sampled |
| RV32Zve64d | V 1.0 FP64 vector | 29 | All additional RV32 forms first enabled by Zve64d validated; parameter combinations sampled |
| RV64Zve64x | V 1.0 indexed EEW64 memory | 4 | Four forms disallowed on RV32 validated under RV64; parameter combinations sampled |

The [ratified bitmanip specification](https://docs.riscv.org/reference/isa/unpriv/b-st-ext.html)
defines B as Zba + Zbb + Zbs. Zbc is separate. The
[scalar crypto specification](https://docs.riscv.org/reference/isa/unpriv/scalar-crypto.html)
defines Zbkb, including the unique `pack`, `packh`, `brev8`, `zip` and `unzip`
forms used here. The [V 1.0 specification](https://docs.riscv.org/reference/isa/unpriv/v-st-ext)
defines Zve32x and Zvl length extensions. Zve32x requires Zicsr and has a
minimum VLEN of 32 bits. These tests choose Zvl128b so four 32-bit elements
fit with LMUL 1. A full V implementation implies Zve32x and Zvl128b.

The standard V subsets form a capability ladder. The five named groups have
complete RV32 opcode-form coverage under the chosen Zvl128b test profile.
Vector state and parameter combinations remain sampled.

| Vector subset | Minimum VLEN | Additional capability |
|---|---:|---|
| Zve32x | 32 bits | Integer EEW up to 32; requires Zicsr |
| Zve32f | 32 bits | FP32 vectors; requires Zve32x and F |
| Zve64x | 64 bits | Integer EEW up to 64; requires Zve32x |
| Zve64f | 64 bits | FP32 vectors; requires Zve32f, Zve64x and F |
| Zve64d | 64 bits | FP64 vectors; requires Zve64f and D |

The package selector expands these dependencies and the implied shorter Zvl
lengths when comparing a package against a core's advertised ISA. It does not
turn the 259 Zve32x cases into coverage of the higher subsets; the separate
higher-group cases provide that evidence.

The pinned [RISC-V V opcode catalog](https://github.com/riscv/riscv-opcodes/blob/f24ac23ec9fa947011781a09cd6fd25a7c36dc45/extensions/rv_v)
contains 375 opcode forms. `reports/isa-audit/vector_opcode_candidates.json`
classifies 259 as applicable to RV32Zve32x and records all 259 as independently
Sail-validated. The other 116 comprise 101 vector FP forms, 13 EEW64 memory
forms, and two extension forms that need SEW64 to keep their source EEW at
least 8. All 112 forms applicable to RV32 now have Sail-validated cases across
the higher Zve groups; four indexed EEW64 forms are validated under RV64.

The full-V opcode catalog breaks down as follows. The audit records
each form's minimum Zve subset and XLEN: Zve32f 66, Zve64x 15, Zve64f 6,
and Zve64d 29. Four indexed EEW64 memory forms require RV64.

| Opcode family | Catalog forms | Tested forms | Unselected forms |
|---|---:|---:|---:|
| Configuration | 3 | 3 | 0 |
| Loads and stores | 58 | 58 | 0 |
| Integer, mask, fixed point, permutation | 213 | 213 | 0 |
| Floating point | 101 | 101 | 0 |

For a real full V 1.0 core, coverage must still be matched to its verified
hardware profile. V requires Zve64d, Zvl128b, F and D. The current cases
use selected legal SEW 8/16/32/64 settings and VL 2/4, including widening,
narrowing, mask, fixed point, memory, FP32, FP64 and configuration forms.
Some forms encode additional variants, including segmented
memory operations through `nf`, which need explicit test parameter choices.
The architecture excludes EEW64 indexed memory forms when XLEN is 32.

The 259-case result is per-opcode-form basic coverage, not exhaustive vector
state or parameter coverage. Further scenarios should vary VLEN, LMUL, SEW,
VL, masks, tail policy, `vstart`, `vxsat`/`vxrm`, FP flags, segmented and
faulting memory operations, and traps.
Advanced scenarios now check mask-undisturbed lanes and `vstart` CSR
write/read/reset. A nonzero-`vstart` vector-operation resume passed QEMU but
trapped in the current Sail RV32 max configuration, so it remains an open
cross-model check.
The e8 saturation scenario checks `vxsat`, and the FP32 reciprocal estimate
basic cases check the architected DZ flag for zero input.
Software passes can be recorded under Sail and QEMU; hardware coverage still
requires a selected core and a working ProcessorCI execution adapter.

The vector package `march` also includes M because the installed GCC currently
rejects this Zve32x build without M; M is a toolchain constraint for these
packages, not a dependency of the Zve32x ISA. The tests execute with the
upstream Sail `sail-rv32-max` reference configuration (VLEN 1024), using VL 4
and checking a defined architectural result. Whole-register cases reserve
enough memory for the maximum standard VLEN of 65536 bits. The packages record
the minimum VLEN and chosen SEW/LMUL. Cores with only Zve32x's minimum
VLEN 32 require retargeted tests because these packages require Zvl128b.
An advanced vector load/add/store interaction checks two initialized lanes
under QEMU and Sail; it uses VL 2 with the same Zve32x/Zvl128b profile.

The removed V folder used older names `vcompress.m` and `vpopc.m`; current
cases use `vcompress.vm` and `vcpop.m`. Each generated ELF is disassembled to
confirm its target encoding.

The current [P proposal](https://github.com/riscv/riscv-p-spec/blob/master/P-ext-proposal.adoc)
is a developing v0.6 draft. It depends on Zmmul, Zba and Zbb, but its packed
instructions are not thereby reassigned to those Z extensions. The P profile
is excluded from the configured suite while its specification remains a draft.

Rebuild and audit the selected Z cases with:

```sh
python3 tools/build_basic_sail.py
python3 tools/isa_audit.py --compile
python3 tools/combined_report.py
pytest -q validation_tests/test_phase1.py
```

`tools/extension_profiles.py` derives the RV32Zve32x inventory from the pinned
V opcode catalog. `tools/extension_cases.py` and `tools/vector_cases.py` hold
the expected-value cases. The audit reveals any applicable opcode form without
a validated case.
