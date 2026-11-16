"""Execute advanced scenarios under Sail using their existing self-checks."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from advanced_cases import CASES, VECTOR_SCENARIO_LMUL, VECTOR_SCENARIO_PROFILES, source
from build_advanced import elf_segments, symbols
from build_basic_sail import CONFIG, GCC, ROOT, SAIL
sys.path.insert(0, str(ROOT))
from riscv_test_runner.core.package import initial_memory, outcome


def sail_source(case: tuple) -> str:
    original = source(case)
    march = case[2]
    base, *named = march.split("_")
    fp_enabled = bool(set(base[4:]) & {"f", "d"}) or any(
        ext.startswith("zve") and ext.endswith(("f", "d")) for ext in named)
    vector_enabled = "v" in base[4:] or any(ext.startswith("zve") for ext in named)
    state = (0x6000 if fp_enabled else 0) | (0x600 if vector_enabled else 0)
    if state:
        original = original.replace("_start:\n", f"_start:\nli t6, {state:#x}\ncsrs mstatus, t6\n", 1)
    completion = '''beqz a0, 1f
li t2, 3
j 2f
1: li t2, 1
2: la t1, tohost
sw t2, 0(t1)
sw zero, 4(t1)
3: j 3b'''
    if original.count("li a7, 93\necall") != 1:
        raise ValueError("advanced completion template changed")
    return (original.replace("li a7, 93\necall", completion) +
            '.section .tohost,"aw",@progbits\n.balign 8\n.global tohost\ntohost: .dword 0\n.global fromhost\nfromhost: .dword 0\n')


def validate(output: Path = ROOT / "build/advanced-sail") -> dict:
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for case in CASES:
        name, category, march, expected, _ = case
        xlen = 64 if march.startswith("rv64") else 32
        src = output / f"{name}.S"
        src.write_text(sail_source(case))
        elf = output / f"{name}.elf"
        subprocess.run([GCC, "-nostdlib", "-static", f"-march={march}", "-mabi=lp64" if xlen == 64 else "-mabi=ilp32",
                        "-Wl,-Ttext=0x80000000", "-Wl,--no-relax", str(src), "-o", str(elf)],
                       check=True, capture_output=True, text=True)
        config = (CONFIG.parent.parent / "sail-RVI20U64/sail.json" if xlen == 64 else
                  CONFIG.parent.parent / "sail-rv32-max/sail.json" if "zve" in march else CONFIG)
        run = subprocess.run([str(SAIL), "--config", str(config), str(elf)],
                             capture_output=True, text=True, timeout=10)
        if run.returncode or "SUCCESS" not in run.stdout:
            raise RuntimeError(f"Sail rejected {name}: {run.stdout} {run.stderr}")
        entry, segments = elf_segments(elf)
        status = symbols(elf)["tohost"]
        package = {"schema_version": 1, "test_source": "advanced", "test_id": name,
                   "category": category, "isa": march, "entry": entry, "segments": segments,
                   "oracle": {"type": "selfcheck_tohost", "address": status,
                              "pass_value": 1, "failure_rule": "odd value greater than 1"},
                   "completion": {"type": "tohost_write", "max_cycles": 10000},
                   "expected_a0": expected & ((1 << xlen) - 1), "reference_model": "Sail 0.13.1",
                   "reference_validated": True, "hardware_execution": "pending"}
        if category == "vector":
            extension, sew, vl = VECTOR_SCENARIO_PROFILES[name]
            package["vector_profile"] = {"extension": extension,
                                         "minimum_vlen_bits": 128, "sew_bits": sew,
                                         "lmul": VECTOR_SCENARIO_LMUL.get(name, "m1"),
                                         "vl": vl, "reference_vlen_bits": 1024}
        memory = initial_memory(package, supported_isa={march})
        if outcome(package, memory, stopped=False) != "INCONCLUSIVE":
            raise RuntimeError(f"advanced package initialized with completion: {name}")
        memory[status] = 1
        if outcome(package, memory, stopped=True) != "PASS":
            raise RuntimeError(f"advanced package host check failed: {name}")
        (output / f"{name}.json").write_text(json.dumps(package, indent=2) + "\n")
        results.append({"id": name, "category": category, "march": march,
                        "expected_a0": expected & ((1 << xlen) - 1),
                        "package": str((output / f"{name}.json").relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output / f"{name}.json"),
                        "sail_validated": True, "host_mock_validated": True})
    report = {"scenarios": len(results), "sail_validated": len(results),
              "host_mock_validated": len(results), "hardware_validated": 0, "results": results}
    (ROOT / "reports/advanced-sail-summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    report = validate()
    print(f"Advanced Sail: {report['sail_validated']}/{report['scenarios']} validated")
