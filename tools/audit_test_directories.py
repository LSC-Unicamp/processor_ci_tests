"""Reconcile legacy test triples, package suites, and configured extra tests."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from isa_audit import ROOT, legacy_hex

REPORT = ROOT / "reports/isa-audit/test_directories.json"
SUITES = {"basic": "basic-sail", "advanced": "advanced-sail", "invalid": "invalid-sail"}


def _source_has_instruction(path: Path) -> bool:
    for line in path.read_text(errors="replace").splitlines():
        code = line.split("#", 1)[0].strip()
        if re.match(r"[A-Za-z][A-Za-z0-9.]*\s", code):
            return True
    return False


def _legacy(base: Path) -> dict:
    sources = {path.stem: path for path in (base / "src").glob("*.s")}
    memory = {path.stem: path for path in (base / "memory").glob("*.hex")}
    reference = {path.stem: path for path in (base / "reference").glob("*.hex")}
    substantive = {stem for stem, path in sources.items() if _source_has_instruction(path)}
    return {
        "sources": len(sources), "instruction_bodies": len(substantive),
        "memory_words": sum(legacy_hex(path)[0] == "words" for path in memory.values()),
        "reference_words": sum(legacy_hex(path)[0] == "words" for path in reference.values()),
        "reference_placeholders": sum(legacy_hex(path)[0] == "placeholder" for path in reference.values()),
        "missing_memory": sorted(sources.keys() - memory.keys()),
        "missing_reference": sorted(sources.keys() - reference.keys()),
        "orphan_memory": sorted(memory.keys() - sources.keys()),
        "orphan_reference": sorted(reference.keys() - sources.keys()),
        "substantive_without_numeric_reference": sorted(
            stem for stem in substantive if legacy_hex(reference.get(stem, Path()))[0] != "words"),
    }


def _packages(root: Path) -> tuple[dict, list[dict]]:
    by_group = defaultdict(lambda: defaultdict(list))
    issues = []
    qemu_summary = root / "build/advanced/summary.json"
    advanced_sources = ({row["id"]: row["source"]
                         for row in json.loads(qemu_summary.read_text())["results"]}
                        if qemu_summary.is_file() else {})
    for suite, folder in SUITES.items():
        for path in sorted((root / "build" / folder).glob("*.json")):
            package = json.loads(path.read_text())
            if package.get("test_source") != suite:
                continue
            if suite == "basic":
                group = package["test_id"].split("-", 1)[0]
                source = f"tests/{group}/basic/package_src/{package['target_instruction']}.S"
            elif suite == "advanced":
                source = advanced_sources.get(package["test_id"])
                group = source.split("/")[1] if source else "unknown"
            else:
                source = package.get("source_path")
                group = source.split("/")[1] if source else "unknown"
            by_group[group][suite].append({"id": package["test_id"], "source": source,
                                           "package": str(path.relative_to(root)),
                                           "validated": package.get("reference_validated") is True})
            if not source or not (root / source).is_file():
                issues.append({"severity": "error", "group": group, "suite": suite,
                               "detail": f"package {package['test_id']} has no source at {source}"})
            if not package.get("reference_validated"):
                issues.append({"severity": "error", "group": group, "suite": suite,
                               "detail": f"package {package['test_id']} lacks reference validation"})
    return by_group, issues


def generate(root: Path = ROOT, output: Path = REPORT, *, include_extra_tests: bool = False) -> dict:
    config = json.loads((root / "config.json").read_text())
    configured = {entry["name"] for entry in config["test_directories"]}
    packages, issues = _packages(root)
    retirement_manifest = root / "tools/legacy_advanced_retired.txt"
    retired_sources = retirement_manifest.read_text().splitlines() if retirement_manifest.is_file() else []
    for source in retired_sources:
        path = root / source
        companions = [path.parent.parent / folder / f"{path.stem}.hex"
                      for folder in ("memory", "reference")]
        if path.exists() or any(companion.exists() for companion in companions):
            issues.append({"severity": "error", "group": path.parents[2].name, "suite": "advanced",
                           "detail": f"retired placeholder triple reappeared: {source}"})
    groups = []
    for directory in sorted((root / "tests").glob("RV*")):
        if not directory.is_dir():
            continue
        group = directory.name
        legacy = {suite: _legacy(directory / suite) for suite in SUITES}
        package_rows = {}
        for suite in SUITES:
            sources = {str(path.relative_to(root)) for path in (directory / suite / "package_src").glob("*.S")}
            if suite == "advanced":
                sources = {str(path.relative_to(root)) for path in (directory / suite / "src/scenarios").glob("*.S")}
            built = packages[group][suite]
            recorded = {row["source"] for row in built if row["source"]}
            package_rows[suite] = {"sources": len(sources), "validated_packages": sum(row["validated"] for row in built),
                                   "sources_without_package": sorted(sources - recorded),
                                   "packages_without_source": sorted(recorded - sources)}
            if sources - recorded:
                issues.append({"severity": "error", "group": group, "suite": suite,
                               "detail": f"{len(sources - recorded)} package sources have no built package"})
            if recorded - sources:
                issues.append({"severity": "error", "group": group, "suite": suite,
                               "detail": f"{len(recorded - sources)} packages have no suite source"})
        advanced = legacy["advanced"]
        if advanced["missing_reference"]:
            example = ", ".join(advanced["missing_reference"][:3])
            issues.append({"severity": "legacy_gap", "group": group, "suite": "advanced",
                           "detail": f"{len(advanced['missing_reference'])} legacy sources lack reference files (e.g. {example})"})
        if advanced["orphan_reference"]:
            example = ", ".join(advanced["orphan_reference"][:3])
            issues.append({"severity": "legacy_gap", "group": group, "suite": "advanced",
                           "detail": f"{len(advanced['orphan_reference'])} reference files have no matching source (e.g. {example})"})
        if advanced["substantive_without_numeric_reference"]:
            issues.append({"severity": "legacy_gap", "group": group, "suite": "advanced",
                           "detail": f"{len(advanced['substantive_without_numeric_reference'])} executable legacy sources have no numeric reference"})
        groups.append({"group": group, "configured_legacy": group in configured,
                       "legacy": legacy, "packages": package_rows})
    extras = []
    runner = (root / "riscv_test_runner/core/runner.py").read_text()
    extra_runner_implemented = not re.search(r"def run_extra_tests\(self\):\s*\.\.\.", runner)
    for entry in config.get("extra_tests", []) if include_extra_tests else []:
        name = entry["name"]
        test_dir = root / "tests" / name
        benchmark_dir = root / "benchmarks" / name
        test_files = [path for path in test_dir.rglob("*") if path.is_file() and path.stat().st_size]
        benchmark_sources = list(benchmark_dir.glob("*.c")) + list(benchmark_dir.glob("*.S"))
        row = {"name": name, "test_directory": test_dir.is_dir(),
               "nonempty_test_files": len(test_files), "benchmark_sources": len(benchmark_sources),
               "runner_implemented": extra_runner_implemented}
        extras.append(row)
        if not test_files or not extra_runner_implemented:
            issues.append({"severity": "unavailable", "group": name, "suite": "extra",
                           "detail": "configured extra test has no runnable assets or runner implementation"})
    report = {"configured_legacy_groups": len(configured),
              "package_only_groups": sum(not row["configured_legacy"] for row in groups),
              "extra_tests_included": include_extra_tests,
              "retired_legacy_advanced_placeholders": len(retired_sources),
              "package_totals": {suite: sum(row["packages"][suite]["validated_packages"] for row in groups)
                                 for suite in SUITES},
              "groups": groups, "extra_tests": extras, "issues": issues,
              "notes": ["Z-extension groups use package_src and need no legacy hex/reference triples.",
                        "ACT 4.1 tests are built under build/act4, outside tests/.",
                        "Each configured ISA group has at least one package-based advanced scenario.",
                        "The 82 executable legacy arithmetic/control-flow cases have a separate Sail replay; the timer case has a separate RTL unit probe."]}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    rows = ["# Test directory audit", "",
            "Counts distinguish legacy `src/memory/reference` assets from executable package suites.",
            "A blank legacy triple in a Z-extension group is intentional; its basic package is the executable test.", "",
            "| Group | Configured legacy | Basic packages | Advanced packages | Invalid packages | Legacy basic bodies/sources | Legacy advanced bodies/sources | Advanced without numeric oracle |",
            "|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in groups:
        p, l = row["packages"], row["legacy"]
        rows.append(f"| {row['group']} | {'yes' if row['configured_legacy'] else 'no'} | "
                    f"{p['basic']['validated_packages']} | {p['advanced']['validated_packages']} | "
                    f"{p['invalid']['validated_packages']} | "
                    f"{l['basic']['instruction_bodies']}/{l['basic']['sources']} | "
                    f"{l['advanced']['instruction_bodies']}/{l['advanced']['sources']} | "
                    f"{len(l['advanced']['substantive_without_numeric_reference'])} |")
    rows += ["", f"Validated package totals: basic {report['package_totals']['basic']}, "
             f"advanced {report['package_totals']['advanced']}, "
             f"invalid {report['package_totals']['invalid']}.",
             f"Retired comment-only legacy advanced triples: {len(retired_sources)} "
             "(paths in `tools/legacy_advanced_retired.txt`)."]
    rows += ["", "## Findings", ""]
    rows += ([f"- **{issue['severity']}** {issue['group']} {issue['suite']}: {issue['detail']}"
              for issue in issues] if issues else ["No ISA directory findings."])
    if include_extra_tests:
        rows += ["", "## Configured extra tests", "",
                 "| Name | Test directory | Nonempty test files | Benchmark sources | Runner implemented |",
                 "|---|---|---:|---:|---|"]
        rows += [f"| {row['name']} | {'yes' if row['test_directory'] else 'no'} | "
                 f"{row['nonempty_test_files']} | {row['benchmark_sources']} | "
                 f"{'yes' if row['runner_implemented'] else 'no'} |" for row in extras]
    rows += ["", "## Interpretation", ""] + [f"- {note}" for note in report["notes"]]
    rows += ["", "Configured `/eda/processor_ci_tests/...` paths are environment-specific; "
             "the package CLI resolves ISA groups from this checkout before listing them."]
    if not include_extra_tests:
        rows += ["", "Configured extra tests are outside this audit's current scope."]
    (output.parent / "test_directories.md").write_text("\n".join(rows) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-extra-tests", action="store_true")
    args = parser.parse_args()
    result = generate(include_extra_tests=args.include_extra_tests)
    print(f"Audited {len(result['groups'])} ISA groups and {len(result['extra_tests'])} extra tests; "
          f"{len(result['issues'])} findings")
