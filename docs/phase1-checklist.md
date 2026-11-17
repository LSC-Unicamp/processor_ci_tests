# ProcessorCI Tests phase-one checklist

Source of requirements: `ProcessorCi_Tests_phase1_prompt.md` in the workspace
root. Check a box only after its stated evidence exists. Keep counts tied to
the generated reports; do not infer validation from a filename or mock result.

## Current baseline (2026-11-16)

- Basic ISA: 602 instructions inventoried across defined groups; 76 legacy
  sources compile, contain the target opcode, and match checked-in images.
  A separate Sail replay matched 67 old numeric references at the first
  completion write. Eleven RV32A references are comment-only placeholders;
  the intentional timeout has no completion write. Three numeric RV32I
  references have comment-only source placeholders.
  **599** dedicated ordinary tests compile, contain the intended encoding,
  pass Sail, and pass the host package check. The other **3** encodings are
  `ecall`, `ebreak`, and `c.ebreak`, validated separately with expected M-mode
  trap cause and PC checks. B 1.0 is split into named Z subsets; all 259
  applicable RV32Zve32x forms are tested under a Zvl128b profile. The legacy
  B, P and V groups were removed; P is excluded while its specification is a
  draft. The pinned 375-form V catalog has 371 forms applicable to RV32 full V;
  all 371 are Sail validated across five named Zve groups. Four indexed EEW64
  forms are Sail validated under RV64Zve64x. All 375 basic forms and fourteen
  advanced vector scenarios also pass VLEN=128 replay under full V and their
  matching named Zve Sail support levels. Parameter and state coverage is
  still sampled.
- ACT 4.1.0: pinned at `6e8a45123f14cebfb3df151a0e7b849b4389b33b`.
  The upstream Sail RVI20U32 software configuration produced **39** RV32 I
  self-checking ELFs, **39** packages, **39** direct Sail passes, and **39**
  host-mock validations. The upstream RVI20U64 software configuration produced
  **51** RV64 I self-checking ELFs and packages, all directly Sail-executed and
  host-mock validated. The RV32 max sample generated **47** tests for an I/M/C
  request: I 39, M 8, C 0; all 47 passed Sail and host checks. ACT 4.1 has no
  C test source in its current `tests/` tree. These are software sample targets.
  The selected RV-Bench CV32E40S DUT profile runs all 47 I/M packages through
  controller/UART RTL. No C, U-mode, interrupt, or Zkt DUT ACT validation is
  claimed. FPGA execution remains pending.
- Advanced: **59** distinct scenarios across RV32 I/M/C/A/F/D/Zicsr/Zve32x/Zve64x and RV64 I/M/A/F/D
  compiled, disassembled, packaged, and passed under both QEMU user mode and
  Sail. **0** have DUT execution evidence.
- Invalid: all **60** generic legacy placeholder triples have been retired.
  Nineteen new
  expected-trap package tests, including a deliberately illegal 32-bit
  encoding, a reserved 16-bit compressed encoding, reserved CSR access, and
  two U-mode privilege violations, two policy-dependent misalignment traps, and
  FP instructions with FS disabled, a read-only CSR write, a vector instruction
  with VS disabled, and RV32/RV64 misaligned AMOs pass Sail and host checks.
  Three retired triples map directly to packages; the other 57 never specified
  an instruction or expected trap.
- Existing random/generated workflow: absent from this local checkout. Do not
  claim coexistence or compatibility until the actual implementation is found
  or integrated.
- Software checks last run: 49 pytest tests passed; 599/599 basic Sail cases,
  19/19 invalid trap cases, 59/59 advanced QEMU and Sail cases, 389/389 VLEN128
  full-V and named-Zve Sail replays, and 39/39 RV32
  plus 51/51 RV64 and 47/47 RV32 I/M/C-request ACT Sail executions passed.
  FPGA results: none.

## 1. Audit and inventory — Phase A

- [x] Inspect local repository, uncommitted changes, runner, configuration,
  build scripts, test tree, and historical ACT submodule.
- [x] Scan basic, advanced, and invalid legacy assets; record comment-only and
  missing assets in `reports/isa-audit/`.
- [x] Reconcile all 23 ISA test directories against their legacy triples and
  built packages. All 599 basic, 59 advanced, and 19 invalid package sources
  are present. All configured ISA groups now have advanced packages, and the
  current directory audit has no ISA directory findings;
  configured extra tests are outside this audit's scope.
- [x] Repair and replay the 80 RV32M and two RV32I control-flow legacy
  advanced cases: numeric references agree with an independent RV32 oracle
  and Sail's first completion write. Correct 12 divide-by-zero result stores,
  rebuild their images, and remove seven orphan placeholder references.
- [x] Replace the legacy timer's wrong MMIO address with `0xfffffffc`, add
  a self-checking result and matching image/reference, and verify the timer
  counter RTL unit. Full core/controller execution of that program remains
  pending and is reported separately from the 82 Sail replays.
- [x] Retire 147 comment-only legacy advanced source/image/reference triples
  and stop the structure script from recreating them. Keep their paths in
  `tools/legacy_advanced_retired.txt`; place real advanced sources under their
  ISA groups and add RV64 A/F/D/M plus RV32 CSR scenarios.
- [x] Build a conservative core instruction inventory for RV32/64 I, M, A,
  C, F, D, and Zicsr against the selected ISA specification.
- [x] Reassemble supported RV32 legacy sources, verify intended opcodes in
  disassembly, and compare memory images with source builds.
- [x] Replace legacy B with Zba/Zbb/Zbs, track Zbc and Zbkb separately, and
  remove unratified P and obsolete V profiles.
- [x] Classify all 375 pinned V opcode forms for RV32Zve32x applicability:
  259 applicable forms have dedicated Sail-validated cases; 101 vector FP,
  13 EEW64 memory and two SEW64-dependent forms are outside that profile.
- [x] Classify the remaining 116 forms by minimum Zve subset and XLEN:
  Zve32f 66, Zve64x 15, Zve64f 6, Zve64d 29; four indexed EEW64 forms
  require RV64. Record the per-form result in the vector catalog report.
- [x] Add and Sail-validate the 11 additional RV32 Zve64x integer forms under
  Zvl128b. The other four Zve64x forms require RV64 indexed EEW64 memory.
- [x] Add and Sail-validate the 66 Zve32f, six Zve64f, and 29 Zve64d RV32
  forms. All 371 RV32 full-V opcode forms now have dedicated basic cases.
- [x] Add and Sail-validate the four indexed EEW64 forms that require RV64.
  The full 375-form pinned V opcode catalog is covered across RV32/RV64
  software profiles; this is not one core's verified hardware coverage.
- [ ] Vary vector parameters and state beyond the basic opcode-form cases;
  validate selected real core profiles. VLEN128 software replay now passes
  375 basic and fourteen advanced vector cases under full V and named Zve
  support levels. The directed cases now sample fractional LMUL, LMUL=2/8,
  SEW 8/16/32/64, selected VL values from 2 through 40, `vxrm`, masking,
  tail and `vstart` behavior;
  real-core evidence remains open.
- [x] Classify all 166 configured legacy basic sources, images, and references
  per asset and group. RV64, F, D, and Zicsr old sources have no instruction
  body to compile; their new package sources are compiled, disassembled,
  packaged, and Sail validated. The 79 substantive old RV32 sources are replayed
  separately; 76 inventoried sources also match their checked-in images.
- [x] Replay all 79 substantive legacy RV32 basic sources under Sail with
  the old address-zero layout: 67 numeric reference matches, 11 RV32A
  comment-only references, and one intentional timeout. Record each source in
  `reports/isa-audit/legacy_basic_sail.json`. Legacy RV64, FP, and CSR sources
  are comment-only; new package cases cover their defined encodings separately.

## 2. Complete basic instruction tests — Phase B

- [x] Establish a reproducible basic Sail build path with 599
  dedicated tests, real opcode checks, sparse packages, and a corrupted
  expected-result negative test.
- [x] Cover the current defined I/M/A/C/F/D/Zicsr and RV64 core inventory:
  187 ordinary basic cases plus 3 separate expected-trap cases.
- [x] Add 412 Z-extension cases: RV32 Zba 3, Zbb 18, Zbc 3, Zbs 8,
  unique Zbkb 5, 371 RV32 vector cases across five Zve groups, and four
  RV64-only Zve64x forms. Remove legacy B/P/V directories.
- [x] Ensure every selected ordinary basic case yields a reproducible ELF,
  sparse memory image, target opcode proof, expected result, and ProcessorCI
  package. Legacy placeholder assets remain separately flagged by the audit.
- [x] Run all 599 ordinary basic cases under a matching Sail configuration;
  compare the self-checking result with the hand-specified expectation.
- [x] Verify target opcode width from disassembly for every basic package:
  all 34 ordinary RV32C targets have 16-bit encodings, and all other targets
  have 32-bit encodings. A forced 32-bit replacement fails the build proof.
- [x] Handle the selected software configurations without false passes:
  SC success/failure paths check the corresponding memory state; FP cases
  compare raw bits and selected NV/DZ/NX flags; all C targets have verified
  16-bit encodings; legal CSR operations pass Sail and illegal accesses reach
  cause-checked handlers. Corrupted expectations and trap states fail.
- [x] Reach 100% of the defined software instruction inventory: 599 ordinary
  Sail-validated encodings plus three separately validated expected-trap
  encodings. The pinned V catalog is 375/375 across RV32/RV64 software
  profiles. This does not establish core-specific or hardware coverage.

## 3. ACT 4.1 integration — Phase C

- [x] Replace historical RISCOF gitlink at the canonical path with pinned
  ACT 4.1.0; remove obsolete RISCOF-only helper scripts.
- [x] Install Sail 0.13.1 and build real upstream RV32 I self-checking tests
  with Sail-derived signatures using the software reference configuration.
- [x] Convert 39 real ACT ELFs to sparse packages retaining `tohost`, entry,
  segments, ISA, and upstream revision; execute all 39 with Sail after build.
- [x] Build and validate 51 RV64 I ACT 4.1 tests using the official
  Sail RVI20U64 software configuration; report them separately from RV32 I.
- [x] Request I/M/C against the ACT 4.1 Sail RV32 max software sample:
  39 I and 8 M tests generated and validated; C has zero upstream sources.
- [x] Audit `processorci_top`, per-core JSON, board memory sizes and controller
  status behavior as reusable ACT DUT inputs; document missing hardware claims
  and the current ACT ELF size mismatch.
- [x] Select picorv32/Nexys4 DDR as the first candidate and add a static
  package-fit checker. The current 39 ACT RV32 sample packages all fail its
  reset-PC and 8 KiB memory checks. The smallest LOAD payload is 77,776
  bytes, so even a linker relayout cannot fit the current sample on a 16 KiB
  board. The directed I/M/C probe used the *legacy ProcessorCI wrapper* and
  does not describe RV-Bench's picorv32 wrapper, which uses core defaults.
- [x] Analyze RV-Bench's pinned sources and curated wrappers for a standard
  machine-mode ACT candidate. Select CV32E40S at
  `9d9cae78b01a11458953133d1173c61933a2ba86`. Its wrapper has a passing
  RV-Bench execution smoke record, and a new directed probe passed `mstatus`,
  `mtvec`, `ecall`/`mcause`/`mepc`/`mret`, multiply/divide, and `c.addi` through
  that wrapper. See `docs/act4-rvbench-core-selection.md` and
  `reports/act4-cv32e40s-rvbench-probe.json`. This is not an ACT execution.
- [x] Stage the ACT 4.1 CV32E40S UDB, Sail configuration, macros and reset-zero
  linker in `build/act4-cv32e40s/`; use `tohost=1/3` for ProcessorCI
  classification. Build 39 I and eight M ELFs and packages; all 47 pass direct
  Sail and host oracle checks. The linker and Sail program region now match
  508 KiB; ACT-required CLINT and interrupt-generator devices are explicitly
  reference-only. Detailed UDB capability claims remain under review.
- [x] Run a real ACT `I-addi-00` ELF through the RV-Bench CV32E40S wrapper:
  `tohost=1` is PASS, and an injected instruction error produces `tohost=3`
  and SELF_CHECK_FAILURE. Fix the wrapper's missing store response and
  `fence.i` acknowledgement; rerun RV-Bench wrapper validation successfully.
  These are core/wrapper RTL results with 512 KiB simulation memories, not
  controller or FPGA execution.
- [x] Run the real ACT `M-mul-00` ELF through the corrected RV-Bench wrapper;
  RTL writes `tohost=1` and the host oracle classifies PASS.
- [x] Inspect the smallest generated ACT RV32 ELF: 8,832 bytes of test code,
  68,000 bytes of initialized data, 16 bytes of `tohost`, and 928 bytes of
  model code. Its 77,776-byte LOAD lower bound cannot fit by relinking or
  shrinking the reserved stack.
- [x] Build a separate 176-byte RV32I address-zero bring-up package with an
  explicit 8 KiB linker map and `tohost` at `0xa0`. It passes Sail and static
  picorv32/Nexys4 fit checks; it is a directed smoke case, not an ACT result.
- [x] Host-mock test PASS, self-check FAIL, timeout, trap, and malformed
  package handling; preserve ACT's self-checking oracle.
- [x] Give expected-trap packages distinct observed failure codes for no trap,
  wrong cause, and wrong `mepc`; map them through the canonical host oracle
  and mock serial adapter without changing legacy package results.
- [ ] Create a truthful ProcessorCI DUT `test_config.yaml`, UDB YAML,
  `rvmodel_macros.h`, linker script, Sail config, and memory map for each
  selected core. The selected CV32E40S has an audited 512 KiB map and a
  conservative I/M test scope. A directed RTL probe now checks `mtvec` WARL,
  misaligned word access, and U-mode fetch denial with zero PMP regions.
  The first probe `mstatus` read was zero despite an RTL reset constant of
  `0x1800`; resolve that discrepancy and the full CSR WARL/reset matrix.
  Zc/JVT, external interrupt/WFI, and Zkt timing claims still need review.
  ACT requires reference-only CLINT and
  interrupt-generator services in Sail; they are not DUT hardware.
- [x] Source-review the selected CV32E40S **I/M execution profile** against
  the pinned wrapper and RTL: verify core defaults, PMP/PMA behavior, RAM,
  reset address, completion, `mtvec` reserved writes, and misaligned word access.
  Align Sail RAM cacheability and WFI behavior. The directed probe passes;
  the audit records broader claims separately without counting them as ACT
  DUT coverage.
- [x] Reconcile the selected ACT 4.1 DUT coverage with generated test sources
  and observed execution: I 39, M 8, C 0. The pinned ACT tree has no C
  source directory; C and other advertised core extensions have no ACT DUT
  pass count. Record the scope and known profile limitations in the
  machine-readable profile audit and combined report.
- [x] Validate real ACT self-check PASS and deliberately induced FAIL through
  the ProcessorCI controller and UART execution interface. A serial-loaded
  ADDI mismatch returns `tohost=3` and 371 bytes of readable diagnostics;
  an illegal-instruction mutation reports cause 2 and EPC `0x88`. An
  unreachable completion address reports TIMEOUT despite an ACT pass status.
- [ ] Build a truthful configuration for a real ProcessorCI RV32IMC core and
  verify its actual capabilities; keep C coverage open because the pinned ACT
  release has no C test sources. CV32E40S is the selected RV-Bench candidate;
  its sampled machine-mode and RV32IMC RTL path passed, and all 47 generated
  I/M ELFs run through its wrapper and controller. Its ACT UDB still needs
  the four reviews above, and the current memory map does not fit the board. The earlier picorv32
  probe used a different, legacy wrapper.
- [x] Verify controller sparse-segment loading, byte enables, shared address
  visibility, write-qualified completion, UART status readback, and ACT
  diagnostic retrieval in RTL. The 512 KiB shared map fits all 47 I/M
  packages. All 47 pass with simulation preload and full UART segment upload.
  See `docs/act4-cv32e40s-512k-integration.md`.
- [ ] Synthesize a memory backend for a selected FPGA board and verify device
  loading and execution. The old board RAM profile fits 0/47 ACT packages;
  the 512 KiB wrapper configuration is not yet an FPGA result.

## 4. Advanced and exception suites — Phase D

- [x] Implement at least 30 distinct scenarios covering dependencies, control
  flow, memory, arithmetic/M corner cases, and compressed execution.
- [x] Compile, verify intended encodings, package, and run the 38 initial
  scenarios under QEMU; include a corrupted expected-value negative test.
- [x] Validate all 59 advanced cases with Sail and reject a deliberately
  corrupted expected result. Export their Sail-tested sparse packages and
  exercise the host oracle. DUT pipeline behavior remains unobserved.
- [x] Add practical A, F, D, RV64, and Zve32x interaction scenarios and validate
  them with QEMU and Sail. Full V coverage remains open.
- [x] Add a two-lane EEW64 Zve64x load/arithmetic/store scenario and validate
  both output lanes under QEMU and Sail.
- [x] Check mask-undisturbed lanes and `vstart` CSR write/read/reset with
  QEMU and Sail. A separate nonzero-`vstart` vector-load resume now passes
  both models; it checks unchanged early lanes, updated later lanes and reset
  `vstart`. The arithmetic resume probe passes QEMU and permissive Sail but
  traps in the pinned strict Sail configuration by its `zero_required.arith`
  setting. It remains a conditional, separately reported capability.
- [x] Check tail-undisturbed behavior when VL contracts from four to two
  e32 lanes and expands back to four; QEMU and Sail both preserve lanes 2–3.
- [x] Check four saturating e8 lanes and sticky `vxsat` under QEMU and Sail;
  check DZ flags for the exact-zero FP32 reciprocal estimate basic cases.
- [x] Check an e8 LMUL=2 group with VL=20 across the VLEN128 register
  boundary, plus a nonzero-`vstart` store that preserves lanes 0–1 and
  updates lanes 2–3. Deliberately corrupted lane checks fail QEMU and Sail.
- [x] Check fractional LMUL=1/2 at SEW8/VL8, LMUL=8 at SEW16/VL40,
  `vxrm` rounding state, and masked stores preserving disabled lanes. All
  four pass QEMU, Sail, and both VLEN128 Sail profiles; corrupted checks fail.
- [x] Derive VLMAX at runtime for SEW8/16 and LMUL1/2, check their ratios,
  and verify AVL=1024 clamps to VLMAX. The same source passes QEMU and Sail
  with different modeled VLEN values; a wrong ratio fails both.
- [x] Check dynamic FP rounding: RTZ and RUP convert 1.5 to different integer
  results, each sets NX, and a deliberately wrong rounding mode fails under
  QEMU and Sail.
- [x] Add observable M-mode handlers for ECALL, EBREAK, and C.EBREAK; compare
  `mcause` and `mepc` and reject an intentionally wrong cause. Also validate
  an illegal 32-bit encoding and reserved CSR access with cause 2.
- [x] Enter U mode with explicit PMP access and validate illegal U-mode MRET
  and machine CSR read as cause-2 traps under Sail RV32 max.
- [x] Validate reserved compressed encoding `0x0000` as a cause-2 trap with
  exact `mepc` and an independently checked 16-bit ELF encoding.
- [x] Validate misaligned word load/store cause 4/6 and exact `mepc` under the
  pinned Sail RVI20U32 alignment policy; require both cases to fail when an
  allow-misaligned override disables the expected traps.
- [x] Replace three comment-only invalid placeholder triples with executable
  cause-checked packages for illegal32, illegal16, and F with FS disabled.
  Enabling FS makes the F case fail its expected-trap oracle. The replacement
  map is in `reports/isa-audit/invalid_replacements.json`.
- [x] Retire all 57 remaining generic comment-only invalid triples and stop
  the structure script from recreating them. Add eight cause-checked RV32/RV64
  ISA and state traps. `legacy_invalid_retired.json` records all 60 removals;
  57 had no defined instruction or expected result to preserve. Negative Sail
  replays restore legal FP/vector/alignment state and must report missing trap.
  Never count a hang as an expected trap.

## 5. Shared execution, builds, and reports — Phases E–G

- [x] Add exact XLEN/extension directory selection and offline listing;
  expand standard B/V aliases to their Z prerequisites, keep umbrella B/V
  directories out of executable selection, list invalid trap packages by ISA,
  and reject draft P without a profile. Offline listing now also filters exact
  instruction, scenario, category, and test ID without bypassing ISA checks.
- [x] Add a sparse ACT package validator and distinct host-side outcomes for
  PASS, self-check failure, timeout, trap, and invalid package.
- [x] Use one sparse manifest schema for basic, advanced Sail, ACT, and trap
  packages, with separate oracle types. No riscv-dv packages exist in this
  checkout to migrate.
- [x] Add serial loading of sparse packages, memory initialization, completion/status
  observation, and ACT failure diagnostics to the canonical package adapter.
  The real UART RTL path now distinguishes PASS, self-check failure, unexpected
  trap with cause/EPC, and timeout. The adapter keeps failures
  distinct: mismatch, self-check failure, missing/extra trap, timeout,
  communication error, unsupported, invalid, inconclusive. A host-mocked
  zero-based serial adapter loads a fitting package by clearing and writing the whole program RAM,
  reads back `tohost`, and classifies PASS/FAIL/TIMEOUT and detailed trap
  self-check failures with a cycle-boundary
  check. Interpreter RTL protocol simulation and controller write-qualified
  completion probes pass. Real-device behavior remains unverified.
- [x] Validate offline ISA/capability filtering from manifest metadata for
  RV32/RV64 differences and B, V, Zve, Zvl, F/D and Zicsr dependencies.
  Full RV32V selects the FP64 Zve packages while RV64-only indexed forms stay
  out of RV32 selection.
- [ ] Check advertised ISA and manifest filtering against a selected core's
  actual RTL and privilege capabilities. CV32E40S I/M execution is confirmed;
  C/Zc and U-mode filters must respect the zero-source and zero-PMP limits.
- [x] Make basic and advanced builds reproducible with explicit toolchain,
  `-march`, ABI, linker/runtime, disassembly, and reference configuration.
- [x] Add meaningful pytest negative tests for all package/oracle types,
  memory packing, C widths, RV64, A/F/D/V, traps, CLI filters, JSON/JUnit, and
  legacy compatibility.
- [x] Extend software-only CI to rebuild all 599 basic cases, nineteen expected
  traps, 59 advanced cases with Sail and QEMU, and replay 389 vector cases at
  VLEN128 with full V and named Zve Sail configurations. ACT builds remain a separate
  manual target because of their larger Ruby and Python dependency stack.
- [x] Generate separate basic, advanced, ACT, and combined reports from actual
  scans and executions. Never merge ACT certification counts with basic
  instruction coverage. The combined report separately records 47/47 CV32E40S
  controller RTL and UART upload PASS cases, three negative outcomes, its
  static profile map audit, and the legacy board profile's 0/47 fit.

## 6. Documentation and final acceptance — Phase H

- [x] Document current audit, ACT 4.1 setup, Sail install, offline commands,
  and explicit software/hardware limitations.
- [x] Document how to add/rebuild each basic and advanced case, select suites,
  reproduce a failure, update ACT, and configure a real DUT in
  `docs/adding-tests.md`.
- [x] Re-run all available software gates; record exact commands, counts,
  failures, and example packages/reports in the final report.
- [x] Run ACT I/M on the selected core, controller, and UART RTL; all 47 pass.
- [ ] Run on an FPGA when a 512 KiB memory backend and hardware are available;
  keep FPGA validation marked pending until then.

## Immediate next sequence

1. Validate the sampled vector parameter/state cases against selected real
   core profiles; software VLEN128 and named Zve replays are reproducible.
2. Resolve the CV32E40S initial `mstatus` read/reset discrepancy and finish
   the staged UDB's full CSR WARL/reset and Zc/JVT checks;
   add external interrupt/WFI support before claiming those tests, and measure
   Zkt timing before claiming it. The directed probe has resolved sampled
   `mtvec`, misaligned word, and zero-PMP U-mode behavior.
3. Synthesize a 512 KiB backend or reduce the ACT payload for a selected board;
   existing board configuration still fits 0/47 packages.
4. Run the already validated controller/UART path on an FPGA when hardware is
   available. RTL covers loading, status, diagnostic text, trap, and timeout.
