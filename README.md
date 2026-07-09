# ProcessorCI Tests

[![Pylint](https://github.com/LSC-Unicamp/processor-ci-tests/actions/workflows/pylint.yml/badge.svg)](https://github.com/LSC-Unicamp/processor-ci-tests/actions/workflows/pylint.yml)

ProcessorCI Tests contains the RISC-V software test assets and the serial test
runner used to validate a processor through ProcessorCI hardware. It includes ISA
test corpora, benchmark build support, third-party test material, and the Python
runner that communicates with a board.

## Repository Layout

```text
riscv_test_runner/       Canonical Python package for the runner
riscv_test_runner/core/  Runner implementation, -march parsing, and helpers
main.py                  Compatibility wrapper around the package CLI
core/                    Legacy import compatibility shims
tests/                   ISA test corpus grouped by architecture and level
benchmarks/              Bare-metal benchmark sources and build helpers
third_party_repositories/ Imported or converted upstream test material
docs/                    Layout and maintenance notes
config.json              Example test configuration
requirements.txt         Python dependencies for runner and CI checks
```

## Installation

```bash
git clone https://github.com/LSC-Unicamp/processor-ci-tests.git
cd processor-ci-tests
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
```

The runner expects the ProcessorCI communication package to be available next to
this repository or on `PYTHONPATH`.

## Quick Start

Run the package CLI:

```bash
python -m riscv_test_runner.cli \
  --port /dev/ttyUSB0 \
  --config config.json \
  --march rv32im_zicsr \
  --key 0x4e455859
```

Use the compatibility wrapper:

```bash
python main.py \
  --port /dev/ttyUSB0 \
  --config config.json \
  --march rv32im_zicsr \
  --key 0x4e455859
```

Both entrypoints use the same parser and behavior.

## Common Usage

Show CLI help:

```bash
python -m riscv_test_runner.cli --help
```

Run only tests selected by an architecture string:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im
```

Run with custom serial and core timeouts:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im_zicsr \
  -s 10 \
  -t 5000
```

Run against a core with separate instruction and data memories:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im \
  --core-use-two-memories
```

Request extra benchmark-style tests listed in `config.json`:

```bash
python -m riscv_test_runner.cli \
  -p /dev/ttyUSB0 \
  -c config.json \
  -m rv32im \
  -e coremark
```

## Test Corpus

ISA tests live under:

```text
tests/<architecture>/<level>/src/
tests/<architecture>/<level>/memory/
tests/<architecture>/<level>/reference/
```

- `src/`: assembly source.
- `memory/`: compiled instruction memory hex files.
- `reference/`: expected values read by the runner.

Architectures are named like `RV32I`, `RV32M`, `RV64I`, and `RV32Zicsr`.
Current levels are `basic`, `advanced`, and `invalid`; the runner currently
executes the `basic` level.

`config.json` maps architecture directories to paths and breakpoint addresses.
The sample file may use CI/container paths; adjust paths for local runs.

## Benchmarks

`benchmarks/` stores benchmark source and porting support separately from the ISA
corpus:

- `benchmarks/coremark/`: CoreMark source tree.
- `benchmarks/port/`: bare-metal boot and platform hooks.
- `benchmarks/common/`: minimal C library support.
- `benchmarks/target/`: target-specific library and Makefile.
- `benchmarks/compile_coremark.sh`: CoreMark build helper.
- `benchmarks/compile_common.sh`: common library build helper.

Generated benchmark build output should stay under benchmark build directories.

## Outputs

The runner communicates with the board, executes the selected tests, and writes a
JUnit report named `test_results_<timestamp>.xml`.

## Development

`riscv_test_runner/` is the canonical implementation. Keep `main.py` and the
root-level `core/` package as compatibility shims for older scripts.

Useful checks:

```bash
pytest
python -m riscv_test_runner.cli --help
python main.py --help
```

See [docs/README.md](docs/README.md) for layout notes.

## Contributing

Issues and pull requests are welcome. When adding tests, include source,
compiled memory, expected reference output, and any config changes needed to run
the new cases.

## License

This project is licensed under the [MIT License](LICENSE).
