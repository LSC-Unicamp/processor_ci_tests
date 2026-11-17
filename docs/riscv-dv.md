# riscv-dv generation for ProcessorCI Tests

This adapter uses [riscv-dv](https://github.com/chipsalliance/riscv-dv) to generate
random programs. ProcessorCI Tests owns the linker configuration, Spike reference
check, self-checking completion code, sparse package, and host-mock validation.
Generation is separate from later DUT execution. RV-Bench integration is future
work; no RV-Bench code is required here.

Progress and remaining tasks are tracked in the [integration checklist](riscv-dv-checklist.md).
The [pinned upstream and handoff audit](riscv-dv-upstream-audit.md) records
PyFlow feature limits and coverage-probe evidence.

## Setup

The `third_party_repositories/riscv-dv` submodule pins upstream commit
`f557b89ed6881a20515481a2585e9d004cd9642b`. The upstream source is
Apache-2.0 licensed; its own `LICENSE.txt` and source notices remain in the
submodule. Install in an isolated Python 3.11 environment:

```sh
git submodule update --init third_party_repositories/riscv-dv
python3.11 -m venv .venv-riscv-dv
. .venv-riscv-dv/bin/activate
pip install -r requirements-riscv-dv.txt
```

Install a RISC-V bare-metal compiler and `nm`, and Spike with commit logging.
The tested commands were `riscv32-unknown-elf-gcc` 16.1.0,
`riscv64-elf-gcc`, and Spike 1.1.1-dev. `--toolchain-prefix` selects another
matching compiler and `nm`; `--spike` selects the reference executable.

## Generate and validate

Run from this repository. The command below creates one RV32I package at reset
PC 0 with a 512 KiB shared RAM assumption:

```sh
python -m riscv_test_runner.cli --tool riscv-dv \
  --isa rv32i --profile riscv_arithmetic_basic_test \
  --tests 1 --seed 42 --instr-count 100 \
  --spike /path/to/spike --output build/riscv-dv/example
```

For a general random program with branch and jump instructions, select
`riscv_rand_instr_test`. Add `--load-store` for the upstream load/store stream;
that mode needs a core that supports misaligned loads and stores. The upstream
load/store PyFlow compatibility fixes are staged in the isolated generated
workspace. The upstream
`riscv_jump_stress_test` profile is also supported with subprograms disabled.
The upstream `riscv_unaligned_load_store_test` uses its random and hazard
load/store streams. ProcessorCI stages three small PyFlow fixes for this
profile; the 50-seed software campaign passed. It requires a core that
supports misaligned accesses. Compressed generation is disabled for this
profile, even when the selected ISA includes C. The legacy
`--experimental-profile` switch remains accepted for older matrix files.
For software validation of F/D programs, use `--isa rv64imfdc` with
`--profile riscv_rand_instr_test`, `riscv_arithmetic_basic_test`, or
`riscv_jump_stress_test`, an RV64 compiler, and Spike. These profiles enable
floating-point generation, check
all 32 FPRs and `fcsr`, and require a core with F/D and writable `mstatus.FS`.
Random and arithmetic profiles disable their directed and load/store streams.
Jump stress keeps the upstream directed jump stream and disables random
branches; its [10-package matrix](../reports/riscv-dv-rv64imfdc-jump-validation.json)
executed jumps in every seed across three memory layouts.
For the filtered Zbb profile, use `--isa rv32imc_zbb` with
`--profile riscv_arithmetic_basic_test`. The adapter derives a target from pinned
`rv32imcb`, disables draft B instructions, and requires executed Zbb
instructions before completion. Its [10-package matrix](../reports/riscv-dv-zbb-validation.json)
passed the exact compiler ISA, Spike, package validation, and host mock.
For the bounded atomic profile, use `--isa rv64ima --profile riscv_lr_sc_test`.
It generates one aligned, adjacent LR/SC pair with the pinned PyFlow stream,
using isolated compatibility fixes. The SC writes back the value loaded by LR,
so success and failure leave RAM unchanged. The SC result register is excluded
from the fixed GPR signature. A single-hart A-capable core is required; the
[11-package matrix](../reports/riscv-dv-lrsc-profile-validation.json) passed
shared, nonzero-base, and split memory configurations in software, with five
LR/SC.W and six LR/SC.D programs.
For deterministic AMOs on one hart, use `--isa rv64ima` with
`--profile riscv_amo_test`, `riscv_amo_pair_test`, or
`riscv_amo_triple_test`. These profiles use the upstream AMO stream with
isolated fixes to generate one, two, or three aligned
operations. The adapter moves the bounded stream before completion and checks
the full Spike-derived GPR and final memory signatures. The
[single-AMO campaign](../reports/riscv-dv-amo-profile-validation.json) passed
24 packages; the [two-AMO campaign](../reports/riscv-dv-amo-pair-profile-validation.json)
passed 18. Together they exercised all 18 word/doubleword AMO operations in
the pinned PyFlow model across three memory layouts. The
[three-AMO campaign](../reports/riscv-dv-amo-triple-validation.json) passed
12 more packages, each with three checked stores. Competing harts and
memory writers are outside these profiles.
For the bounded privileged profile, use `--isa rv32i` or `rv64i` with
`--profile riscv_csr_test`. It runs the upstream directed CSR Python generator
with [the full-width mscratch map](../examples/riscv-dv/csr-mscratch.yaml),
checks its own CSR reads and writes, and then requires Spike and host-mock
completion. `--csr-map` accepts an equivalent bounded map. This profile uses
one machine-mode hart and requires a writable `mscratch`. Its
[10-package matrix](../reports/riscv-dv-csr-profile-validation.json) passed
both XLENs, including a split nonzero-base layout. `--instr-count` controls
PyFlow profiles; the CSR generator uses its own fixed directed sequence.
The [expanded map](../examples/riscv-dv/csr-mscratch-mepc.yaml) adds aligned
`mepc` bits; its [10-package matrix](../reports/riscv-dv-csr-expanded-validation.json)
passed RV32I/RV64I with self-checks for both CSRs. A target core must make
`mepc` bits XLEN-1 through 2 writable as declared by that map.
Use `--upstream-option +name=value` for an approved PyFlow option such as
`+no_fence=1`. The adapter accepts only simple option tokens from a small
allowlist because upstream `run.py` constructs a shell command and other
options can change the hardware requirements. `--tests 100 --seed 1000` gives
100 individually seeded programs,
one upstream invocation per seed. Failed seeds are reported without retry.
Add `--reference-coverage` to run upstream PyFlow `cov.py` on the executed
raw Spike trace. The adapter limits the trace to instructions before
`test_done`, normalizes the upstream converter's trampoline assumption, and
saves `coverage/upstream/CoverageReport.txt` beside the package. The manifest
and per-seed report label it `spike_reference_execution`; it is not a DUT
measurement. The optional path has been validated on an RV32I arithmetic seed.

To run several ISA/profile configurations in one invocation, use the
[example matrix](../examples/riscv-dv/config-matrix.json):

```sh
python -m riscv_test_runner.cli --tool riscv-dv \
  --matrix examples/riscv-dv/config-matrix.json \
  --spike /path/to/spike --output build/riscv-dv/matrix
```

The JSON `configurations` list gives each row a unique `name`. A row may set
`isa`, `profile`, `seed`, `tests`, `instr_count`, `load_store`, toolchain and
Spike paths, memory settings, `reset_pc`, and the other single-run options; omitted fields
inherit CLI defaults. Numeric fields use JSON integers. Each row has its own
output directory and per-seed report. The root `report.json` and
`report.junit.xml` aggregate results.
Unsupported configurations get a named `unsupported` row with the preflight
error, and subsequent rows still run. The command exits nonzero if any row or
seed fails. Each package retains its own ISA and memory requirements.

Use `--testlist examples/riscv-dv/custom-testlist.yaml` to select an entry
from a user YAML test list. The selected entry must name one of the four
validated profiles and use `riscv_instr_base_test`. ProcessorCI accepts safe
generator options and the directed streams validated for that profile; it
rejects unsupported streams, privilege changes, and options that would change
the package's memory requirements without the corresponding CLI setting.
`--instr-count`, seed, ISA, and the bare machine-mode runtime remain under
ProcessorCI control. A test list may contain entries for several profiles;
`--profile` selects exactly one. The input YAML is saved as
`input-testlist.yaml` in every package and its SHA-256 is checked when the
package is reopened.

The [custom test-list matrix](../examples/riscv-dv/custom-testlist-matrix.json)
runs five ISA/profile combinations with nine seeds. All nine passed
[software validation](../reports/riscv-dv-custom-testlist-validation.json),
including two unaligned programs with committed misaligned wide accesses and
one RV64IMFDC program with 57 committed floating instructions.
Matrix `testlist` paths are resolved from the command's working directory.

Use `--target-settings examples/riscv-dv/rv32i-core-target.py` to supply a
PyFlow `riscv_core_setting.py` for a selected core. The adapter checks that
XLEN and ISA groups match `--isa` exactly, with one hart, bare machine mode,
and V disabled. Load/store profiles require the target's unaligned support.
It stages the settings outside the pinned submodule, saves `input-target.py`
in each package, and verifies its SHA-256 on reopening. Matrix rows accept
`target_settings`. The [example matrix](../examples/riscv-dv/custom-target-matrix.json)
passed [four software programs](../reports/riscv-dv-user-target-validation.json).
Settings that change privilege, A/V support, or the oracle need separate
profile validation. The [RV64IMA target example](../examples/riscv-dv/rv64ima-core-target.py)
has the exact A groups, bare machine mode, and one hart required by the
bounded atomic profiles. A [six-program matrix](../reports/riscv-dv-atomic-custom-target-validation.json)
passed LR/SC, one-AMO, and two-AMO packages using that target file across
three memory layouts.

The [advanced-profile audit](../reports/riscv-dv-advanced-profile-audit.json)
records the bounded A and CSR package profiles and the remaining limits.
Longer AMO streams, multi-hart ordering, illegal-instruction/trap profiles,
other CSRs, and MMU behavior remain open. A separate
[RV64GCV Spike probe](../reports/riscv-dv-vector-capability-probe.json)
executed vector arithmetic and captured all 16 bytes from a vector store.
This pinned PyFlow revision has no V instruction model or V-enabled target,
so there is no V generated package profile yet.

Each output directory contains `generated.S`, the adapted
`checked.S`, linked `program.elf`, `imem.hex`, `dmem.hex`, `manifest.json`,
linker and test-list files, and generation and Spike traces. For CSR-free
packages, `upstream-generated.S` preserves the exact PyFlow
output before the single-hart startup substitution. Atomic packages also save
that upstream source plus the staged target and generator copies. CSR packages
save the input map and staged directed generator. The hex images
are byte addressed: `@<16-digit byte address>` followed by byte values in
ascending address order. The sparse manifest's ELF LOAD segments are the
authoritative input to the existing serial loader. `report.json` and
`report.junit.xml` distinguish generation, compilation, Spike execution,
package validation, host-mock validation, and hardware status.

The raw program executes on Spike first. The adapter reads committed register
values and store results before `test_done` from Spike's trace, then adds
comparisons for 30 GPRs and up to 64 written memory bytes by default to the
completion path. `--memory-signature-limit N` selects 1 to 1024 bytes. When
more bytes were written than the limit, it samples evenly across sorted
addresses. It compiles a new ELF, executes it on Spike, and requires a write
of 1 to `tohost`; a mismatch writes 3. The manifest records the selected
address/value bytes and total number of written bytes. A program that commits
no stores has an empty memory signature. The upstream jump scratch register
varies by seed and cannot be compared at that point. For RV64IMFDC, all 32 FPRs
and `fcsr` are checked. Other CSRs and V state are outside this signature.
The CSR profile instead uses the upstream bounded CSR self-check. The LR/SC
profile excludes its SC destination and checks memory bytes that are identical
for success and failure.
The package uses the existing `selfcheck_tohost` schema,
and the existing serial loader is exercised through a software host mock.
Host-mock success is a protocol check; it is not a DUT result.

The adapter links raw and checked ELFs with the same data layout. If inserting
checks pushes `.text` across a linker page boundary, it fixes the `tohost`
placement, relinks both ELFs, and reruns the raw Spike reference before
validating the checked ELF. The manifest records `linker_layout`. This matters
for longer load/store programs because registers and stores can contain data
addresses that would otherwise change between the two ELFs.

To rerun a seed, use the `reproduction_command` in its report row. A saved
package can be loaded later with `riscv_test_runner.core.serial_package.run_package`
after supplying a core-specific memory size, reset PC, ISA set, and serial
device. The selected DUT must implement machine mode, Zicsr and Zifencei,
byte-addressed RAM at the selected base and a tohost write-completion breakpoint.
PyFlow packages also require `mhartid` unless `--single-hart-no-csr` was used;
the directed CSR profile instead requires the writable CSRs declared by its map.
It must also support every instruction in the package's ISA and, for
`--load-store`, the indicated misaligned memory policy. Set `--memory-base` to
a 4 KiB-aligned RAM address and `--reset-pc` to a word-aligned entry within
that RAM. For example, `--memory-base 0x80000000 --reset-pc 0x80000080`
links both raw and checked ELFs at the offset entry. The manifest records
the required base, size, and entry. The [five-configuration nonzero-base
matrix](../examples/riscv-dv/nonzero-base-matrix.json) passed the software
pipeline.

For a single-hart core without `mhartid` or Zicsr, add
`--single-hart-no-csr`. The adapter replaces the one upstream `mhartid` read
with `li x5, 0`, excludes CSR and fence instructions, compiles for the exact
base ISA, and records these requirements in the manifest. It retains and
hashes `upstream-generated.S` alongside the adapted `generated.S`. This mode
does not apply to floating programs, which need `mstatus.FS` and `fcsr`.
The [CSR-free matrix](../examples/riscv-dv/csr-free-portability-matrix.json)
covers RV32I, RV32IMC, RV64I, and RV32I load/store software execution.
Core-specific memory and completion wiring still need separate validation.

Set `--data-base` to a 4 KiB-aligned address above the reset PC and within
the configured RAM to separate executable and data LOAD segments. For example,
`--memory-base 0x80000000 --reset-pc 0x80000000 --data-base 0x80020000`
places `.tohost` and data at `0x80020000` or above. The package records a
`split_disjoint` layout and exports disjoint `imem.hex` and `dmem.hex` address
ranges; saved-package verification checks their placement. The
[three-configuration split matrix](../examples/riscv-dv/split-disjoint-matrix.json)
passed software validation. Spike and the serial host mock use a flat address
space. Loading through a core's separate physical instruction/data ports and
overlapping Harvard address ranges remain core-specific work for later use.

A [store-heavy custom test list](../examples/riscv-dv/memory-oracle-testlist.yaml)
and [two-limit matrix](../examples/riscv-dv/memory-oracle-matrix.json) exercise
the memory oracle with 64 sampled bytes and all 187 committed written bytes
checked at a limit of 256. The [validation report](../reports/riscv-dv-memory-oracle-validation.json)
records both software results.

New per-seed report rows include `manifest_sha256`. Before reusing a saved
package, check that digest and the assembly, ELF, and memory image hashes:

```sh
python -m riscv_test_runner.cli --tool riscv-dv \
  --verify-package build/riscv-dv/example/riscv_arithmetic_basic_test-rv32i-42 \
  --expected-manifest-sha256 <digest-from-report.json>
```

This read-only check validates the saved package files. The later DUT runner
still needs its own ISA, memory-map, and completion checks.

## Confirmed compatibility

| ISA | Upstream PyFlow target | Compiler and Spike | ProcessorCI package | DUT requirements |
| --- | --- | --- | --- | --- |
| RV32I | `rv32i` | Smoke validated | Smoke validated | I, machine mode, Zicsr, Zifencei, shared RAM |
| RV32IM | `rv32imc`, C disabled | Smoke validated | Smoke validated | I/M, machine mode, Zicsr, Zifencei, shared RAM |
| RV32IMC | `rv32imc` | Smoke validated | Smoke validated | I/M/C, machine mode, Zicsr, Zifencei, shared RAM |
| RV32IMC_Zbb | Filtered pinned `rv32imcb` target, 12 ratified Zbb mnemonics | 10 arithmetic seeds passed with 202 executed Zbb instructions | 10 packages passed host mock | I/M/C/Zbb, machine mode, Zicsr, Zifencei |
| RV64I | Derived `rv64i` target from pinned `rv64imc`, M/C removed | 15 arithmetic/random/jump seeds passed | 15 packages passed host mock | RV64 I, machine mode, Zicsr, Zifencei, shared RAM |
| RV64IM | `rv64imc`, C disabled | Smoke validated | Smoke validated | RV64 I/M, machine mode, Zicsr, Zifencei, shared RAM |
| RV64IMC | `rv64imc` | Smoke validated | Smoke validated | RV64 I/M/C, machine mode, Zicsr, Zifencei, shared RAM |
| RV64IMFDC | Derived `rv64imfdc` target from pinned `rv64imafdc`, A removed | 10 random, 5 arithmetic, and 10 jump F/D seeds passed | 25 packages passed host mock with FPR and `fcsr` checks | RV64 I/M/F/D/C, machine mode, writable `mstatus.FS`, Zicsr, Zifencei, shared RAM |
| RV64IMA | Derived `rv64ima` target from pinned `rv64imafdc` | 11 LR/SC, 24 single-AMO, 18 two-AMO, and 12 three-AMO seeds passed | 65 packages passed host mock | RV64 I/M/A, one machine-mode hart, Zicsr, Zifencei, aligned RAM |
| RV32I/RV64I CSR | Pinned directed Python CSR generator | 10 mscratch and 10 mscratch/mepc seeds passed | 20 packages passed host mock | Writable `mscratch` and aligned `mepc` as selected, one machine-mode hart |
| RV32E, other F/D, multi-hart A, traps/MMU, V, other Z | No validated target/adapter combination | Not claimed | Rejected by CLI | Requires separate evaluation |

The [RV32IMCB probe](../reports/riscv-dv-specialized-profile-audit.json)
generated PyFlow assembly, but the exact compiler rejected 21 draft or
extension-specific B instructions. The filtered Zbb target excludes those
instructions; the pinned PyFlow tree still has no RV32E target or ISA group.

These are package-generation results across the supported ISAs. CV32E40S and
Ibex have separate RV32 RTL replays; no FPGA core has run.
The `riscv_arithmetic_basic_test` profile works under PyFlow with the configured
shorter instruction count. The full upstream `riscv_rand_instr_test` profile
references directed streams that this PyFlow revision does not register.
The integer random profile selects only its upstream jump stream by default and optionally
its upstream load/store stream. The separate unaligned profile uses the
registered load/store hazard stream with isolated compatibility fixes.
The adapter records each reduction in every
manifest. The jump-stress profile also uses its upstream jump stream, with
subprograms forced to zero because the pinned PyFlow revision lacks its
call-stack generator. The upstream loop profile did not finish a timed probe
and remains unsupported. The SystemVerilog/UVM backends require separate
simulator support;
Verilator has not been assumed to run this flow. Optional upstream PyFlow
coverage from Spike reference execution is exported when requested. RTL/DUT
coverage is not exported by this software-only adapter.
The RV64IMFDC random, arithmetic, and jump profiles enable floating-point generation
and exclude directed and load/store streams. Their packages check all 32 FPRs
and `fcsr` against Spike after the GPR checks. The
[arithmetic campaign](../reports/riscv-dv-rv64imfdc-arithmetic-validation.json)
committed 283 floating instructions across five seeds.
The [jump campaign](../reports/riscv-dv-rv64imfdc-jump-validation.json)
executed 378 jumps and 778 floating instructions across ten seeds.

The adapter rejects unsupported ISAs and backends, missing dependencies,
unexpected upstream revisions, out-of-RAM packages, bad Spike completion,
and failed host-mock comparisons. The validated A and privileged slices are
limited to bounded LR/SC, AMO, and `mscratch`/`mepc` profiles above. Exception,
MMU, debug, vector, and other floating-point configurations remain outside this path.

## CV32E40S Controller RTL replay

The [saved-package RTL runner](../tools/run_riscv_dv_cv32e40s_rtl.py) verifies
each manifest and its file hashes, checks the ISA, zero entry, and 512 KiB
shared RAM bounds, then executes the package on the existing CV32E40S plus
ProcessorCI Controller simulation. It observes the acknowledged `tohost`
write and classifies the result with the package's existing outcome logic.
For example, after generating the named matrix packages:

```sh
python3 tools/run_riscv_dv_cv32e40s_rtl.py \
  --package build/riscv-dv/config-matrix-validation/rv32i-arithmetic/riscv_arithmetic_basic_test-rv32i-7100/manifest.json \
  --package build/riscv-dv/config-matrix-validation/rv32imc-random/riscv_rand_instr_test-rv32imc-7200/manifest.json \
  --package build/riscv-dv/config-matrix-validation/rv32i-load-store/riscv_rand_instr_test-rv32i-7400/manifest.json \
  --package build/riscv-dv/campaign-loadstore-1000-5/riscv_rand_instr_test-rv32i-6005/manifest.json \
  --output reports/riscv-dv-cv32e40s-controller-rtl.json
```

The [four-package RTL report](../reports/riscv-dv-cv32e40s-controller-rtl.json)
records RV32I arithmetic, RV32IMC random, RV32I load/store, and a long RV32I
load/store seed passing with `tohost=1`. The latter checked 26 committed
memory bytes. An [injected wrong register expectation](../reports/riscv-dv-cv32e40s-controller-rtl-induced-fail.json)
reached `tohost=3` and was classified as `SELF_CHECK_FAILURE`; only the
simulation memory image was changed. With `--serial-full-load`, the runner
uploaded saved ELF LOAD segments over the existing Controller UART protocol,
executed the core, and read back status. Both the [RV32I](../reports/riscv-dv-cv32e40s-controller-uart.json)
and [RV32IMC](../reports/riscv-dv-cv32e40s-controller-uart-compressed.json)
packages passed. A single experimental unaligned RV32I seed also passed
[core RTL replay](../reports/riscv-dv-cv32e40s-unaligned-controller-rtl.json).
These reports demonstrate RTL simulation, not physical FPGA execution.

## Ibex Controller RTL replay

The [Ibex reset-PC matrix](../examples/riscv-dv/ibex-reset-pc-matrix.json)
uses `reset_pc: 128` for five selected RV32 configurations. Reproduce its
software validation with:

```sh
python -m riscv_test_runner.cli --tool riscv-dv \
  --matrix examples/riscv-dv/ibex-reset-pc-matrix.json \
  --spike /path/to/spike --output build/riscv-dv/ibex-reset-pc-matrix
```

The [matrix report](../reports/riscv-dv-ibex-reset-pc-matrix-validation.json)
records five of five generated, compiled, Spike validated, packaged, and
host-mock validated. The [Ibex RTL runner](../tools/run_riscv_dv_ibex_rtl.py)
verifies each saved package before loading it. It stages a temporary copy of
the existing Ibex wrapper with shared 512 KiB RAM, byte enables, and grant and
response timing; the testbench applies an explicit core reset edge. The adjacent RV-Bench
sources are not edited. A [saved RV32I example](../examples/riscv-dv/ibex-rv32i-seed9700/manifest.json)
can be replayed directly:

```sh
python3 tools/run_riscv_dv_ibex_rtl.py \
  --package examples/riscv-dv/ibex-rv32i-seed9700/manifest.json \
  --output build/riscv-dv/ibex-example-rtl.json
```

The [five-package RTL report](../reports/riscv-dv-ibex-controller-rtl.json)
records RV32I and RV32IM arithmetic, RV32IMC random, RV32I jump stress,
and RV32I load/store all reaching `tohost=1`. The load/store package checked
seven committed memory bytes. This proves the staged simulation profile; the
unchanged Ibex wrapper and physical FPGA remain separate validation gates.

## Dependency and unaligned load/store profile

The original [unaligned matrix](../examples/riscv-dv/unaligned-profile-matrix.json)
retains the initial six failures. The adapter now stages isolated copies of two
PyFlow modules and records their SHA-256 digests in each new manifest. These
copies exclude `x0` as a load/store base, deep-copy load/store instruction
templates to prevent one stream changing another stream's registers, and
enable wide accesses in unaligned mode. The pinned submodule is unchanged.
Unavailable multi-page and memory-region streams remain disabled. Reproduce
the wider [five-ISA campaign](../examples/riscv-dv/unaligned-compat-campaign-matrix.json)
with:

```sh
python -m riscv_test_runner.cli --tool riscv-dv \
  --matrix examples/riscv-dv/unaligned-compat-campaign-matrix.json \
  --spike /path/to/spike --output build/riscv-dv/unaligned-true-50
```

The [50-seed summary](../reports/riscv-dv-unaligned-compat-validation.json)
records 50 complete PyFlow, compiler, Spike, package, and host-mock passes.
Spike committed 589 misaligned halfword, word, or doubleword accesses across
49 seeds; one seed finished without taking such an access. Two repaired RV32I
packages also passed [CV32E40S RTL replay](../reports/riscv-dv-cv32e40s-unaligned-width-rtl.json).
Compressed instructions are disabled for this profile because the pinned
PyFlow load/store path produced constraint failures on RV64IMC when they were
enabled. No compressed hazard coverage is claimed. The original
[ten-seed failure report](../reports/riscv-dv-unaligned-experimental-validation.json)
is kept as evidence of the unfixed upstream behavior.

The derived RV64I target removes M and C from the pinned RV64IMC PyFlow
settings. The [15-seed RV64I report](../reports/riscv-dv-rv64i-profile-validation.json)
records five seeds each for arithmetic, random, and jump profiles, all
Spike/package/host-mock validated. All 15 linked ELFs report
`rv64i_zicsr_zifencei`; five further RV64I unaligned/hazard seeds passed the
[software path](../reports/riscv-dv-rv64i-hazard-validation.json), all with
committed misaligned wide accesses. No RV64 core RTL execution is claimed.

The [initial RV64IMAFDC probe](../reports/riscv-dv-rv64fd-pyflow-probe.json)
identified that bare startup left `mstatus.FS` disabled. The adapter now
stages an RV64IMFDC target without A and enables floating-point state before
PyFlow's FPR initialization. The [10-seed campaign](../reports/riscv-dv-rv64imfdc-profile-validation.json)
passed the complete software path; each checked program compared 32 FPRs and
`fcsr` at `test_done`. The campaign committed 501 floating instructions,
including double-precision operations, and no atomic instructions. An
FPU-equipped DUT has not been replayed in RTL or hardware.
The original [AMO probe](../reports/riscv-dv-rv64a-pyflow-probe.json) stopped
during PyFlow stream construction. Isolated fixes now support bounded
[RV64IMA LR/SC](../reports/riscv-dv-lrsc-profile-validation.json),
[single-AMO](../reports/riscv-dv-amo-profile-validation.json), and
[two-AMO](../reports/riscv-dv-amo-pair-profile-validation.json) packages. The
[three-AMO matrix](../reports/riscv-dv-amo-triple-validation.json) adds 12
more packages under the same single-hart oracle.
Multi-hart ordering profiles still need separate outcome policies.

## Recorded software campaign

The [validation summary](../reports/riscv-dv-validation.json) records four
campaigns on this workspace: 100 RV32I arithmetic, 10 RV32I random, 10
RV32IMC random, and 10 RV64IMC arithmetic programs. All 130 generated,
compiled, passed Spike, exported packages, and passed the serial host mock;
none has run on hardware. The exact per-seed records and JUnit reports are in
`build/riscv-dv/campaign-*-final/`. A complete saved RV32I seed 5000 package
is in [examples/riscv-dv/rv32i-arithmetic-seed5000](../examples/riscv-dv/rv32i-arithmetic-seed5000/).

The 100-program run used:

```sh
python -m riscv_test_runner.cli --tool riscv-dv \
  --isa rv32i --profile riscv_arithmetic_basic_test \
  --tests 100 --seed 5000 --instr-count 40 \
  --spike /path/to/spike \
  --output build/riscv-dv/campaign-rv32i-100-final
```

The other campaigns used the same command with `--tests 10` and these
ISA/profile/seed/output combinations: `rv32i`/`riscv_rand_instr_test`/2000/
`campaign-rv32i-random-10-final`, `rv32imc`/`riscv_rand_instr_test`/3000/
`campaign-rv32imc-10-final`, and `rv64imc`/`riscv_arithmetic_basic_test`/4000/
`campaign-rv64imc-10-final`.

The historical 130-program summary predates memory checking. A separate
[load/store campaign summary](../reports/riscv-dv-load-store-validation.json)
records 10 RV32I random seeds at 100 instructions with `--load-store`.
All 10 passed PyFlow, compilation, Spike, package validation, and the serial
host mock. Eight committed stores and received memory checks; two committed no
stores before `test_done`. A real seed 42 test also confirmed that corrupting
one expected memory byte prevents Spike completion. Reproduce the campaign
with the example command above, changing the profile to
`riscv_rand_instr_test`, the seed to `6000`, the count to `10`, and adding
`--load-store`.

The [configuration matrix validation](../reports/riscv-dv-config-matrix-validation.json)
records four named configurations and eight programs across RV32I arithmetic,
RV32IMC random, RV64IMC jump stress, and RV32I load/store. All eight passed
generation, compilation, Spike, package validation, and the serial host mock;
none has run on hardware.

An additional [ISA/profile matrix](../examples/riscv-dv/isa-profile-matrix.json)
ran one seed for every combination of the five supported ISAs and the three
supported profiles. The [15-result summary](../reports/riscv-dv-isa-profile-matrix-validation.json)
records all 15 as software validated. These are configuration smokes; the
longer campaigns above provide broader seed coverage for selected combinations.

The [long-profile matrix](../examples/riscv-dv/long-profile-matrix.json) ran
four 1,000-instruction configurations. All four passed the software pipeline.
The [result summary](../reports/riscv-dv-long-profile-validation.json) records
that one branch-restricted load/store seed committed 26 memory bytes and used
fixed `tohost` placement. The other load/store seed generated memory
instructions but executed no store before `test_done`, so its memory signature
was empty. A generated load/store stream does not guarantee a store on every
execution path.

A separate [five-seed long load/store campaign](../reports/riscv-dv-long-load-store-validation.json)
used RV32I, 1,000 instructions, `--load-store`, and
`--upstream-option +no_branch_jump=1`. All five seeds passed software
validation and committed stores; their manifests checked 26, 6, 17, 6, and
21 memory bytes respectively. One seed exercised the fixed-layout fallback.
A [five-seed RV32IMC random campaign](../reports/riscv-dv-long-random-validation.json)
at 1,000 instructions also passed generation, Spike, package validation, and
the serial host mock.

The [reference coverage validation](../reports/riscv-dv-reference-coverage-validation.json)
records one RV32I seed with a nonempty upstream coverage report and an
integrity-checked manifest. The 147 reported groups belong to the upstream
model; the adapter records the group count and report hash without treating
the score as DUT coverage.

Offline CI runs the adapter's dependency-free tests alongside the directed
suite. The real PyFlow/Spike tests run when `PROCESSORCI_SPIKE` points to an
installed Spike and the optional Python and toolchain dependencies are present;
they are not yet part of the offline CI job.
