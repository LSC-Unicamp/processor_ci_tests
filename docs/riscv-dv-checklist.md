# riscv-dv integration checklist

Tracks the work requested in `ProcessorCI_Tests_agent_prompt_riscvdv.md`.
Status reflects the evidence available on 17 November 2026. `[x]` means
implemented and checked; `[ ]` means open or only partly validated. This work
is in ProcessorCI Tests. Running it through RV-Bench is a later integration.

**Current priority:** broaden core portability across memory maps and core
profiles, then advance the generator profiles and Spike-derived oracles.
Further device evidence will be gathered later through RV-Bench. A real
PyFlow/Spike CI job is lower priority for this stage.

**Recorded software baseline:** [130 programs](../reports/riscv-dv-validation.json)
generated, compiled, Spike validated, packaged, and passed through the serial
host mock with register checks; zero FPGA runs. A separate
[10-program load/store campaign](../reports/riscv-dv-load-store-validation.json)
used the newer memory signature and also passed software validation. The saved
[example package](../examples/riscv-dv/rv32i-arithmetic-seed5000/manifest.json)
contains the original assembly, checked assembly, ELF, and memory images.
The [configuration matrix result](../reports/riscv-dv-config-matrix-validation.json)
adds eight validated programs in four named configurations.
The original [ISA/profile cross product](../reports/riscv-dv-isa-profile-matrix-validation.json)
adds one validated seed for each of 15 combinations across five ISAs.
The [long-profile matrix](../reports/riscv-dv-long-profile-validation.json)
adds four 1,000-instruction programs, including one with 26 checked memory bytes.
A [five-seed long load/store campaign](../reports/riscv-dv-long-load-store-validation.json)
passed with executed stores in every seed.
A [five-seed long random campaign](../reports/riscv-dv-long-random-validation.json)
passed for RV32IMC at 1,000 instructions.
The [CV32E40S Controller RTL replay](../reports/riscv-dv-cv32e40s-controller-rtl.json)
passed four saved packages; separate UART uploads passed RV32I and RV32IMC.
The [original unaligned profile probe](../reports/riscv-dv-unaligned-experimental-validation.json)
retains its four passes and six failures. After isolated PyFlow fixes, a
[50-seed cross-ISA hazard campaign](../reports/riscv-dv-unaligned-compat-validation.json)
passed software validation and recorded 589 committed misaligned wide accesses.
The [RV64I profile campaign](../reports/riscv-dv-rv64i-profile-validation.json)
passed 15 arithmetic, random, and jump seeds.
The [RV64IMFDC jump campaign](../reports/riscv-dv-rv64imfdc-jump-validation.json)
passed 10 F/D packages with executed jumps in every seed.
The [three-AMO campaign](../reports/riscv-dv-amo-triple-validation.json)
passed 12 packages; the [expanded CSR campaign](../reports/riscv-dv-csr-expanded-validation.json)
passed 10; and the [filtered Zbb campaign](../reports/riscv-dv-zbb-validation.json)
passed 10 packages with 202 executed Zbb instructions.
The [custom test-list campaign](../reports/riscv-dv-custom-testlist-validation.json)
passed nine seeds across five configurations, including F/D and unaligned
profiles.
The [Ibex reset-PC matrix](../reports/riscv-dv-ibex-reset-pc-matrix-validation.json)
passed five software configurations, and all five passed
[Ibex plus Controller RTL replay](../reports/riscv-dv-ibex-controller-rtl.json).
The bounded [RV64IMA LR/SC matrix](../reports/riscv-dv-lrsc-profile-validation.json)
passed 11 packages across three memory layouts, with both word and doubleword
atomics. The [machine-mode mscratch matrix](../reports/riscv-dv-csr-profile-validation.json)
passed 10 packages across RV32I and RV64I. An
[RV64GCV capability probe](../reports/riscv-dv-vector-capability-probe.json)
ran on Spike and captured 16 vector-store bytes; V generation remains open.
The [single-AMO campaign](../reports/riscv-dv-amo-profile-validation.json)
passed 24 packages, and the [two-AMO campaign](../reports/riscv-dv-amo-pair-profile-validation.json)
passed 18. Together they executed all 18 word/doubleword AMO operations in
the pinned PyFlow model across shared, nonzero-base, and split layouts.
A separate [six-package custom RV64IMA target matrix](../reports/riscv-dv-atomic-custom-target-validation.json)
passed the LR/SC and both AMO profiles with an exact single-hart target file.
The adapter and current limits are described in the [integration guide](riscv-dv.md).
The [core corpus roadmap](riscv-dv-core-roadmap.md) prioritizes independent
RV32, RV64, and later vector validation targets.

## Phase 1 — Upstream and existing infrastructure (P0)

- [x] Identify the canonical [CLI](../riscv_test_runner/cli.py), sparse
  [package validator](../riscv_test_runner/core/package.py), existing
  [serial loader](../riscv_test_runner/core/serial_package.py), host mock,
  and JSON/JUnit conventions.
- [x] Inspect riscv-dv `run.py`, PyFlow, targets, simulator and ISS YAML,
  base test list, linker script, startup, and `tohost` termination.
- [x] Generate real programs with upstream PyFlow on Python 3.11 using the
  isolated [dependency list](../requirements-riscv-dv.txt).
- [x] Pin riscv-dv as a submodule at
  `f557b89ed6881a20515481a2585e9d004cd9642b`; retain upstream
  Apache-2.0 notices and `LICENSE.txt`.
- [x] Finish the [pinned PyFlow feature audit](riscv-dv-upstream-audit.md),
  covering coverage, directed streams, alternative backends, and whether
  limits originate upstream or in ProcessorCI.
- [x] Complete the [read-only cross-repository handoff audit](riscv-dv-upstream-audit.md)
  before any later RV-Bench adapter work. Preserve unrelated local changes.

## Phase 2 — Selectable test source (P0)

- [x] Expose `--tool riscv-dv` with ISA, target mapping, profile, seed range
  (`--seed` plus `--tests`), instruction count, output, backend, compiler
  prefix, Spike path, memory size, and a restricted upstream-option escape
  hatch. `--reset-pc` selects a word-aligned entry within the selected RAM.
  Generation is separate from device execution.
- [x] Use upstream `riscv_arithmetic_basic_test` and
  `riscv_rand_instr_test` rather than a ProcessorCI instruction generator.
  Record that PyFlow uses a subset of the latter's directed streams.
- [x] Add the upstream `riscv_jump_stress_test` profile with subprograms
  disabled; validate RV32I and RV64IMC software execution at 200 instructions.
- [x] Run named ISA/profile/seed configurations from a JSON matrix, preserving
  per-config and per-seed reports. The [example matrix](../examples/riscv-dv/config-matrix.json)
  passed with four configurations and eight programs; the
  [original five-ISA cross product](../examples/riscv-dv/isa-profile-matrix.json)
  passed with 15 configurations and 15 programs. RV64I and the hazard profile
  have separate multi-seed campaigns.
- [x] Document and smoke-check RV32I, RV32IM, RV32IMC, RV64I, RV64IM, RV64IMC,
  RV64IMFDC, and bounded RV64IMA LR/SC;
  reject unvalidated ISA and backend requests. The package ISA also states
  the required Zicsr and Zifencei extensions unless the CSR-free mode is used.
- [x] Validate the optional `--load-store` path in a 10-program RV32I random
  campaign at 100 instructions. Eight programs committed stores and received
  memory checks. This path requires misaligned access support.
- [x] Validate random, jump, and load/store configurations at 1,000
  instructions; preserve all four results in the tracked long-profile summary.
- [x] Stabilize the upstream `riscv_unaligned_load_store_test` random and
  hazard streams with isolated pinned PyFlow fixes: reject `x0` as a base,
  deep-copy instruction templates, and enable halfword/word accesses in
  unaligned mode. All 50 new seeds across the original five ISAs passed
  generation, compilation, Spike, package, and host-mock validation; 49
  executed at least one misaligned wide access. Five
  [RV64I seeds](../reports/riscv-dv-rv64i-hazard-validation.json) also passed
  and each executed a misaligned wide access.
  Compressed generation is disabled for this profile, including on C ISAs.
- [ ] Stabilize the upstream loop profile. Its timed PyFlow probe did not
  finish. A source audit also found that pinned PyFlow randomizes arbitrary
  instructions for loop initialization and update and inserts a reference to
  its own loop list. Repair needs upstream generator work; no loop support is
  claimed. The [loop/backend audit](../reports/riscv-dv-loop-vector-backend-audit.json)
  records the exact source blockers.
- [ ] Evaluate F/D, A, privileged, V, and specialized Z configurations
  individually before adding them to the supported matrix. Do not infer
  support from an upstream target name alone.
  - [x] RV64I: stage a derived base-I PyFlow target and pass five seeds each
    of arithmetic, random, and jump through the full software pipeline.
    `readelf` confirms RV64I/Zicsr/Zifencei with no M/C in all 15 ELFs.
  - [x] RV64IMFDC F/D: derive a pinned target without A, enable `mstatus.FS`,
    capture all 32 FPRs and `fcsr` from Spike, and self-check them at
    `test_done`. A [10-seed software campaign](../reports/riscv-dv-rv64imfdc-profile-validation.json)
    passed generation, compilation, Spike, packaging, and host mock with 501
    committed floating instructions and no atomics. A wrong expected FPR
    fails completion. No FPU core RTL or FPGA run is claimed.
  - [x] Add the RV64IMFDC arithmetic profile with floating generation and the
    same FPR/`fcsr` oracle. Five seeds passed the
    [software campaign](../reports/riscv-dv-rv64imfdc-arithmetic-validation.json).
  - [x] Add RV64IMFDC jump stress with floating generation and the same
    FPR/`fcsr` oracle. The [10-package matrix](../reports/riscv-dv-rv64imfdc-jump-validation.json)
    passed shared, nonzero-base, and split layouts. Every seed executed a
    jump and floating instructions before completion; the campaign recorded
    378 jumps, 778 floating instructions, and no atomics. Random branches are
    disabled so the directed jump stream executes.
  - [ ] Expand F/D to further ISA/profile combinations and an FPU-equipped DUT.
  - [x] A bounded LR/SC slice: repair the pinned PyFlow stream in an isolated
    copy, derive exact RV64IMA target settings, and package one aligned
    adjacent LR/SC pair. Both permitted SC outcomes leave RAM unchanged;
    exclude only the SC destination from the fixed GPR oracle. The
    [11-package matrix](../reports/riscv-dv-lrsc-profile-validation.json)
    passed across shared, nonzero-base, and split layouts, with five LR/SC.W
    and six LR/SC.D programs. A wrong expected
    GPR fails; original source and compatibility copies are hash-checked.
  - [x] Add bounded single-hart AMO profiles with one or two operations from
    the upstream stream. Isolated fixes bind the base register and select the
    actual AMO category; Spike-derived GPR and memory checks cover each
    deterministic result. The [24 single-AMO packages](../reports/riscv-dv-amo-profile-validation.json)
    and [18 two-AMO packages](../reports/riscv-dv-amo-pair-profile-validation.json)
    passed across three memory layouts and together exercised all 18 pinned
    word/doubleword AMO operations. A wrong expected memory byte fails.
  - [x] Extend the same bounded single-hart stream to three aligned AMOs.
    The [12-package matrix](../reports/riscv-dv-amo-triple-validation.json)
    passed across three memory layouts, with three executed stores per seed.
  - [ ] Broaden A to longer and multi-hart atomic streams, memory ordering
    outcomes, and a suitable DUT. The validated AMO profiles assume one hart
    and no competing memory writer.
  - [x] Privileged bounded CSR slice: package upstream directed
    `riscv_csr_test` for full-width machine-mode `mscratch` on RV32I/RV64I,
    with isolated `bitstring` compatibility, saved map and generator hashes,
    Spike completion, and host-mock verification. The
    [10-package matrix](../reports/riscv-dv-csr-profile-validation.json)
    passed; a wrong expected CSR value fails.
  - [x] Add aligned `mepc` to the bounded directed CSR map alongside
    `mscratch`. The [10-package matrix](../reports/riscv-dv-csr-expanded-validation.json)
    passed RV32I/RV64I; a wrong expected `mepc` value fails.
  - [ ] Broaden privileged/MMU support to illegal-instruction generation,
    trap entry/return, more CSRs and privilege modes, and memory translation.
    The [active illegal probe](../reports/riscv-dv-advanced-profile-audit.json)
    still fails in pinned PyFlow randomization.
  - [ ] V: confirm a working upstream backend and vector-capable compiler,
    Spike, F/V signature, and selected vector core configuration. The
    [capability probe](../reports/riscv-dv-vector-capability-probe.json)
    compiled and ran RV64GCV vector arithmetic on Spike and captured all 16
    committed vector-store bytes. The pinned PyFlow tree lacks a V instruction
    model and V-enabled target. The pinned SV target has a V model, but its
    Verilator configuration requires a UVM source tree; `UVM_HOME` and that
    source are absent locally. No V generated package is enabled; see the
    [backend audit](../reports/riscv-dv-loop-vector-backend-audit.json).
  - [x] Validate a bounded RV32IMC_Zbb arithmetic profile with an isolated
    target that filters pinned draft RV32B down to 12 ratified mnemonics.
    The [10-package matrix](../reports/riscv-dv-zbb-validation.json)
    passed the exact compiler ISA, Spike, packaging, and host mock across
    three memory layouts, executing 202 Zbb instructions. The target file
    and its digest are saved with each package.
  - [ ] Other specialized Z and RV32E: the
    [RV32IMCB probe](../reports/riscv-dv-specialized-profile-audit.json)
    generated real PyFlow assembly, but exact-ISA compilation rejected 21
    draft or extension-specific B instructions before filtering. The pinned
    PyFlow tree has no RV32E target or ISA group. Other ratified Z subsets
    still need separate compiler, Spike, package, and core validation.
- [x] Provide bounded custom-target paths: RV64I stages pinned RV64IMC
  settings with M/C removed; RV64IMFDC stages pinned RV64IMAFDC settings with
  A removed; RV64IMA stages pinned RV64IMAFDC settings with F/D/C removed.
  All three validate real programs.
- [x] Accept a user YAML test list for the four validated PyFlow profiles.
  Check allowed options and directed streams, save the input YAML and digest
  in each package, and allow `testlist` in a configuration matrix. The
  [five-configuration example](../reports/riscv-dv-custom-testlist-validation.json)
  passed nine of nine programs, including two unaligned seeds and one F/D seed.
- [x] Accept a user-supplied PyFlow `riscv_core_setting.py` with
  `--target-settings` and matrix `target_settings`. Check XLEN, exact ISA
  groups, bare machine mode, single hart, V disabled, and the required
  unaligned policy before staging. Save the input settings and SHA-256 with
  each package. The [four-program custom-target campaign](../reports/riscv-dv-user-target-validation.json)
  passed PyFlow, compiler, Spike, package, and serial host mock.
- [x] Allow exact RV64IMA user target settings for the bounded atomic
  profiles. The [six-program matrix](../reports/riscv-dv-atomic-custom-target-validation.json)
  passed LR/SC, one-AMO, and two-AMO profiles across shared, nonzero-base,
  and split layouts. The validator rejects missing A groups and multiple
  harts, and each package hashes the supplied target.
- [ ] Validate additional core-specific target settings and any feature that
  changes the ISA, privilege model, memory map, or oracle before enabling it.

## Phase 3 — ProcessorCI package adapter (P0)

- [x] Save original assembly, checked assembly, linked ELF, byte-addressed
  instruction and data images, manifest, generation options, seed, revision,
  tool versions, and source/ELF/image hashes.
- [x] Reuse schema version 1 with `selfcheck_tohost` and the existing sparse
  loader. Read LOAD segments and entry from the ELF, check RAM bounds, and
  verify image bytes against manifest memory in the integration test.
- [x] Use upstream bare machine-mode startup with a configurable linker layout;
  require `mhartid`/Zicsr and Zifencei. Reach `tohost` only
  after the Spike-derived register checks complete.
- [x] Reject unsupported privileged/runtime options through the CLI's safe
  option set; retain a full-ISA requirement in each manifest.
- [x] Detect when checks shift the linker data layout, fix `tohost` placement,
  relink both ELFs, and rerun Spike. A 1,000-instruction load/store seed with
  26 committed memory bytes passed this path.
- [x] Add a selected reset PC within the configured RAM. The Ibex
  `0x80` entry matrix passed five PyFlow, Spike, package, host-mock, and RTL
  runs; a [saved example package](../examples/riscv-dv/ibex-rv32i-seed9700/manifest.json)
  retains the exact linker layout and image.
- [x] Add nonzero, 4 KiB-aligned RAM bases and offset reset PCs. Five
  [cross-ISA configurations](../reports/riscv-dv-memory-portability-validation.json)
  passed generation, Spike, package verification, and serial host mock.
- [x] Export disjoint instruction and data address ranges with separate
  `imem.hex` and `dmem.hex`, explicit `memory_layout`, and saved-package
  checks. Three [split configurations](../reports/riscv-dv-memory-portability-validation.json)
  passed the software pipeline. The host mock uses the same flat address
  space; physical split-port loading remains for later core integration.
- [x] Add a single-hart CSR-free startup mode that substitutes zero for the
  upstream `mhartid` read, excludes CSR and fence instructions, and compiles
  against the exact base ISA. Preserve and hash the upstream assembly alongside
  the adapted source. The [portability matrix](../reports/riscv-dv-csr-free-portability-validation.json)
  covers RV32I, RV32IMC, RV64I, and an RV32I load/store program in software.
- [ ] Validate the CSR-free package on a configured PicoRV32 core and its
  actual memory/completion interface during later core integration.
- [ ] Add a core-specific split-port loader and overlapping Harvard address
  spaces if a later core requires them.
- [x] Verify selected saved packages on CV32E40S plus Controller RTL with an
  acknowledged `tohost` write stop, cycle limit, and status classification.
  Four positive packages passed; a corrupted expected register reached
  `tohost=3` and was classified as `SELF_CHECK_FAILURE`. Two packages also
  passed full Controller UART segment upload and execution. These are RTL
  simulations, with no FPGA result.
- [ ] Verify the same packages on physical hardware when available.
- [x] Replay five `0x80`-entry packages on Ibex plus Controller RTL with a
  simulation-staged shared RAM and byte-enable wrapper. RV32I, RV32IM,
  RV32IMC, jump stress, and a load/store seed passed. The load/store seed
  checked seven committed memory bytes. This does not establish the unchanged
  RV-Bench Ibex wrapper or physical FPGA behavior.

## Phase 4 — Reference and correctness checking (P0)

- [x] Execute the raw ELF on Spike, read committed integer registers at
  `test_done`, insert comparisons for 30 GPRs, compile a checked ELF, and
  require its Spike run to write `tohost=1`.
- [x] Confirm that corrupting an expected GPR makes the checked program fail
  reference completion. Keep Spike, package, host-mock, and hardware statuses
  distinct; report `hardware_validated: 0` for the software campaigns.
- [x] Add a selected-memory signature from committed Spike stores. Check up to
  64 written bytes by default after GPR checks; reject an intentionally
  corrupted expected byte in the real PyFlow/Spike test.
- [x] Make the memory signature limit configurable from 1 to 1024. A
  [store-heavy example](../reports/riscv-dv-memory-oracle-validation.json)
  compares 64 sampled bytes with all 187 committed written bytes.
- [x] Parse committed AMO writes in Spike traces and retain their final
  memory bytes. A manual `amoadd.w` smoke passed the compiler, Spike, and
  four-byte reference-memory check. The bounded LR/SC generator profile now
  also checks memory bytes shared by both SC outcomes.
- [x] Parse every committed element of a unit-stride vector store in the Spike
  trace. A real RV64GCV probe captured four 32-bit elements (16 bytes).
- [ ] Add richer architectural state checks for later profiles. The current
  signature checks GPRs and, for RV64IMFDC, all 32 FPRs and `fcsr`. Other
  CSRs outside bounded `mscratch`/`mepc`, V state, and the upstream jump scratch register remain unchecked;
  memory bytes beyond the selected limit remain unchecked.
- [x] Document and enforce both permitted outcomes for the bounded LR/SC
  profile. Its SC writes back the LR value, so success and failure both leave
  RAM unchanged. Exclude the SC destination, check stable GPRs and RAM, and
  retain the Spike-observed outcome in the package.
- [x] Check deterministic single-hart AMO results using all GPRs except the
  upstream jump scratch and the final committed memory bytes. One- and
  two-operation streams have negative memory-oracle tests.
- [ ] Define outcome policies for broader atomic, exception, and other
  nondeterministic profiles before enabling them.
- [x] Classify Spike traps before `test_done` with cause and PC in per-seed
  reports. Current supported programs use bare machine-mode completion.
- [ ] Define expected trap/handler behavior for future privileged profiles.

## Phase 5 — Coverage, campaigns, and reports (P1)

- [x] Record per-seed profile, ISA, seed, options, ELF hash, result stage,
  elapsed time, and a reproduction command; record upstream revision and
  compiler/Spike versions at campaign level and source/image hashes in each
  manifest. Failed seeds are reported without automatic retry.
- [x] Produce per-campaign JSON and JUnit reports plus the tracked
  [four-campaign summary](../reports/riscv-dv-validation.json).
- [x] Probe upstream `cov.py` on a normalized Spike reference trace. The
  [probe record](../reports/riscv-dv-coverage-probe.json) has a nonempty
  report; raw traces produce zero rows because of the upstream trampoline
  assumption.
- [x] Export optional upstream PyFlow coverage from a normalized Spike trace,
  labeled `spike_reference_execution` in the manifest and per-seed report.
  One RV32I seed passed the [full coverage path](../reports/riscv-dv-reference-coverage-validation.json);
  no DUT coverage is claimed.
- [x] Add structured `unsupported` rows for rejected configurations in matrix
  reports; later rows continue. Single-run preflight still exits directly.
- [x] Add `manifest_sha256` to new per-seed reports and a read-only
  `--verify-package` path that checks the manifest digest plus saved assembly,
  ELF, and image hashes. Historical campaign reports predate this field.

## Phase 6 — Software validation (P0)

- [x] End-to-end smoke: upstream generation, compilation, Spike reference,
  package validation, serial host mock, and same-seed reproducibility.
- [x] Representative campaigns: 100 RV32I arithmetic, 10 RV32I random,
  10 RV32IMC random, and 10 RV64IMC arithmetic programs, all software
  validated. RV32IM and RV64IM have separate one-program smokes.
- [x] Exercise invalid ISA/backend/options, missing Spike, too-small RAM,
  malformed entry, incorrect register expectation, failed status, and host
  timeout paths in the [adapter tests](../validation_tests/test_riscv_dv.py).
- [x] Run the legacy phase-one and riscv-dv suites together: 71 passed and
  ten optional tests skipped. Run the riscv-dv suite with PyFlow and Spike:
  32 passed. Existing directed tests and packages remain available.
- [x] Automate missing compiler and Spike preflight failures.
- [x] Detect corruption of a saved package image and an incorrect expected
  manifest digest in the adapter tests.
- [x] Detect missing PyFlow imports before starting a campaign and exercise
  that preflight in the adapter tests.
- [x] Reject a synthetic Spike illegal-instruction trap with a structured
  cause and PC before generated completion.
- [ ] Classify and validate expected trap-handler completion for future
  privileged profiles.
- [x] Run a 10-program RV32I load/store campaign at 100 instructions with
  explicit memory checks; preserve all seed results in the tracked summary.
- [x] Run the four-configuration matrix through PyFlow, Spike, packaging, and
  the host mock: eight of eight programs passed, zero hardware runs.
- [x] Smoke the original five ISAs against arithmetic, random, and jump
  stress profiles: 15 of 15 programs passed the software pipeline.
- [x] Validate RV64I with a derived target: five seeds each of arithmetic,
  random, and jump passed; five additional hazard seeds also passed.
- [x] Validate RV64IMFDC with a derived target: ten random seeds passed the
  full software path with FPR/`fcsr` self-checks. A corrupted expected FPR
  fails on Spike, and a changed startup file fails saved-package verification.
- [x] Validate RV64IMFDC jump stress across three memory layouts: ten of ten
  PyFlow, compiler, Spike, package, and host-mock results passed. Each raw
  reference executed jumps and F/D instructions before `test_done`.
- [x] Validate bounded RV64IMA LR/SC across three memory configurations:
  eleven of eleven PyFlow, compiler, Spike, package, and host-mock results
  passed. Five used LR/SC.W and six used LR/SC.D. All eleven committed a
  successful SC on Spike; packages accept
  either architectural outcome. A wrong GPR expectation fails completion.
- [x] Validate one- and two-AMO streams across three memory configurations:
  24/24 and 18/18 packages passed the software pipeline. The two-operation
  campaign committed 36 AMO stores; the combined campaigns exercised all 18
  pinned word/doubleword AMO operations.
- [x] Validate three-AMO streams across three memory configurations: 12/12
  packages passed, each with three Spike-observed stores and checked RAM.
- [x] Validate `mscratch` plus aligned `mepc` on RV32I and RV64I: 10/10
  directed packages passed, and a wrong expected `mepc` fails.
- [x] Validate filtered RV32IMC_Zbb arithmetic across three memory layouts:
  10/10 packages passed with 202 executed Zbb instructions.
- [x] Validate bounded machine-mode mscratch CSR packages: ten of ten passed
  across RV32I and RV64I, with a wrong CSR expectation rejected on Spike.
- [x] Run an RV64GCV vector arithmetic and store probe on Spike; all four
  committed 32-bit elements were captured by the reference parser. This is
  capability evidence, not a generated package profile.
- [x] Run a custom YAML test-list matrix across five ISA/profile combinations:
  nine of nine passed, and saved-list tampering is rejected.
- [x] Validate the fixed unaligned hazard profile across five ISAs: 50 of 50
  seeds passed and 49 executed a misaligned wide access on Spike.
- [x] Run a four-configuration 1,000-instruction matrix, including a
  branch-restricted load/store seed that actually committed stores.
- [x] Run a five-seed, 1,000-instruction load/store campaign with executed
  stores in every seed and one stable-layout fallback.
- [x] Run five 1,000-instruction RV32IMC random programs without load/store
  constraints; all passed the software pipeline.
- [x] Add the adapter's dependency-free tests to
  [offline CI](../.github/workflows/offline-verification.yml) with the pinned
  riscv-dv submodule.
- [ ] Add a CI job with PyFlow dependencies, a matching compiler, and Spike
  that actually generates and executes programs. The offline job skips the
  optional real PyFlow tests. Lower priority at this stage.

## Phase 7 — Documentation and later core use (P1)

- [x] Document setup, pinned revision/license, CLI, package contents,
  compatibility matrix, Spike oracle, reproducing seeds, saved packages,
  limitations, and a complete example.
- [x] Select CV32E40S for initial RV32IMC RTL validation and test its
  Controller completion path, including a misaligned load/store package.
- [x] Validate an additional core profile in RTL: Ibex with five selected
  saved packages, the `0x80` entry, and a ProcessorCI simulation-staged
  wrapper. Keep the original adjacent core and wrapper checkouts read-only.
- [ ] Validate further core profiles and physical hardware when available.
  Defer additional device evidence to later RV-Bench work.
- [ ] After a core profile and device behavior are verified, add the separate
  RV-Bench adapter and per-core selection. Keep riscv-dv generation in
  ProcessorCI Tests.

## First software-integration acceptance gate

- [x] A real riscv-dv program was converted into a compatible package.
- [x] The program compiled; Spike supplied independent expected values and
  validated the checked ELF.
- [x] The package passed the existing serial-loader host mock.
- [x] A nontrivial random branch/jump profile passed end to end.
- [x] A 100-program supported-ISA campaign passed software validation.
- [x] Directed-test regression, limitations, commands, and saved example
  artifacts are recorded.
- [x] All reports keep FPGA validation at zero. CV32E40S core RTL execution
  is recorded separately from host-mock and FPGA results.

**Scope guard:** Continue using upstream riscv-dv streams and existing
ProcessorCI package/communication code. Do not add a new random generator,
ISA implementation, NTV change, UART command, or RTL mutation workflow as
part of this checklist.
