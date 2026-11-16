# ACT 4.1 CV32E40S: 512 KiB controller integration

The selected core is RV-Bench's pinned CV32E40S and its curated
`overlay/cv32e40s/wrappers/cv32e40s.sv`. The wrapper now instantiates the
controller in `RV-Bench/tools/controller` with one 512 KiB memory shared by its instruction and
data ports. The controller preserves byte enables and rejects out-of-range
accesses instead of wrapping them into low RAM. Its normal stop condition
requires an acknowledged status write.
Compile the controller with `ENABLE_SECOND_MEMORY` and `ENABLE_BYTE_SELECT`;
the wrapper defines both, and the RTL replay passes them to Verilator
explicitly so file order cannot change the interface.

| Address | Purpose |
|---|---|
| `0x00000`–`0x7efff` | 508 KiB ACT program and data RAM; linker and Sail use this limit. |
| `0x7f000` | Diagnostic byte count; writing zero clears the count. |
| `0x7f004` | Diagnostic ring capacity, 1024 bytes. |
| `0x7f100`–`0x7f4ff` | Four diagnostic characters per serial-readable word. |
| `0x7f500`–`0x7ffff` | Reserved diagnostic window. |
| `0x10000000` | ACT virtual-printer write port; bytes enter the diagnostic ring. |

The 4 KiB diagnostic window is outside the ACT linker and Sail RAM region.
Controller serial accesses to that window read diagnostic registers; core
accesses do not alias program RAM. The wrapper uses a 24-bit execution pulse
counter, covering ACT's 100,000-cycle timeout.

Rebuild and validate from `processor_ci_tests`:

```sh
PATH="$PWD/.venv-act4/bin:$PATH" python3 tools/build_act4_cv32e40s.py --extensions I,M
python3 tools/validate_act4_cv32e40s.py
python3 tools/check_act4_cv32e40s_fit.py --shared-memory-bytes 524288 --output reports/act4-cv32e40s-fit-512k.json
python3 tools/probe_controller_rtl.py
python3 tools/run_act4_cv32e40s_controller_rtl.py --all
python3 tools/run_act4_cv32e40s_controller_rtl.py --all --serial-full-load --output reports/act4-cv32e40s-controller-serial-all.json
python3 tools/run_act4_cv32e40s_serial.py --all --dry-run
```

`--all` executes each ACT ELF through the core and controller using a direct
simulation preload. `--serial-full-load` sends every ELF segment over the
real UART before execution and reads `tohost` through UART afterward. The
testbench starts unused RAM bytes at zero; the host adapter clears the whole
program RAM for deterministic execution across repeated device runs.
Both [controller RTL replay](../reports/act4-cv32e40s-controller-rtl.json)
and [full UART replay](../reports/act4-cv32e40s-controller-serial-all.json)
passed all 47 I/M packages. The [combined report](../reports/combined-summary.md)
tracks these as separate DUT simulation evidence.

Negative paths use the same controller and UART:

```sh
python3 tools/run_act4_cv32e40s_controller_rtl.py --serial-full-load --inject-addi-failure --output reports/act4-cv32e40s-controller-serial-full-load-induced-fail.json
python3 tools/run_act4_cv32e40s_controller_rtl.py --serial-full-load --inject-illegal --output reports/act4-cv32e40s-controller-serial-full-load-illegal.json
python3 tools/run_act4_cv32e40s_controller_rtl.py --expect-timeout
```

The injected ADDI mismatch writes `tohost=3` and emits failure text. An
injected illegal instruction also writes `tohost=3`; its serial-readable ACT
diagnostics identify `XCAUSE=2` and `XEPC=0x88`. An unreachable completion
address returns the controller timeout flag even when `tohost` later contains
the ACT pass value. The host adapter decodes the diagnostic ring and keeps
timeout, self-check failure, and unexpected trap distinct.
The [negative reports](../reports/act4-cv32e40s-controller-serial-full-load-illegal.json)
retain the complete ACT trap message and its decoded cause and EPC.

For a future device with this memory map, the host entry point is
`tools/run_act4_cv32e40s_serial.py --port <port> --all`. It uses the same
package oracle, clears and loads the 508 KiB program RAM, checks the controller
ID when `--expected-id` is provided, reads `tohost` and diagnostics, and writes
JSON and JUnit results. `--dry-run` checks package fit without a device; it
currently selects all 47 packages.

These are RTL simulation results. The older Nexys4 DDR board profile specified
8 KiB primary and 4 KiB data RAM, so none of the 47 ACT packages fit that
legacy profile. The CV32E40S wrapper now requests 512 KiB, but that memory
implementation has not been synthesized or executed on an FPGA. The upstream UDB's detailed
CSR, privilege, alignment, and Zc claims remain provisional for the pinned
core; the 47 generated ACT tests cover I and M, while ACT 4.1 provides no C
sources in this selection.
