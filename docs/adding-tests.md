# Maintaining the directed and ACT suites

Run commands from the `processor_ci_tests` directory. Install the toolchain and
Sail as described in [Sail and ACT setup](install-sail-act4.md). On a system
using `riscv64-unknown-elf-` tools, set `RISCV_TOOL_PREFIX` and
`BASIC_RISCV_GCC=riscv64-unknown-elf-gcc` before rebuilding.

## Basic instruction cases

`tools/basic_cases.py` defines each ordinary case as `(group, instruction,
march, expected_a0, assembly_body)`. Add a dedicated case to that table, with
the exact target mnemonic and a hand-specified expected architectural value.
Bitmanip Z cases are in `tools/extension_cases.py`. RV32Zve32x cases are in
`tools/extension_cases.py` and `tools/vector_cases.py`; higher integer vector
cases are in `tools/vector_higher_cases.py`, and vector FP cases are in
`tools/vector_fp_cases.py`. Their inventory is derived independently from the
pinned `tools/vector_opcode_candidates.txt` catalog by
`tools/extension_profiles.py`. The
[named extension profiles](z-extension-profiles.md) describe bitmanip and
vector scope and why P is excluded.
Initialize every register and memory location read by the body. For A cases,
check only architecturally permitted outcomes. For F/D cases, initialize FP
state and check raw result bits or required flags. Use a `march` that includes
the instruction's dependencies.

```sh
python3 tools/build_basic_sail.py
python3 tools/build_dut_smoke.py
python3 tools/validate_legacy_basic_sail.py
python3 tools/validate_legacy_advanced_sail.py
python3 tools/validate_legacy_advanced_timer.py
python3 tools/isa_audit.py --compile
python3 tools/audit_test_directories.py
```

The build regenerates `tests/<group>/basic/package_src/<instruction>.S`,
assembles an ELF, checks the target opcode in disassembly, executes the check
under Sail, and writes a sparse package to `build/basic-sail/`. It requires a
16-bit target encoding for C cases and a 32-bit encoding for the other groups;
the package records `instruction_bits` and `target_opcode_hex`. The audit
compares the package result with its inventory. Check the row in
`reports/isa-audit/instruction_inventory.json` and the execution row in
`reports/basic-sail-summary.json`. The package source is generated from the
case table; edit the table first and rebuild.

After building both the basic and advanced Sail suites, run
`python3 tools/validate_vector_vlen.py`. It replays every selected Zve ELF at
VLEN=128, the minimum claimed by these packages, once with full V and once
with the corresponding named Zve support level and ELEN. Optional Zv
extensions in the ACT Sail max base configurations are disabled for the named
Zve replay. The results are in `reports/vector-vlen128-summary.json`.
These software configurations still do not describe a particular DUT.

The legacy replay uses the pinned Sail RV32 max model with 64 KiB RAM at
address zero. It compares checked-in reference words when the old program
first writes address 60. `reports/isa-audit/legacy_basic_sail.json` records
the observed words, missing references, and the intentional timeout. This
does not replace the separate self-checking package tests or establish DUT
behavior.

Exceptional encodings use `tools/build_invalid_sail.py`. Each case must
install a handler, compare `mcause` and `mepc`, and publish a status word.
`ecall`, `ebreak`, `c.ebreak`, deliberately illegal 32-bit and 16-bit encodings, a
reserved CSR access, and U-mode MRET/machine-CSR violations are in this suite.
An F instruction with FS disabled checks the illegal-instruction trap. Its
negative pytest replay enables FS and requires the expected-trap oracle to
report that no trap occurred. When an executable case supersedes an old
comment-only invalid placeholder, add its path to `LEGACY_REPLACEMENTS` in
`tools/build_invalid_sail.py`, remove that source/image/reference triple, and
regenerate `reports/isa-audit/invalid_replacements.json` with the audit tool.
The other generic `invalid1`–`invalid5` triples were retired because they had
no instruction body or expected result. `reports/isa-audit/legacy_invalid_retired.json`
records all 60 historical paths. The structure script no longer creates them.
Add new exceptional tests by defining their trigger, expected `mcause`, `mepc`
check, and Sail configuration in the package-based invalid builder.
Misaligned word load/store cases check `mcause` 4/6 and `mepc` under the pinned
RVI20U32 Sail configuration, which requests alignment exceptions. The build
also replays each with `tools/config/allow-misaligned.json` and requires the
expected-trap self-check to fail, showing the result depends on that memory
policy. These cases make no claim about a DUT until its memory policy is known.
The U-mode cases configure PMP access before dropping privilege. Keep expected trap counts separate from ordinary
instruction coverage.

Trap packages use distinct `tohost` failure codes: 3 means the trigger returned
without trapping, 5 means the handler saw the wrong `mcause`, and 7 means it
saw the wrong `mepc`. The canonical host oracle reports these as
`EXPECTED_TRAP_MISSING`, `UNEXPECTED_TRAP`, and `ARCHITECTURAL_MISMATCH`.
Older trap packages without `trap_failure_codes` retain their generic
`SELF_CHECK_FAILURE` result. A timeout never counts as an expected trap.
Use `python3 -m riscv_test_runner.cli --list --suite invalid --march rv32ic_zicsr`
to list ISA-compatible trap packages offline. Serial execution
still requires verified controller stop-cause behavior.

## Advanced scenarios

Add a distinct `(id, category, march, expected_a0, assembly_body)` entry to
`tools/advanced_cases.py`. The body should express one architectural
interaction and check its final result, without assuming a pipeline depth or
number of stall cycles. `source_group()` places the generated source under the
ISA group it exercises. The historical `advanced/src/*.s` sources are separate:
82 arithmetic/control-flow cases have Sail-checked numeric references, while
the controller timer case has a self-check reference and RTL unit probe.
The 147 comment-only historical triples were retired and listed in
`tools/legacy_advanced_retired.txt`. The two builds use the same scenario body:

```sh
python3 tools/build_advanced.py
python3 tools/validate_advanced_sail.py
python3 tools/probe_vector_vstart.py
python3 tools/validate_vector_vlen.py
```

The first run checks encodings and executes the user-mode ELF under QEMU. The
second uses a bare-metal `tohost` completion, executes under Sail, and writes
the ProcessorCI sparse package to `build/advanced-sail/<id>.json`. Compare the
scenario IDs in `build/advanced/summary.json` and
`reports/advanced-sail-summary.json` by running
`python3 tools/combined_report.py`; it fails if they differ. To reproduce an
unexpected result, run the relevant build and inspect its ELF, source, JSON
package, and captured failure output. The pytest suite includes deliberate
wrong-value cases for QEMU and Sail.

The nonzero-`vstart` arithmetic probe is separate from the ordinary advanced
count because the pinned Sail max configuration explicitly traps such an
operation. `tools/probe_vector_vstart.py` verifies the strict behavior and
reruns the same source with arithmetic resume enabled, including at Zve32x
VLEN128. See `reports/vector-vstart-summary.json`. A DUT must advertise its
chosen policy before this probe is selected for it.

## Offline package selection

Use `--list` to inspect generated packages without opening a serial port:

```sh
python3 -m riscv_test_runner.cli --list --suite basic --march rv32ic --instruction c.addi
python3 -m riscv_test_runner.cli --list --suite advanced --march rv32if_zicsr --scenario fp_dynamic_rounding_flags
python3 -m riscv_test_runner.cli --list --suite advanced --march rv32ifd_zicsr --category floating
python3 -m riscv_test_runner.cli --list --suite arch --march rv32i --test-id I-addi-00
```

The filters use exact matches and still require ISA compatibility. `--suite`
selects the source; `--instruction` applies to basic tests, while
`--scenario` and `--category` apply to advanced tests. `--test-id` works with
any package source. Instruction and scenario filters are mutually exclusive.
Generic filtered serial execution remains limited to the legacy basic runner.
The selected CV32E40S ACT profile supports `--test-id` over serial.

## ACT 4.1 and a real DUT

The submodule is pinned to ACT 4.1.0 at
`6e8a45123f14cebfb3df151a0e7b849b4389b33b`. After a clone, initialize
it with `git submodule update --init
third_party_repositories/riscv-arch-test`. The sample software flow is:

```sh
python3 tools/build_act4.py --act-exe .venv-act4/bin/act
python3 tools/validate_act4_packages.py
python3 tools/check_dut_package_fit.py
PATH="$PWD/.venv-act4/bin:$PATH" python3 tools/build_act4_cv32e40s.py --extensions I,M
python3 tools/validate_act4_cv32e40s.py
python3 tools/probe_rvbench_cv32e40s.py
python3 tools/audit_act4_cv32e40s_profile.py
python3 tools/run_act4_cv32e40s_rtl.py
python3 tools/run_act4_cv32e40s_rtl.py --inject-addi-failure
python3 tools/run_act4_cv32e40s_rtl.py --package build/act4-cv32e40s/packages/M-mul-00.json --output reports/act4-cv32e40s-rtl-mul.json
python3 tools/check_act4_cv32e40s_fit.py
python3 tools/check_act4_cv32e40s_fit.py --shared-memory-bytes 524288 --output reports/act4-cv32e40s-fit-512k.json
python3 tools/probe_controller_rtl.py
python3 tools/run_act4_cv32e40s_controller_rtl.py --all
python3 tools/run_act4_cv32e40s_controller_rtl.py --all --serial-full-load --output reports/act4-cv32e40s-controller-serial-all.json
python3 -m riscv_test_runner.cli --suite arch --act-profile cv32e40s-512k --march rv32im --list
python3 tools/combined_report.py
```

Updating ACT requires deliberately changing the gitlink, the pinned revision
in `tools/build_act4.py`, the release metadata in the validation/reporting
scripts, and the setup documentation. Rebuild and run the new ELFs under its
matching Sail release before recording package counts. Keep upstream files
unmodified; adapt configurations in generated `build/` output.

The included `sail-RVI20U32` configuration describes a software target. For a
ProcessorCI core, start with its `RV-Bench/config/cores/<core>.json`, pinned
RTL, curated `RV-Bench/overlay/<core>/wrappers/<core>.sv`, and selected board's
memory definition, then confirm
its actual XLEN, extension and privilege set, CSR and exception behavior,
reset/entry address, memory map, memory interface, and completion observation.
See the [DUT infrastructure audit](act4-dut-infrastructure-audit.md). Create matching ACT
`test_config.yaml`, UDB YAML, `rvmodel_macros.h`, linker script and Sail
configuration for that core, then build only compatible ACT tests. Use shared
templates with reviewed per-variant capability overrides; the current RV-Bench
checkout has 190 core JSON configs, but they do not require 190 handwritten ACT
config sets. The selected candidate is [RV-Bench CV32E40S](act4-rvbench-core-selection.md).
Run `python3 tools/probe_rvbench_cv32e40s.py` to reproduce its directed
machine-mode, misalignment, and U-mode access-denial probe. The ACT DUT count
is I=39, M=8, C=0; the pinned ACT release has no C source directory. Zero PMP
regions deny U-mode fetches in this wrapper, and interrupt inputs are tied
low. The earlier picorv32 probe used the legacy
ProcessorCI wrapper and is not evidence for RV-Bench's picorv32 variant. The
current board RAM configuration cannot fit the ACT images. The selected
RV-Bench wrapper and controller now have a separate 512 KiB RTL map with
byte enables, serial-readable diagnostics, and write-qualified completion.
See [the integration procedure](act4-cv32e40s-512k-integration.md) for full
UART loading and PASS, FAIL, trap, and timeout replay. A timeout or breakpoint
alone cannot establish PASS.
The static fit checker currently targets picorv32 on Nexys4 DDR and records
why each unmodified ACT package cannot fit its reset address and 8 KiB memory.
Use `--core`, `--board`, `--base`, and `--reset-pc` to check another mapped
candidate after confirming its wrapper.
`riscv_test_runner.core.serial_package.run_package` uses the existing serial
interface for zero-based, fitting packages. It clears and loads the whole
controller RAM, sets the completion address and timeout, then reads `tohost`
after the controller response. Its command sequence and PASS, failure, and
timeout paths are host-mock tested. `python3 tools/probe_controller_rtl.py`
also runs the neighboring interpreter protocol testbench and probes the
controller stop logic. The probe rejects idle/read address matches and accepts
acknowledged status writes on primary and data buses. The controller does not
expose a decoded trap cause and has not been validated on a device, so this
adapter is not an FPGA validation claim.
`build/dut-smoke/picorv32-addi.json` is a small address-zero RV32I package for
future serial bring-up. It is built with `tools/linker/dut-smoke-8k.ld` and
independently run under Sail. Keep its result separate from ACT certification.

## Final software check

```sh
python3 tools/build_basic_sail.py
python3 tools/build_dut_smoke.py
python3 tools/build_invalid_sail.py
python3 tools/build_advanced.py
python3 tools/validate_advanced_sail.py
python3 tools/validate_act4_packages.py
python3 tools/validate_legacy_basic_sail.py
python3 tools/validate_legacy_advanced_sail.py
python3 tools/validate_legacy_advanced_timer.py
python3 tools/isa_audit.py --compile
python3 tools/combined_report.py
pytest -q validation_tests/test_phase1.py
```

When `../processor_ci_controller` and Icarus/Verilator are available, run
`python3 tools/probe_controller_rtl.py` as a separate RTL protocol check.

`reports/combined-summary.json`, `reports/combined-summary.md`, and
`reports/combined-software.junit.xml` report software evidence. FPGA results
remain pending until a matching core and its execution adapter are tested.
