# Test directory audit

Counts distinguish legacy `src/memory/reference` assets from executable package suites.
A blank legacy triple in a Z-extension group is intentional; its basic package is the executable test.

| Group | Configured legacy | Basic packages | Advanced packages | Invalid packages | Legacy basic bodies/sources | Legacy advanced bodies/sources | Advanced without numeric oracle |
|---|---|---:|---:|---:|---:|---:|---:|
| RV32A | yes | 11 | 1 | 1 | 11/11 | 0/0 | 0 |
| RV32C | yes | 34 | 2 | 1 | 20/20 | 0/0 | 0 |
| RV32D | yes | 26 | 1 | 1 | 0/20 | 0/0 | 0 |
| RV32F | yes | 26 | 3 | 1 | 0/20 | 0/0 | 0 |
| RV32I | yes | 38 | 27 | 9 | 40/43 | 3/3 | 0 |
| RV32M | yes | 8 | 5 | 0 | 8/8 | 80/80 | 0 |
| RV32Zba | no | 3 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zbb | no | 18 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zbc | no | 3 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zbkb | no | 5 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zbs | no | 8 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zicsr | yes | 6 | 1 | 1 | 0/6 | 0/0 | 0 |
| RV32Zve32f | no | 66 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zve32x | no | 259 | 13 | 1 | 0/0 | 0/0 | 0 |
| RV32Zve64d | no | 29 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zve64f | no | 6 | 0 | 0 | 0/0 | 0/0 | 0 |
| RV32Zve64x | no | 11 | 1 | 0 | 0/0 | 0/0 | 0 |
| RV64A | yes | 11 | 1 | 1 | 0/11 | 0/0 | 0 |
| RV64D | yes | 6 | 1 | 1 | 0/6 | 0/0 | 0 |
| RV64F | yes | 4 | 1 | 1 | 0/4 | 0/0 | 0 |
| RV64I | yes | 12 | 1 | 1 | 0/12 | 0/0 | 0 |
| RV64M | yes | 5 | 1 | 0 | 0/5 | 0/0 | 0 |
| RV64Zve64x | no | 4 | 0 | 0 | 0/0 | 0/0 | 0 |

Validated package totals: basic 599, advanced 59, invalid 19.
Retired comment-only legacy advanced triples: 147 (paths in `tools/legacy_advanced_retired.txt`).

## Findings

No ISA directory findings.

## Interpretation

- Z-extension groups use package_src and need no legacy hex/reference triples.
- ACT 4.1 tests are built under build/act4, outside tests/.
- Each configured ISA group has at least one package-based advanced scenario.
- The 82 executable legacy arithmetic/control-flow cases have a separate Sail replay; the timer case has a separate RTL unit probe.

Configured `/eda/processor_ci_tests/...` paths are environment-specific; the package CLI resolves ISA groups from this checkout before listing them.

Configured extra tests are outside this audit's current scope.
