# Pinned riscv-dv PyFlow and repository handoff audit

This audit covers riscv-dv commit `f557b89ed6881a20515481a2585e9d004cd9642b`
and the adjacent ProcessorCI checkouts inspected on 16 November 2026. It
records what the current ProcessorCI Tests adapter has exercised. The
[integration checklist](riscv-dv-checklist.md) tracks implementation work.

## Generator features at the pinned revision

| Feature | Upstream evidence | ProcessorCI result and limit |
| --- | --- | --- |
| Python generator | `yaml/simulator.yaml` selects `pygen/pygen_src/test/<test_name>.py`; `run.py` passes the selected `gen_test`, target, seed, and options. | Python 3.11 with the pinned dependencies generated real RV32I/IM/IMC and RV64I/IM/IMC programs. The adapter requires the pinned revision and uses one upstream invocation per seed. |
| Bare machine-mode program | PyFlow's base test and upstream linker/runtime generate the startup, stack, data pages, and `test_done` path. | The adapter changes the linker base to zero, keeps the upstream runtime, disables CSR/EBREAK/WFI generation, and verifies completion with Spike. Other privilege modes and trap profiles require separate runtime and oracle work. |
| Arithmetic and random streams | `yaml/base_testlist.yaml` supplies the profiles. The random profile lists seven directed streams. | The arithmetic profile and a supported subset of random streams pass software campaigns. The adapter keeps upstream jump and optional load/store streams. The full random list is unavailable in this PyFlow path. |
| Jump stress | The base test list selects `riscv_jal_instr`; PyFlow's factory registers it. | One seed for each supported ISA passed at 200 instructions. The adapter forces `num_of_sub_program=0` because the pinned PyFlow `gen_callstack` path raises `AttributeError: callstack_gen`. |
| Other directed streams | PyFlow's factory registers numeric corner, load/store random/hazard, and loop streams; the base list also names multi-page and memory stress streams. | The factory lacks several streams in the full random list. The initial unaligned hazard probe passed four of ten seeds. Isolated compatibility copies now prevent `la x0`, prevent shared instruction-template register changes, and enable wide unaligned accesses; 50 of 50 new seeds passed. Compressed generation is disabled for this profile. A loop-profile probe did not complete within 30 seconds even at 50 instructions and zero subprograms. Its pinned implementation also contains unconstrained loop initialization/update and a self-reference in the loop list. Multi-page profiles remain unvalidated. |
| More ISAs | Upstream documentation lists RV32/64 IMAFDC and more privileged features; target directories include F/D, B, and V configurations. | ProcessorCI accepts six integer ISAs, RV64IMFDC, bounded RV64IMA atomic profiles, and filtered RV32IMC_Zbb arithmetic. RV64I derives from RV64IMC with M/C removed; 15 arithmetic/random/jump seeds passed. RV64IMFDC derives from RV64IMAFDC with A removed; FPRs and `fcsr` are checked. RV64IMA derives from RV64IMAFDC with F/D/C removed; 65 atomic packages passed across LR/SC and one-, two-, and three-AMO profiles. Multi-hart A, other F/D combinations, and V generation remain open. |
| Alternative backend | `yaml/simulator.yaml` includes Verilator and commercial SystemVerilog/UVM commands. Upstream documentation describes UVM 1.2 simulator prerequisites. | No alternate backend has passed this adapter's generate/compile/Spike/package pipeline. The Verilator entry still requires a working UVM build and tool setup. PyFlow remains the validated software backend. |

These limits have different owners. The missing PyFlow stream registrations,
subprogram call-stack error, and loop timeout occurred in the pinned upstream
generator. ProcessorCI's ISA allowlist, selected RAM mapping,
two-stream random selection, and integer/memory oracle are adapter validation
boundaries. The adapter reports profile reductions in each manifest.
The [unaligned profile report](../reports/riscv-dv-unaligned-experimental-validation.json)
retains every exploratory seed and its last completed stage.
The [compatibility campaign](../reports/riscv-dv-unaligned-compat-validation.json)
records 50 successful seeds and their independently observed memory accesses.
A [custom test-list campaign](../reports/riscv-dv-custom-testlist-validation.json)
passed nine seeds across five ISA/profile configurations. The adapter validates
the selected YAML entry and saves its digest with each package; arbitrary
directed streams remain outside this path. A later
[user-target campaign](../reports/riscv-dv-user-target-validation.json)
passed four programs with an exact-ISA, bare single-hart target settings
file saved and hashed in each package.
An [F/D runtime probe](../reports/riscv-dv-rv64fd-pyflow-probe.json) emitted
and compiled floating instructions. Its bare startup trapped at `fmv.d.x`;
setting `mstatus.FS` in a scratch startup ran 69 floating instructions to
`test_done` on Spike. The subsequent [RV64IMFDC campaign](../reports/riscv-dv-rv64imfdc-profile-validation.json)
validated 10 packages with FPR and `fcsr` signatures. No FPU RTL replay exists.
The later [RV64IMFDC jump matrix](../reports/riscv-dv-rv64imfdc-jump-validation.json)
validated ten more packages, with executed jumps and floating instructions in
every seed.
A [directed AMO probe](../reports/riscv-dv-rv64a-pyflow-probe.json) failed
inside PyFlow's `riscv_amo_instr_stream` constructor before assembly output.
An isolated repair of the pinned LR/SC stream now enables the bounded
[RV64IMA LR/SC package profile](../reports/riscv-dv-lrsc-profile-validation.json).
Further isolated fixes enable [single-AMO](../reports/riscv-dv-amo-profile-validation.json)
and [two-AMO](../reports/riscv-dv-amo-pair-profile-validation.json) streams.
The 42 AMO packages passed software validation and together exercised all
18 word/doubleword AMO operations in the pinned model. Their oracle assumes
one hart and no competing memory writer.
The [three-AMO matrix](../reports/riscv-dv-amo-triple-validation.json) adds
12 packages and 36 Spike-observed stores under the same single-hart oracle.
The separate pinned directed CSR Python generator, adapted in isolation for
`bitstring` 5, enables [mscratch packages](../reports/riscv-dv-csr-profile-validation.json).
An [expanded map](../reports/riscv-dv-csr-expanded-validation.json) also
validated 10 packages with aligned `mepc` reads and writes on RV32I/RV64I.
The [advanced-profile audit](../reports/riscv-dv-advanced-profile-audit.json)
retains the manual AMO evidence and the active illegal-instruction failure.
An [RV64GCV Spike probe](../reports/riscv-dv-vector-capability-probe.json)
compiled and executed vector arithmetic and recorded 16 vector-store bytes.
The PyFlow tree has no V instruction model or V-enabled target, so V package
generation still needs a working upstream SV/UVM path or upstream PyFlow support.
The pinned SV target `rv64gcv` and `src/isa/rv32v_instr.sv` provide a vector
model, but the local Verilator entry requires `$UVM_HOME/src/uvm.sv` and
`uvm_dpi.cc`; no UVM source tree is configured here. The
[backend audit](../reports/riscv-dv-loop-vector-backend-audit.json) records
this prerequisite and the structural PyFlow loop errors.
The [RV32IMCB probe](../reports/riscv-dv-specialized-profile-audit.json)
generated assembly, but compilation rejected 21 instructions from the pinned
draft B model. An isolated target now filters that model to 12 ratified Zbb
mnemonics. The [RV32IMC_Zbb matrix](../reports/riscv-dv-zbb-validation.json)
passed ten full software packages with 202 executed Zbb instructions. The
backend still has no RV32E target or ISA group; full draft B remains rejected.

## Coverage probe

Upstream `cov.py` supports PyFlow functional coverage from Spike trace CSV. Its
`scripts/spike_log_to_trace_csv.py` waits for a fetch at `0x1010` before
parsing instructions. The current Spike reference trace starts in reset ROM
at `0x08000000` and enters the generated program at PC zero; passed directly
to the converter, it produced zero instructions.

For one RV32I arithmetic seed, a probe dropped the reset ROM, inserted the
converter's `0x1010` marker immediately before PC zero, and stopped before
`test_done`. The marker was skipped by the converter. The upstream converter
then produced 145 trace rows and the upstream PyFlow model processed 114
instructions into a nonempty report with 147 coverage groups. The exact
trace/report hashes and counts are in the
[coverage probe record](../reports/riscv-dv-coverage-probe.json). This is
**Spike reference-execution functional coverage**. It includes generated
startup and executed test instructions and does not measure DUT or RTL
coverage. The adapter now exposes that normalization through optional
`--reference-coverage`; one RV32I seed passed the full path, recorded in the
[reference coverage validation](../reports/riscv-dv-reference-coverage-validation.json).

The probe also showed that `cov.py` launches a child `python3` from `PATH`;
the isolated PyFlow environment must be first on `PATH`. The upstream model
currently skips AMO coverage. Coverage scores that include unexercised ISA
groups need interpretation before being used as a campaign quality gate.

## Cross-repository handoff

The adjacent checkouts were inspected read-only. ProcessorCI Communication
(`ab95aacddf63`) provides the existing serial read/write and end-address
commands. ProcessorCI Controller (`f3c03a5c810f`) qualifies normal completion
on an acknowledged write to the configured status address; its interpreter
returns the `luck` completion packet and timeout bit used by
`riscv_test_runner.core.serial_package.run_package`. ProcessorCI Verification
(`0fa5ae409826`) remains outside this integration. RV-Bench (`24b192440013`)
has a separate core/wrapper selection flow for later use.

The current package runner accepts a selected RAM base and reset PC and an
aligned `tohost` word, with a 24-bit controller timeout. Packages declare
their exact ISA and memory requirements. A CSR-free single-hart mode avoids
Zicsr/Zifencei. Disjoint instruction/data packages have passed the flat
software host mock; physical split-port loading remains unvalidated.
Before using a generated package on a selected core, verify its memory map,
instruction support, `tohost` write acknowledgment, and real execution
response. No riscv-dv package has been run on a DUT or FPGA in this work.

The Communication, Controller, and RV-Bench checkouts had unrelated local
changes at audit time. This audit made no changes in those repositories.
