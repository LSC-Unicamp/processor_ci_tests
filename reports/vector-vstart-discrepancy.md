# Nonzero `vstart` depends on the Sail vector configuration

The earlier `vadd.vv` probe initialized four e32 lanes, set `vstart=2`, and
expected lanes 0–1 to retain 9 while lanes 2–3 became 5. QEMU completed the
self-check. The pinned ACT `sail-rv32-max/sail.json` sets
`extensions.V.vstart.zero_required.arith=true`; Sail traps at `vadd.vv` under
that setting. The model's config comments say this trap is permitted for
vector arithmetic with nonzero `vstart`.

`python3 tools/probe_vector_vstart.py` now rebuilds the probe and records:

- QEMU user-mode resume: PASS.
- Pinned strict Sail configuration: trap-loop diagnostic at the arithmetic
  instruction. This diagnostic is not counted as a passing exception test.
- Sail with `tools/config/vector-vstart-arith-resume.json`: PASS.
- Sail Zve32x/ELEN32/VLEN128 with the same arithmetic-resume policy: PASS.

The machine-readable result is `reports/vector-vstart-summary.json`. The
ordinary advanced suite separately checks `vector_vstart_load_resume`, which
passes QEMU and the pinned strict Sail configuration: a vector load starts at
lane 2, leaves lanes 0–1 unchanged, updates lanes 2–3, and resets `vstart`.

Arithmetic resume remains a conditional capability. A selected DUT must
document its policy before this probe can be treated as applicable to it.
