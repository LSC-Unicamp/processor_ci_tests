# Phase-one verification status

The local repository is an older ProcessorCI Tests revision. It has the legacy
`src/memory/reference` corpus, but no generated-test manifest implementation or
riscv-dv integration. The ACT submodule is pinned to
`241b1fe294567751bd3ae6f338b1dbfc40c41a20` (2025-10-16), which used
RISCOF. The submodule now points to the official ACT 4.1.0 release
`6e8a45123f14cebfb3df151a0e7b849b4389b33b` at the same path. Legacy
RISCOF-specific helper scripts were removed.

## What runs now

```sh
python3 tools/isa_audit.py --compile
python3 tools/validate_legacy_advanced_sail.py
python3 tools/validate_legacy_advanced_timer.py
python3 tools/audit_test_directories.py
python3 tools/build_basic_sail.py
python3 tools/build_invalid_sail.py
python3 tools/build_advanced.py
python3 tools/validate_advanced_sail.py
python3 tools/probe_vector_vstart.py
python3 tools/validate_vector_vlen.py
python3 tools/validate_act4_packages.py
python3 tools/build_act4.py --config third_party_repositories/riscv-arch-test/config/sail/sail-RVI20U64/test_config.yaml --output build/act4-rv64 --act-exe .venv-act4/bin/act
python3 tools/validate_act4_packages.py --output build/act4-rv64 --report reports/act4-rv64-summary.json
python3 tools/build_act4.py --config third_party_repositories/riscv-arch-test/config/sail/sail-rv32-max/test_config.yaml --output build/act4-rv32imc --extensions I,M,C --act-exe .venv-act4/bin/act
python3 tools/validate_act4_packages.py --output build/act4-rv32imc --report reports/act4-rv32imc-summary.json
python3 tools/combined_report.py
pytest -q validation_tests/test_phase1.py
python3 -m riscv_test_runner.cli --list --march rv32imc --suite basic,advanced
python3 -m riscv_test_runner.cli --list --march rv32ic_zicsr --suite invalid
python3 -m riscv_test_runner.cli --list --march rv32if_zicsr --suite advanced --scenario fp_dynamic_rounding_flags
```

Set `RISCV_TOOL_PREFIX=riscv64-unknown-elf-` when that cross toolchain is
installed instead of the default `riscv32-unknown-elf-`. The software-only CI
workflow installs QEMU, the cross toolchain, the pinned ACT configuration, and
Sail. It rebuilds basic, trap, and advanced software results and generates the
combined report. ACT package builds are a separate manual target.

The audit emits `reports/isa-audit/` with a machine-readable inventory, CSV,
missing instruction list, invalid-asset list, and summary. It counts real
source bodies separately from filename and hex presence. With `--compile` it
assembles supported RV32 sources, checks the intended disassembled opcode, and
compares rebuilt binary words with the checked-in image. No legacy source is
promoted to reference-validated solely because a hex file exists.
The CSV retains separate `legacy_compiled`, `legacy_image_matches_source`,
`legacy_reference_validated`, and `legacy_issue` fields alongside new package
evidence. The 76 inventoried legacy sources built in the current assembler
profile match their checked-in images. Sail replay of all 79 substantive old
RV32 sources matched 67 numeric references at the first address-60 write.
Eleven RV32A references are comment-only placeholders; the intentional
timeout has no completion write. Three more numeric RV32I references belong
to comment-only source placeholders (`fence`, `ecall`, `ebreak`).
`reports/isa-audit/legacy_basic_assets.json` and `legacy_basic_sail.json`
record the per-source classification and observed words. RV64, FP, and CSR
legacy sources are comment-only and cannot be replayed as old tests.

The [directory audit](../reports/isa-audit/test_directories.md) reconciles
all 23 ISA groups with 599 basic, 59 advanced, and 19 invalid package sources.
The package suites have no missing sources, and the current ISA directory audit
has no unresolved file gaps. The 80 RV32M legacy advanced programs and the two
RV32I control-flow programs now have numeric references matching independent
expected results and Sail's first write to address 60. Twelve divide-by-zero
M cases previously stored zero instead of their result; their sources and
images were corrected. Seven orphan comment-only references were removed.
The [legacy advanced replay](../reports/isa-audit/legacy_advanced_sail.json)
records each case. The timer source now reads the controller's `0xfffffffc`
counter address and self-checks two reads. Its image and reference match, and
the [timer report](../reports/isa-audit/legacy_advanced_timer.json) records a
passing timer RTL unit probe. A core/controller execution of the timer program
is still pending. All 147 comment-only legacy advanced triples were retired;
their paths are in `tools/legacy_advanced_retired.txt`. Each configured ISA
group now has at least one executable advanced package. Configured extra tests
are outside this audit's current scope.

The selected ACT DUT candidate is RV-Bench's pinned CV32E40S and curated
wrapper. Its directed machine-mode/IMC probe passes. A staged ACT 4.1 profile
with reset-zero entry and `tohost` completion builds 39 I and eight M ELFs; all 47 pass Sail
and host oracle checks. The RV-Bench wrapper now uses a 512 KiB shared,
byte-enabled controller memory; all 47 ACT packages fit its 508 KiB program
region and pass core/controller RTL simulation. The UART path uploads real ACT
segments and reads `tohost`; all 47 pass that full-load RTL replay too.
Injected ADDI mismatch, illegal-instruction trap and timeout cases exercise
the controller's distinct outcomes. ACT failure text, trap cause and EPC are
readable through the diagnostic window. The old board profile still fits
0/47 packages, and FPGA synthesis and execution remain unverified. The
staged UDB's detailed core capability claims still need review. See
[512 KiB integration](act4-cv32e40s-512k-integration.md),
[software results](../reports/act4-cv32e40s-software.json), and
[shared-memory fit results](../reports/act4-cv32e40s-fit-512k.json).
Inventory is based on the [20240411 ratified unprivileged ISA](https://docs.riscv.org/reference/isa/v20240411/unpriv/unpriv-index.html).
The legacy B, P and V directories were removed. B 1.0 coverage uses
Zba/Zbb/Zbs; optional Zbc and unique Zbkb forms are separate. The pinned
V opcode catalog identifies 259 RV32Zve32x forms, all of which now have
dedicated Sail-validated cases under a Zvl128b test profile. These cases
sample legal SEW 8/16/32, VL 4 and LMUL 1 settings, with temporary LMUL 2
setup for wide sources. The remaining 116 catalog forms require higher vector
profiles and do not count as missing Zve32x forms. All 112 additional forms
applicable to RV32 now have dedicated Sail-validated cases across Zve32f,
Zve64x, Zve64f and Zve64d. Four indexed EEW64 forms have separate RV64Zve64x
Sail-validated cases. The machine
report classifies
each by minimum Zve subset and XLEN. P remains excluded because
its v0.6 specification is developing. See [named extension profiles](z-extension-profiles.md).

`tools/build_basic_sail.py` creates 599 dedicated RV32/RV64 basic sources and
ELFs, confirms each target opcode in disassembly, executes each self-checking
program under Sail 0.13.1, and exports sparse packages. It checks that C
targets have 16-bit encodings and other targets have 32-bit encodings; each
package records the verified opcode hex and width. A deliberately forced
32-bit substitute for `c.addi` is rejected. The suite covers all defined
ordinary instructions in RV32/64 I/M/A/C/F/D/Zicsr plus the selected Z
subsets in the current inventory. There are 602 inventoried encodings: 599
ordinary Sail-validated cases and three separately validated trap encodings.
The three exceptional encodings ECALL, EBREAK, and C.EBREAK are in a separate
M-mode expected-trap suite, alongside a deliberately illegal instruction,
reserved CSR access, U-mode MRET and U-mode machine CSR access;
each checks `mcause` and `mepc` under Sail.
The trap handler publishes distinct `tohost` values for a missing trap, wrong
cause, and wrong `mepc`. The host oracle maps them to
`EXPECTED_TRAP_MISSING`, `UNEXPECTED_TRAP`, and `ARCHITECTURAL_MISMATCH`;
the serial mock confirms those classifications. A controller stop without a
status write remains inconclusive.
The U-mode tests configure PMP before dropping privilege; they run under the
Sail RV32 max profile, which permits the test program to fetch in U mode.
The invalid suite now checks RV32/RV64 FP instructions with FS disabled,
a vector instruction with VS disabled, a read-only CSR write, and RV32/RV64
misaligned AMOs. Sail reports store/AMO access fault (cause 7) for the AMO
cases under the selected configurations. Restoring legal FP/vector/alignment
state makes the expected-trap self-check fail. All 60 generic legacy invalid
source/image/reference triples were removed; three are linked to individual
packages in the [replacement map](../reports/isa-audit/invalid_replacements.json).
The [retirement record](../reports/isa-audit/legacy_invalid_retired.json)
identifies the other 57, which never defined an instruction or expected trap.
Sail returns nonzero when a deliberately
corrupted expected value is used. The outcomes are recorded in
`reports/basic-sail-summary.json` and merged into the instruction audit as
separate reference evidence. The bitmanip and vector Z cases use the upstream Sail RV32 max
software configuration; the earlier cases use the RVI20U32/U64 configuration.
Hardware compatibility still requires a real DUT map.

`tools/combined_report.py` reconciles the ISA inventory with the basic and
trap reports, checks that advanced QEMU and Sail IDs agree, and verifies ACT
package counts. The RV32 and RV64 ACT software samples have separate results.
It writes `reports/combined-summary.json`, a readable Markdown
summary, and `reports/combined-software.junit.xml`. ACT entries in that JUnit
file represent host-mock checks; they are not DUT execution results.

`tools/build_advanced.py` creates 59 deterministic RV32 and RV64 sources under
the ISA group they exercise (I/M/A/C/F/D/Zicsr and the selected Zve groups).
ELFs and QEMU validation artifacts are under
`build/advanced/`, checks target instructions in disassembly, and runs each
ELF with the matching QEMU user-mode emulator. Each test writes a 1 or 2 status word before
completion and exits with 0 or 1 for offline validation. The script records
the entry, status address, completion address, ISA, memory segments and scenario.
`tools/validate_advanced_sail.py` rebuilds the same scenarios for bare-metal
Sail with a `tohost` completion and independently checks all 59 architectural
outcomes. It writes 59 sparse packages under `build/advanced-sail/` using the
same self-checking schema as basic and ACT packages. Corrupted expected values
fail under both QEMU and Sail. These
software checks do not establish RTL or pipeline correctness.
The vector scenarios now check two EEW64 lanes, masked and tail undisturbed
lanes, `vstart` CSR write/read/reset, nonzero-`vstart` load and store resume,
e8 saturation with sticky `vxsat`, an e8 LMUL=2/VL20 group, fractional
LMUL=1/2 at e8/VL8, LMUL=8 at e16/VL40, `vxrm` rounding, and masked store
preservation. At VLEN128, the LMUL=2 and LMUL=8 cases cross vector register
boundaries. A VLMAX case checks SEW and LMUL ratios and AVL clamping without
assuming a fixed VLEN. Negative QEMU and Sail tests corrupt lane and state checks.
The FP32 reciprocal estimate basic cases also check their DZ flag. Advanced
cases check canonical NaN and `fflags.NV` for square root of −1, plus dynamic
`frm` changes between RTZ and RUP with exact integer conversions and `fflags.NX`.
Both QEMU and Sail reject a deliberately wrong first rounding mode.
A separate nonzero-`vstart` arithmetic probe passes QEMU and Sail when
Sail's `zero_required.arith` option is disabled. The pinned strict Sail max
configuration traps by design, so arithmetic resume remains a conditional
capability outside the ordinary advanced count. The [probe record](../reports/vector-vstart-discrepancy.md)
and [machine report](../reports/vector-vstart-summary.json) show both settings.

The [VLEN128 report](../reports/vector-vlen128-summary.json) replays all 375
basic vector forms and fourteen advanced vector scenarios at VLEN=128, using both
full V and the matching Zve32x, Zve32f, Zve64x, Zve64f, or Zve64d Sail support
level with ELEN=32 or 64. All 389 passed both configurations. The named-Zve
replay disables optional Zv extensions inherited from the ACT Sail max base
configurations. This verifies a second VLEN and the modeled Zve capability;
it does not cover all vector parameters, state transitions, or a real core.

The serial CLI now selects exact XLEN and extension directories and can list
tests without importing the serial package or connecting to a board. Serial
and package host selection resolve B and V aliases, the Zve capability ladder,
Zvl lengths, and implied F/D/Zicsr dependencies. These checks use advertised
ISA strings; they still need comparison with a selected core's actual RTL.
The CLI also lists ISA-compatible invalid trap packages and supports exact
`--instruction`, `--scenario`, `--category`, and `--test-id` filters offline.
Suite names select the test source. Serial execution remains limited to the
legacy basic level, and filtered serial runs are rejected. A new canonical
host adapter can clear and load zero-based sparse packages and read back the
status word; its command sequence has only been tested with a mock device.
The existing controller
API returns an eight-byte response with a completion/timeout bit but no decoded
trap cause. Enabling advanced or invalid packages for
serial execution could turn a timeout or trap into a false pass. Advanced
packages therefore remain offline packages until stop-cause handling and
loading are verified with the controller.
The neighboring interpreter's RTL protocol testbench passes burst access,
breakpoints, early completion and timeout. A Verilator probe of the actual
controller RTL now qualifies normal-mode completion with an acknowledged
write on either memory bus. The adapter checks the reply's cycle count and
reads `tohost`; decoded stop and trap reasons and real-device loading still
need validation before a controller DUT PASS can be trusted. See the
[controller RTL report](../reports/controller-rtl-protocol.json).

## ACT4 adapter boundary

The inspected [ACT4 framework](https://github.com/riscv/riscv-arch-test/tree/act4)
requires `test_config.yaml`, a UDB DUT YAML, `rvmodel_macros.h`, a linker
script, and a Sail reference model. ProcessorCI's per-core JSON configs,
`processorci_top` wrappers and board definitions provide reusable ISA, bus,
boot and memory inputs, but not the full privilege/CSR/trap profile or a
compatible ACT memory layout. The [DUT infrastructure audit](act4-dut-infrastructure-audit.md)
records the exact sources and gaps. The official Sail RVI20U32 software
configuration was used for the initial integration run.

The pinned [ACT 4.1.0 release](https://github.com/riscv/riscv-arch-test/releases/tag/4.1.0)
is at `third_party_repositories/riscv-arch-test`. After installing the
release's documented dependencies, run `python3 tools/build_act4.py` to build
its RV32 `I` tests with the upstream `sail-RVI20U32` software configuration,
derive self-checks through Sail, and convert the resulting ELFs. This software
configuration is for exercising the ACT4 pipeline; it does not advertise a
ProcessorCI FPGA core's capabilities. Sail 0.13.1, Bundler and the
`riscv64-elf-gcc` toolchain are installed locally. The Arch Ruby installation
lacked ERB; a local ERB gem was supplied through `RUBYLIB`. ACT 4.1 then built
39 RV32 I self-checking ELFs after Sail signature generation, converted all 39
to sparse packages, executed all 39 directly with Sail, and the host mock
validated their status handling. The
build output is `build/act4/` and the checked-in summary is
`reports/act4-summary.json`. See [Sail and ACT4 setup](install-sail-act4.md).
The official Sail RVI20U64 sample also built 51 RV64 I ELFs and packages;
all 51 passed direct Sail execution and host checks. Its artifacts are under
`build/act4-rv64/` and its separate report is
`reports/act4-rv64-summary.json`.
The Sail RV32 max sample generated 47 tests when I, M and C were requested:
39 I, eight M and zero C. All 47 passed Sail and host checks. The pinned ACT
4.1 test tree has no C sources, so this is I/M evidence for a software sample,
not ACT C coverage. Its report is `reports/act4-rv32imc-summary.json`.
Initialize it after cloning with
`git submodule update --init third_party_repositories/riscv-arch-test`.

`tools/act4_package.py` converts a built ACT4 ELF with a `tohost` symbol into
sparse segments and an explicit self-checking oracle. Status 1 means PASS;
odd values greater than 1 mean self-checking failure. Timeout and unexpected
trap take precedence over the status value; a breakpoint alone is inconclusive.
The converter rejects malformed ELFs and missing `tohost`. The converter does
not alter upstream normative checks. `riscv_test_runner/core/package.py`
validates sparse segments and maps observed status, timeout, and traps to
distinct host outcomes. A synthetic ACT-style ELF exercises the converter and
mock; this is separate from the 39 generated ACT ELFs. The adapter still
requires a controller path that can observe the write and stop reason.

## Remaining gates

1. Expand vector parameter, state, masking, tail, fault and flag coverage for
   a selected core profile.
2. Validate the selected core's privilege, FP, memory and trap capabilities
   against its RTL before claiming applicable coverage.
3. Provide the core's ACT 4.1 UDB, linker map, macros and Sail config; run
   the built self-checking ELFs on that core or its RTL simulator.
4. Add controller support for sparse segments, explicit completion/status,
   and decoded timeout/trap results before serial package execution.
5. Run RTL and FPGA validation when hardware becomes available.

The phase is **incomplete**: 599 ordinary basic package tests and nineteen invalid
trap tests (three in the basic inventory) were Sail-validated. ACT 4.1
generated 39 RV32 I, 51 RV64 I, and 47 RV32 I/M software-target tests; all
passed Sail execution and package host checks. The 59 advanced scenarios passed
QEMU and Sail.
No hardware result exists.

See [Maintaining the suites](adding-tests.md) for case authoring, rebuilding,
failure reproduction, and real DUT configuration requirements.
