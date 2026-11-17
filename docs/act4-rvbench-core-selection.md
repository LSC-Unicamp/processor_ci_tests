# First ACT 4.1 core: RV-Bench CV32E40S

The candidate implementation is RV-Bench's pinned `cv32e40s` source at
`9d9cae78b01a11458953133d1173c61933a2ba86` with its curated
`overlay/cv32e40s/wrappers/cv32e40s.sv`. The legacy `processor_ci/rtl` wrappers
are not the input for this choice. The current RV-Bench checkout has 190 core
configuration JSON files; the shortlist below favors standard machine-mode
traps, a usable memory bus, and an ACT 4.1 sample profile.

| Core | Evidence | Selection consequence |
| --- | --- | --- |
| CV32E40S | Pinned RTL defaults to RV32I and M, enables Zc internally, implements `mstatus`, `mtvec`, `mcause`, and `mepc`; curated split-memory wrapper passed RV-Bench execution smoke; ACT 4.1 provides `cv32e40s-rv32imc` UDB/macros/Sail examples. | **Select first.** Its wrapper has request-qualified instruction and data buses. |
| CV32E40P | Curated wrapper passed execution smoke; ACT 4.1 has v1/v2 RV32IMC profiles and the core has machine trap CSRs. | Strong fallback, but the ACT profile revision must be matched to RV-Bench's pinned source. |
| CVE2 | Curated wrapper passed execution smoke; ACT 4.1 has a CV32E20 profile and RTL implements machine CSRs. | Useful fallback; the wrapper ties both `cyc` outputs high, so completion/address observation needs extra care. |
| Ibex | Curated wrapper passed execution smoke; RTL defaults include M and compressed subsets and machine CSRs. | Viable, but there is no matching core-specific ACT 4.1 sample profile in this checkout. |
| picorv32 | RV-Bench wrapper passes a simple signature smoke; it instantiates the core without parameter overrides. Its default M, C, and IRQ parameters are off, and its `trap` is a halt signal. | Exclude from the first standard machine-mode ACT target. The earlier I/M/C probe used the **legacy ProcessorCI wrapper**, which enables M and C; it does not describe this RV-Bench wrapper. |

## Directed CV32E40S evidence

`python3 tools/probe_rvbench_cv32e40s.py` compiles a small program with
RV-Bench's own Verilator wrapper simulator and a private instruction image. It
reads `mstatus`, checks that a reserved `mtvec` mode write retains the prior
mode, handles an M-mode `ecall` with `mcause`/`mepc`/`mret`, checks `mul`,
`div`, `c.addi`, and a misaligned word store/load. It also enters U mode and
checks that the first U-mode fetch faults with cause 1 because zero PMP
regions deny unmatched U-mode access. The probe passed; the recorded
source revision, wrapper hash, and result are in
[`reports/act4-cv32e40s-rvbench-probe.json`](../reports/act4-cv32e40s-rvbench-probe.json).
This proves the sampled path through the pinned RTL and curated wrapper. It
does not establish complete CSR or Zc coverage, an ACT result, or FPGA execution.

## Remaining profile and execution work

`tools/build_act4_cv32e40s.py` stages the upstream ACT 4.1 CV32E40S UDB and
Sail configuration, changes the linker entry from `0x80` to the wrapper's
reset address zero, and uses ProcessorCI-compatible `tohost=1/3` halt macros.
The 39 generated I and eight M ELFs all pass direct Sail execution and host oracle checks
(`tools/validate_act4_cv32e40s.py`). The staged linker and Sail program region
now match 508 KiB. ACT requires a reference-only CLINT and interrupt generator
in Sail, although the controller has no corresponding hardware. The UDB
example still contains untested CSR, Zc, interrupt, and Zkt claims.

The selected RV-Bench wrapper instantiates `cv32e40s_core` with its default
parameters and drives `boot_addr_i=0`. The pinned core defaults are `RV32I`,
`M_EXT=M`, `B_EXT=B_NONE`, zero PMP and PMA regions, and `ZC_EXT=1` internally.
Those settings support the staged I/M scope. The U-mode fetch-denial and
misaligned-access probe checks two previously unresolved behaviors. The
UDB's full CSR and Zc claims still need further RTL tests. The first
`mstatus` read in the probe was zero despite an RTL reset constant of
`0x1800`; that discrepancy remains under investigation. The
[profile audit](../reports/act4-cv32e40s-profile-audit.json) checks the pinned
wrapper defaults, program map, and reference-only Sail services.

One real ACT `I-addi-00` ELF now passes through the curated wrapper in RTL:
[`reports/act4-cv32e40s-rtl-addi.json`](../reports/act4-cv32e40s-rtl-addi.json)
records `tohost=1`. Mutating the first checked `addi` after reference
generation yields `tohost=3` and the host oracle's SELF_CHECK_FAILURE in
[`reports/act4-cv32e40s-rtl-addi-induced-fail.json`](../reports/act4-cv32e40s-rtl-addi-induced-fail.json).
The real `M-mul-00` ACT ELF also writes `tohost=1` in RTL, recorded in
[`reports/act4-cv32e40s-rtl-mul.json`](../reports/act4-cv32e40s-rtl-mul.json).
The wrapper needed two corrections: a data response for stores and an
acknowledgement for `fence.i` without an external cache. RV-Bench's wrapper
smoke still passes after those corrections. The RTL run uses 512 KiB private
simulation memories; it is not a controller or FPGA result.

The legacy ProcessorCI board memory is at most 16 KiB primary RAM, with a
4 KiB split data RAM. The smallest staged CV32E40S ACT ELF has 82,480
initialized bytes and a load span beyond 200 KiB. The
[`reports/act4-cv32e40s-fit.json`](../reports/act4-cv32e40s-fit.json)
rejects all 47 packages on Nexys4 DDR. More mapped memory or a materially
smaller ACT runtime is required before FPGA execution on that configuration.

The [512 KiB controller integration](act4-cv32e40s-512k-integration.md)
connects the wrapper's separate instruction and data buses to one shared
memory, preserves byte enables, and reserves a serial-readable diagnostic
window. All 47 I/M packages fit that RTL map. The full core and controller
run passes all 47 with simulation preload; the UART path also uploads ACT
segments, reads status, and distinguishes PASS, self-check failure, illegal
trap diagnostics, and timeout. Physical memory implementation and FPGA
execution remain open.
