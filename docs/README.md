# ProcessorCI Tests Documentation

## Source And Data Boundaries

This repository mixes executable Python code with large verification assets.
Keep those responsibilities separate:

- `riscv_test_runner/` owns runner behavior.
- `main.py` and root `core/` modules are compatibility shims.
- `tests/` owns ISA test data.
- `benchmarks/` owns benchmark sources and build helpers.
- `third_party_repositories/` stores imported or converted upstream material.

## Runner Package

```text
riscv_test_runner/
  cli.py
  core/
    runner.py
    march.py
    utils.py
```

The package CLI is the canonical entrypoint:

```bash
python -m riscv_test_runner.cli
```

Keep parser changes in `riscv_test_runner.cli` so tests and wrappers can share
the same behavior.

## ISA Test Layout

```text
tests/<architecture>/<level>/src/
tests/<architecture>/<level>/memory/
tests/<architecture>/<level>/reference/
```

If a test is refreshed from upstream material, preserve enough information to
trace where it came from and how it was converted.

## Generated Files

Generated reports and build outputs should not be mixed into source trees.
Common generated files include:

- `test_results_<timestamp>.xml`
- benchmark build directories
- Python `__pycache__/`
- temporary serial-run logs

## Validation Checklist

```bash
pytest
python -m riscv_test_runner.cli --help
python main.py --help
```

Hardware execution requires a connected ProcessorCI-compatible board and the
communication package.
