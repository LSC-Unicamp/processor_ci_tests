import argparse
import json
import re
from pathlib import Path

from riscv_test_runner.core.selection import isa_compatible, select_directories
from riscv_test_runner.core.utils import hex_string_to_bytes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Run Processor CI tests against a RISC-V core over serial'
    )

    parser.add_argument(
        '-b',
        '--baudrate',
        type=int,
        default=115200,
        help='Baudrate for serial connection',
    )
    parser.add_argument(
        '-p',
        '--port',
        type=str,
        required=False,
        help='Port for serial connection',
    )
    parser.add_argument(
        '-s',
        '--serial-timeout',
        type=int,
        default=5,
        help='Serial timeout in seconds',
    )
    parser.add_argument(
        '-c',
        '--config',
        type=str,
        default=str(Path(__file__).resolve().parents[1] / 'config.json'),
        help='Path to the configuration file',
    )
    parser.add_argument(
        '-m',
        '--march',
        type=str,
        default='rv32i',
        help='RISC-V architecture string for the tests',
    )
    parser.add_argument(
        '-e',
        '--extra-tests',
        type=str,
        default='',
        help='Comma-separated list of extra tests to run',
    )
    parser.add_argument(
        '-k',
        '--key',
        type=str,
        default='',
        help='Hex key used to sync with the board',
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        default=1000,
        help='Timeout for the tests in clock cycles',
    )
    parser.add_argument(
        '-ctm',
        '--core-use-two-memories',
        action='store_true',
        help='Use separate instruction and data memories in the core',
        default=False,
    )
    parser.add_argument('--suite', default='basic', help='Comma-separated suites: basic,advanced,arch,invalid')
    parser.add_argument('--act-profile', choices=('cv32e40s-512k',),
                        help='Select a verified ACT DUT memory and serial profile')
    parser.add_argument('--act-report', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'reports/act4-cv32e40s-device.json',
                        help='JSON and JUnit output for a selected ACT DUT run')
    parser.add_argument('--host-timeout', type=float, default=120.0,
                        help='Host wait for each ACT execution response, in seconds')
    parser.add_argument('--list', action='store_true', help='List selected tests without serial hardware')
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument('--instruction', help='List one basic instruction mnemonic, such as addi or c.addi')
    selector.add_argument('--scenario', help='List one advanced scenario ID')
    parser.add_argument('--category', help='List one advanced scenario category')
    parser.add_argument('--test-id', help='List one exact package or legacy test ID')

    return parser


def _matches_filters(metadata: dict, args: argparse.Namespace) -> bool:
    source = metadata.get('test_source')
    return (not args.test_id or metadata.get('test_id') == args.test_id) and (
        not args.instruction or source == 'basic' and metadata.get('target_instruction') == args.instruction
    ) and (
        not args.scenario or source == 'advanced' and metadata.get('test_id') == args.scenario
    ) and (
        not args.category or source == 'advanced' and metadata.get('category') == args.category
    )


def main(argv: list[str] | None = None) -> None:
    import sys
    selected = list(sys.argv[1:] if argv is None else argv)
    if '--tool' in selected:
        index = selected.index('--tool')
        if index + 1 >= len(selected):
            raise SystemExit('--tool requires directed or riscv-dv')
        tool = selected[index + 1]
        del selected[index:index + 2]
        if tool == 'riscv-dv':
            from riscv_test_runner.riscv_dv import main as generate_riscv_dv
            generate_riscv_dv(selected)
            return
        if tool != 'directed':
            raise SystemExit(f'unsupported test tool: {tool}')
        argv = selected
    args = build_parser().parse_args(argv)

    extra_tests_parse = args.extra_tests.split(',') if args.extra_tests else []

    with open(args.config, encoding='utf-8') as config_file:
        config_data = json.load(config_file)

    suites = tuple(s.strip() for s in args.suite.split(',') if s.strip())
    if not suites or any(s not in ('basic', 'advanced', 'arch', 'invalid') for s in suites):
        raise SystemExit('Supported suites: basic, advanced, arch, invalid')
    if args.act_profile and suites != ('arch',):
        raise SystemExit('--act-profile requires --suite arch alone')
    if args.act_profile and (args.instruction or args.scenario or args.category):
        raise SystemExit('ACT DUT selection supports --test-id and --march filters')
    directories = select_directories(config_data, args.march)
    root = Path(__file__).resolve().parents[1]
    directories = [{**d, 'path': str(root / 'tests' / d['name'])} for d in directories]
    if args.list:
        if 'basic' in suites:
            for package in sorted((root / 'build' / 'basic-sail').glob('*.json')):
                metadata = json.loads(package.read_text())
                if isa_compatible(metadata['isa'], args.march) and _matches_filters(metadata, args):
                    print(f'package basic {package.stem}')
        if 'arch' in suites:
            arch_dir = ('act4-cv32e40s' if args.act_profile else 'act4')
            for package in sorted((root / 'build' / arch_dir / 'packages').glob('*.json')):
                metadata = json.loads(package.read_text())
                if isa_compatible(metadata['isa'], args.march) and _matches_filters(metadata, args):
                    print(f'ACT4 arch {package.stem}')
        if 'invalid' in suites:
            for package in sorted((root / 'build' / 'invalid-sail').glob('*.json')):
                metadata = json.loads(package.read_text())
                if isa_compatible(metadata['isa'], args.march) and _matches_filters(metadata, args):
                    print(f"package invalid {metadata['test_id']}")
        if 'advanced' in suites:
            advanced_packages = sorted((root / 'build' / 'advanced-sail').glob('*.json'))
            if advanced_packages:
                for package in advanced_packages:
                    metadata = json.loads(package.read_text())
                    if isa_compatible(metadata['isa'], args.march) and _matches_filters(metadata, args):
                        print(f'package advanced {package.stem}')
            else:
                for source in sorted((root / 'tests').glob('RV*I/advanced/src/scenarios/*.S')):
                    header = source.read_text().splitlines()[0]
                    isa = header.split('ISA: ')[-1]
                    category = header.split('category: ', 1)[1].split(';', 1)[0] if 'category: ' in header else None
                    metadata = {'test_source': 'advanced', 'test_id': source.stem, 'category': category}
                    if isa_compatible(isa, args.march) and _matches_filters(metadata, args):
                        print(f'RV32 advanced source {source.stem}')
        for directory in directories:
            for suite in suites:
                if suite in ('advanced', 'arch', 'invalid'):
                    continue
                base = Path(directory['path']) / suite
                for path in sorted((base / 'memory').glob('*.hex')):
                    mnemonic = re.sub(r'^\d+-', '', path.stem)
                    if directory['name'].endswith('C'):
                        mnemonic = re.sub(r'^c(?!\.)', 'c.', mnemonic)
                    legacy = {'test_source': 'basic', 'test_id': f"{directory['name']}-{path.stem}",
                              'target_instruction': mnemonic}
                    if _matches_filters(legacy, args):
                        print(f"{directory['name']} {suite} {path.stem}")
        return
    if args.act_profile:
        if not args.port:
            raise SystemExit('--port is required for ACT DUT serial execution')
        if args.host_timeout <= 0:
            raise SystemExit('--host-timeout must be positive')
        import sys
        sys.path.insert(0, str(root / 'tools'))
        from run_act4_cv32e40s_serial import execute, select, write_report
        paths = []
        for path in sorted((root / 'build/act4-cv32e40s/packages').glob('*.json')):
            metadata = json.loads(path.read_text())
            if isa_compatible(metadata['isa'], args.march) and _matches_filters(metadata, args):
                paths.append(path)
        if not paths:
            raise SystemExit('No compatible ACT packages found for the selected DUT profile')
        results = execute(select(paths), port=args.port, baudrate=args.baudrate,
                          expected_id=hex_string_to_bytes(args.key) if args.key else None,
                          host_timeout=args.host_timeout)
        write_report(args.act_report, results)
        print(f'ACT DUT run: {len(results)} packages; report: {args.act_report}')
        if any(row['outcome'] != 'PASS' for row in results):
            raise SystemExit(1)
        return
    if args.instruction or args.scenario or args.category or args.test_id:
        raise SystemExit('Test filters require --list until serial package selection is verified')
    if not args.port:
        raise SystemExit('--port is required for serial execution')
    if any(s in suites for s in ('advanced', 'arch', 'invalid')):
        raise SystemExit('Advanced/ACT4/invalid packages require verified serial sparse loading and stop-cause handling')
    from riscv_test_runner.core.runner import ProcessorCITest
    extra_tests = [
        test
        for test in config_data['extra_tests']
        if test['name'] in extra_tests_parse
    ]

    tester = ProcessorCITest(
        port=args.port,
        baudrate=args.baudrate,
        serial_timeout=args.serial_timeout,
        sync_keyword=hex_string_to_bytes(args.key),
        timeout=args.timeout,
        directories=directories,
        extra_tests=extra_tests,
        core_use_two_memories=args.core_use_two_memories,
        categories=suites,
    )
    tester.run_tests()
    tester.run_extra_tests()
    tester.generate_junit_report()
    print('All tests finished.')


if __name__ == '__main__':
    main()
