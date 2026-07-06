# Repository Layout

This repo is organized around two kinds of assets:

- source code that runs tests against a core
- data files used by those tests and benchmarks

## Python Runner

```text
riscv_test_runner/
  cli.py
  core/
    runner.py
    march.py
    utils.py
main.py
core/
```

`riscv_test_runner/` is the canonical package. `main.py` and root-level `core/` are compatibility wrappers for older scripts.

## ISA Test Corpus

```text
tests/<architecture>/<level>/src/
tests/<architecture>/<level>/memory/
tests/<architecture>/<level>/reference/
```

- `src/`: assembly source for the test
- `memory/`: compiled hex loaded into the processor memory
- `reference/`: expected values read back by the runner

The architecture folder names are used by the `--march` selector and entries in `config.json`.

## Benchmarks

```text
benchmarks/coremark/
benchmarks/common/
benchmarks/port/
benchmarks/target/
```

The benchmark area keeps source, platform hooks, linker scripts, and build helpers together. Generated files should stay under benchmark build directories rather than being mixed into the ISA test corpus.

## Third-Party Material

`third_party_repositories/` stores imported sources and converted assembly used to derive tests. Keep local edits documented when refreshing these files from upstream material.
