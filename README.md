# Processor CI Tests

[![Pylint](https://github.com/LSC-Unicamp/processor-ci-tests/actions/workflows/pylint.yml/badge.svg)](https://github.com/LSC-Unicamp/processor-ci-tests/actions/workflows/pylint.yml)

Standalone home for the Processor CI RISC-V verification assets: ISA tests, reference memories, benchmark build support, and the serial test runner used to validate a processor core.

## What this repo contains

- `riscv_test_runner/`: Python package for the test runner
- `riscv_test_runner/core/`: runner, `-march` parsing, and small data helpers
- `main.py`: stable compatibility wrapper around the package CLI
- `tests/`: RISC-V ISA test corpus grouped by architecture extension and level
- `benchmarks/`: bare-metal benchmark sources, ports, linker scripts, and build helpers
- `third_party_repositories/`: imported or converted upstream test material
- `config.json`: example test directory configuration consumed by the runner
- `docs/`: repository layout and maintenance notes
- `requirements.txt`: Python dependencies for the runner and CI checks

## Quick start

1. Create a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure the Processor CI communication package is available next to this repository or on `PYTHONPATH`.

4. Run the test runner:

```bash
python -m riscv_test_runner.cli \
  --port /dev/ttyUSB0 \
  --config config.json \
  --march rv32im_zicsr \
  --key 0x4e455859
```

Or use the compatibility wrapper:

```bash
python main.py \
  --port /dev/ttyUSB0 \
  --config config.json \
  --march rv32im_zicsr \
  --key 0x4e455859
```

Both entrypoints use the same parser and behavior.

## Common usage

- Show CLI help:

```bash
python -m riscv_test_runner.cli --help
```

- Run only the tests selected by an architecture string:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im
```

- Run with a longer serial timeout and core execution timeout:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im_zicsr \
  -s 10 \
  -t 5000
```

- Run against a core with separate instruction and data memories:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im \
  --core-use-two-memories
```

- Request extra benchmark-style tests listed in `config.json`:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im \
  -e coremark
```

## Test Layout

The ISA tests live under `tests/<architecture>/<level>/`.

```text
tests/RV32I/basic/src/        assembly source files
tests/RV32I/basic/memory/     compiled instruction memory hex files
tests/RV32I/basic/reference/  expected result hex files
```

Architectures are named like `RV32I`, `RV32M`, `RV64I`, or `RV32Zicsr`. Test levels are:

- `basic`: currently executed by the Python runner
- `advanced`: broader instruction and behavior coverage
- `invalid`: invalid instruction or exception-oriented cases

`config.json` maps each architecture directory to its path and breakpoint addresses. The current sample uses `/eda/processor_ci_tests/...` paths for CI/container use; adjust those paths for local runs if needed.

## Benchmarks

`benchmarks/` keeps benchmark source and porting support separate from the precompiled ISA test corpus.

- `benchmarks/coremark/`: CoreMark source tree
- `benchmarks/port/`: bare-metal boot and platform hooks
- `benchmarks/common/`: minimal C library support
- `benchmarks/target/`: target-specific library and Makefile
- `benchmarks/compile_coremark.sh`: builds CoreMark hex output with `riscv32-unknown-elf-*`
- `benchmarks/compile_common.sh`: builds the minimal common library

Generated benchmark build outputs are written under `benchmarks/build/`.

## CLI Reference

```text
usage: python -m riscv_test_runner.cli [-h] [-b BAUDRATE] -p PORT
                                        [-s SERIAL_TIMEOUT] -c CONFIG
                                        [-m MARCH] [-e EXTRA_TESTS] [-k KEY]
                                        [-t TIMEOUT] [-ctm]
```

- `-p`, `--port`: serial port used to communicate with the FPGA board. Required.
- `-c`, `--config`: JSON test configuration. Required.
- `-b`, `--baudrate`: serial baudrate. Defaults to `115200`.
- `-s`, `--serial-timeout`: serial timeout in seconds. Defaults to `5`.
- `-m`, `--march`: RISC-V architecture string used to select test directories. Defaults to `rv32i`.
- `-e`, `--extra-tests`: comma-separated extra tests from `config.json`.
- `-k`, `--key`: hex sync key expected from the board.
- `-t`, `--timeout`: core execution timeout in clock cycles. Defaults to `1000`.
- `-ctm`, `--core-use-two-memories`: use separate instruction and data memories.

## Developer Notes

- `riscv_test_runner.cli.build_parser()` exposes the CLI parser for tests.
- `riscv_test_runner.cli.main(argv=None)` supports argument injection for wrappers and tests.
- `riscv_test_runner.core.runner.ProcessorCITest` is the hardware-facing runner.
- Root-level `core.*` imports remain as compatibility shims for older scripts.
- Test execution writes a JUnit report named `test_results_<timestamp>.xml`.

## Notes

- The current organization keeps large verification data in place while moving Python implementation into a package, matching the shape used by `processor_ci_discover`.
- The runner currently executes the `basic` category. `advanced` and `invalid` data are preserved for expansion and maintenance.
