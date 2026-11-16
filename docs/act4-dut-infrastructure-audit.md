# ACT 4.1 inputs already present in ProcessorCI

The user does not need to supply a new custom configuration file to start a
ProcessorCI ACT adapter. RV-Bench's pinned sources and curated wrappers, plus
the neighboring controller repository, provide the current implementation
inputs. The older `processor_ci/rtl` wrappers supplied the initial audit but
are not the selected ACT core wrappers. See the
[RV-Bench core selection](act4-rvbench-core-selection.md) for CV32E40S evidence.

| Input | Existing source | What it supplies |
|---|---|---|
| Core choice and coarse ISA | `processor_ci/config/<core>.json` and `RV-Bench/config/cores/<core>.json` | `march`, source files, wrapper name and `two_memory` |
| Core wiring and some reset values | `RV-Bench/overlay/<core>/wrappers/<core>.sv` (`processorci_top`) | Primary and optional data bus; some wrappers show a boot address |
| Pinned core implementation | `RV-Bench/cores/<core>/` and `RV-Bench/config/cores_lock.csv` | Actual RTL and source revision for a selected core |
| Board memory size | `processor_ci/core/board_defines.py` | 4, 8, or 16 KiB controller memory, depending on board |
| Simulation memory | `processor_ci/internal/verification_top.sv` | Two possible 4096-byte memories |
| Controller memory and protocol | `processor_ci_controller/rtl/{controller,memory,interpreter}.sv` and `processor_ci_communication/core/serial.py` | Word writes/reads, end-address execution, an 8-byte completion response with a completion/timeout bit |

`processorci_top` is a shared *interface*, with one wrapper per core. It does
not force the same ISA, boot PC, privilege behavior, or memory wiring on every
implementation. The initial audit of the legacy ProcessorCI wrappers found,
for example, that Grande-Risco-5 advertises `rv32imc` while tying off its data
bus. The `fedar-f1-rv64im` config records `rv32i` despite its RV64IM name; `march`
therefore needs checking against the selected wrapper and core source before
being used as an ACT capability claim. The configs do not record privilege
modes, CSR behavior, exceptions, ISA versions, or a full memory map.

The current ACT software example cannot be loaded unchanged into the FPGA
controller memory. `I-addi-00` has entry `0x80000000`, `tohost` at
`0x8001fd80`, and LOAD segments spanning `0x80000000` to `0x800403a0`.
The largest configured board memory is 16 KiB. The controller's `Memory`
indexes low address bits, so large addresses alias rather than create a
256 KiB region. Relinking to address zero alone would not solve its size and
layout requirements. Across the 39 current RV32 I sample packages, the
smallest total LOAD file payload is 77,776 bytes (`I-nop-00`), exceeding even
the largest 16 KiB configured board memory. A smaller ACT test/runtime or
larger accessible memory, plus a matching linker map, is needed.

The `I-nop-00` ELF's allocated file sections explain this lower bound:
`.text.init` 64 bytes, `.text.rvtest` 8,768 bytes, `.data` 68,000 bytes,
`.tohost` 16 bytes, and `.text.rvmodel` 928 bytes. They sum to 77,776 bytes
before any address gaps or reserved stack. The test code alone exceeds 8 KiB;
the initialized data alone exceeds 16 KiB. Linker alignment or stack changes
cannot make this generated test fit any currently configured controller RAM.

The controller can stop on a configured bus address and its eight-byte
response distinguishes early completion from timeout. It does not report a
decoded trap cause, and address matching alone does not inspect the ACT
`tohost` value. The host runner must read and classify the status word after
the stop and reject timeouts. A trap needs an observable handler result or a
decoded core/harness signal; otherwise the result remains inconclusive rather
than ACT PASS.

The reproducible `tools/probe_controller_rtl.py` run compiled the neighboring
`Interpreter` with Icarus and the `Controller` with Verilator. The interpreter
testbench passed burst writes/reads, breakpoint commands, early completion,
and timeout replies. The controller normal-mode stop logic was corrected to
require an acknowledged write to the configured address; single and split
memory RTL probes now reject idle/read matches and accept the write. Paginated
legacy mode retains its existing address-match behavior. The
[RTL probe report](../reports/controller-rtl-protocol.json) records source
hashes and results. The serial adapter reads back the nonzero status and
rejects a reply whose reported cycle count reaches its timeout. A decoded
trap/stop reason and FPGA execution evidence remain open.

## Reuse path

The RV-Bench checkout currently has 190 core configuration JSON files. ACT
does not need 190 separately maintained sets of five configuration files. A
generator can render one shared `test_config.yaml`, linker, `rvmodel_macros.h`,
UDB and Sail template from a reviewed profile for each *selected core variant*.
The profile can import the coarse ISA and source identity from RV-Bench, the
bus and reset wiring from its curated `processorci_top`, and the RAM size from
the board.
It must also record an explicit, evidence-backed ISA/privilege/CSR/trap claim.
The wrapper's common port shape cannot supply those architectural claims.
Variants with the same verified RTL, wrapper parameters, board map and ACT
runtime can reuse one generated profile; variants with different parameters
need a distinct profile or override. The generator should reject incomplete
claims and an ACT ELF that exceeds the selected board memory before executing
it. The generated files are build artifacts, not handwritten files in every
RV-Bench config directory.

1. Select an `RV-Bench/config/cores/<core>.json` and a supported board. Read
   the curated RV-Bench `processorci_top` wrapper to confirm ISA, reset PC,
   bus behavior and whether software can write the completion word.
2. Read the board memory size from `board_defines.py`; derive an ACT linker
   map and memory limit from the actual accessible memory. Reject tests that
   cannot fit.
3. Generate ACT `test_config.yaml`, linker script, macros and Sail memory
   configuration from those inputs. Fill UDB extension versions, privilege,
   CSR and trap parameters only after checking the selected core.
4. Exercise status loading, completion and timeout against the existing
   controller RTL testbench and host mock, then use hardware when available.

The current Sail RVI20U32 sample remains a software integration target. Its
UDB advertises many optional extensions and machine-level parameters that
cannot be inferred from the shared top-level interface.

## Earlier legacy-wrapper candidate: picorv32 on Nexys4 DDR

This section records the first audit and probe of the *legacy ProcessorCI*
wrapper. It does not describe the RV-Bench picorv32 wrapper, which instantiates
the core with default M/C parameters disabled. The selected RV-Bench ACT
candidate is CV32E40S, documented above.

`processor_ci/config/picorv32.json` and the RV-Bench config advertise `rv32i`
and a single memory.
Its `processorci_top` wrapper resets the CPU to address zero and connects
`mem_valid`, `mem_addr`, `mem_wdata`, `mem_wstrb`, `mem_rdata`, and `mem_ready`
to the controller's primary bus. This gives a concrete path for software to
write a completion word. The wrapper sets `COMPRESSED_ISA=1`, `ENABLE_MUL=1`,
and `ENABLE_DIV=1`, which conflicts with the config's narrower `rv32i` label;
those parameters are evidence of the wrapper configuration. RV-Bench now has
`picorv32.v` at pinned source revision
`87c89acc18994c8cf9a2311e871818e87d304568`. The reproducible
[`tools/probe_picorv32_rtl.py`](../tools/probe_picorv32_rtl.py) simulation
compiled this RTL with the ProcessorCI wrapper and an 8 KiB address-zero bus.
Its [report](../reports/picorv32-rtl-probe.json) records successful status
writes after directed I, multiply/divide, and compressed-add programs. Reads
of `mstatus`, writes to `mtvec`, and `ecall` instead asserted the core's halt
`trap` signal. This is evidence for those sampled instructions and for the
absence of a usable standard machine trap path in this wrapper; it does not
prove every RV32IMC instruction. The ProcessorCI Jenkins generator still
clones the configured repository with `--depth=1` and no commit pin, so an
FPGA build must be tied to the same source revision before these RTL results
can be attributed to that build.

Nexys4 DDR provides 8192 bytes of controller memory. Its board ID matches
the runner's default sync keyword. The ACT sample's load span of more than
256 KiB and entry at `0x80000000` are incompatible with this zero-based,
8 KiB candidate. The controller also observes the configured end address on
the bus without checking that a valid write occurred; the
adapter must verify a status write and read the value before claiming PASS.
The `picorv32` candidate is suitable for a compact serial bring-up package.
It is not currently a truthful standard M-mode ACT target: ACT's machine
trap/CSR tests cannot be represented by the halt-only trap signal. A different
core with standard machine CSRs, or a compatible ACT configuration/runtime
that excludes those requirements, is needed for full ACT execution. There is
no ACT UDB or FPGA execution result for picorv32.

Run `python3 tools/check_dut_package_fit.py` after building the ACT RV32
sample. The host check uses the picorv32 config's advertised ISA, the board's
memory size, the wrapper's reset PC, and each package's LOAD segments and
`tohost` location. It also reports each package's LOAD byte lower bound.
All 39 current sample packages fail this static fit check;
the per-package reasons are in `reports/act4-picorv32-nexys4-fit.json`. A
passing static fit check would only establish address/size compatibility.

For serial bring-up, `python3 tools/build_dut_smoke.py` builds one separate
RV32I `addi` package at address zero using an explicit 8 KiB linker map. Its
LOAD data totals 176 bytes and its `tohost` is at `0xa0`. The executable
passes Sail 0.13.1 with matching address-zero RAM and the static board-fit
check. The [smoke report](../reports/dut-smoke-summary.json) keeps this directed
case separate from ACT 4.1 results. The RTL probe above establishes only its
separate directed I/M/C scenarios; the FPGA smoke package has not executed.
