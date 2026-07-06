import argparse
import json

from riscv_test_runner.core.march import parse_march
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
        required=True,
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
        required=True,
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

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    from riscv_test_runner.core.runner import ProcessorCITest

    extra_tests_parse = args.extra_tests.split(',') if args.extra_tests else []

    with open(args.config, encoding='utf-8') as config_file:
        config_data = json.load(config_file)

    parsed_arch = parse_march(args.march)
    xlen = parsed_arch['xlen']
    extensions = parsed_arch['extensions']
    xlen_str = str(xlen)

    directories = [
        directory
        for directory in config_data['test_directories']
        if (
            directory['name'][2:4] == xlen_str or xlen == 64
        )
        and directory['name'][4:] in extensions
    ]
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
    )
    tester.run_tests()
    tester.run_extra_tests()
    tester.generate_junit_report()
    print('All tests finished.')


if __name__ == '__main__':
    main()
