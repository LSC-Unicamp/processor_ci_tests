# Install Sail for pinned ACT 4.1.0

ACT 4.1.0 in this repository requires `sail_riscv_sim` **0.13.1**. The
instructions below install the official Linux x86_64 release without sudo.
They match this Arch Linux workspace.

```bash
mkdir -p "$HOME/.local/processorci-sail-0.13.1"
curl -fL https://github.com/riscv/sail-riscv/releases/download/0.13.1/sail-riscv-Linux-x86_64.tar.gz -o /tmp/processorci-sail-0.13.1.tar.gz
tar -xzf /tmp/processorci-sail-0.13.1.tar.gz -C "$HOME/.local/processorci-sail-0.13.1" --strip-components=1
export PATH="$HOME/.local/processorci-sail-0.13.1/bin:$PATH"
sail_riscv_sim --version
```

The expected version output is `0.13.1`. Add the `export PATH=...` line to
`~/.bashrc` if you want it in new shells. This Sail version is **already
installed and verified** at that path in the current workspace. The
`tools/build_act4.py` command detects it there without a PATH change.

Sail alone is insufficient to build ACT tests. On Arch Linux, install the
remaining packaged tools:

```bash
sudo pacman -S --needed ruby ruby-bundler ruby-erb riscv64-elf-gcc
cd /home/gabcro/Code/Processor_CI/processor_ci_tests
python3 -m venv .venv-act4
.venv-act4/bin/python -m pip install -e ./third_party_repositories/riscv-arch-test/framework \
  -e ./third_party_repositories/riscv-arch-test/generators/testgen \
  -e ./third_party_repositories/riscv-arch-test/generators/coverage
python3 tools/build_act4.py --act-exe .venv-act4/bin/act
python3 tools/validate_act4_packages.py
```

These commands work in fish and Bash because they invoke the virtual
environment directly; activation is optional. In fish, activation would be
`source .venv-act4/bin/activate.fish`.
This workspace already has the virtual environment, Sail, and the cross
compiler installed. Its ACT build produced 39 self-checking ELFs and packages;
`validate_act4_packages.py` executed all 39 under Sail and checked their host
status mapping.

To also build and validate the official RV64 I Sail software sample:

```bash
python3 tools/build_act4.py --config third_party_repositories/riscv-arch-test/config/sail/sail-RVI20U64/test_config.yaml --output build/act4-rv64 --act-exe .venv-act4/bin/act
python3 tools/validate_act4_packages.py --output build/act4-rv64 --report reports/act4-rv64-summary.json
python3 tools/combined_report.py
```

This workspace produced 51 RV64 I ELFs and packages; all 51 passed direct
Sail execution and host checks. The RV64 report is kept separate from RV32.

To request I, M and C tests on the official RV32 max Sail software sample:

```bash
python3 tools/build_act4.py --config third_party_repositories/riscv-arch-test/config/sail/sail-rv32-max/test_config.yaml --output build/act4-rv32imc --extensions I,M,C --act-exe .venv-act4/bin/act
python3 tools/validate_act4_packages.py --output build/act4-rv32imc --report reports/act4-rv32imc-summary.json
```

ACT 4.1 currently has I and M sources under `tests/rv32i/`, but no C sources.
This request generated 39 I and eight M ELFs, zero C ELFs; all 47 passed
Sail and host validation. The broad RV32 max UDB is a software sample and
does not describe a ProcessorCI core.

The ACT framework installs the pinned UDB Ruby gems through Bundler on its
first build. `tools/build_act4.py` adapts the official Sail RVI20U32 software
or RVI20U64 software configuration to the locally installed tool paths; it writes the adapted YAML
under `build/act4/` and does not modify upstream files. A real ProcessorCI DUT
configuration still needs its actual ISA and memory map before hardware tests
can be called compatible.
