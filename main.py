import os
import json
import argparse
from core.march import parse_march
from core import ProcessorCITest
from core.utils import hex_string_to_bytes


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Script to run tests in a directory'
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
        help='Architecture for the tests',
    )
    parser.add_argument(
        '-e',
        '--extra-tests',
        type=str,
        default='',
        help='Extra tests to run',
    )

    parser.add_argument(
        '-k',
        '--key',
        type=str,
        default='',
        help='Key to sync with the board',
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        default=1000,
        help='Timeout for the tests in cicles of clock',
    )
    # core_use_two_memories
    parser.add_argument(
        '-ctm',
        '--core-use-two-memories',
        action='store_true',
        help='Use two memories in the core',
        default=False,
    )

    args = parser.parse_args()

    config_data = None
    extra_tests_parse = args.extra_tests.split(',') if args.extra_tests else []

    with open(args.config) as f:
        config_data = json.load(f)

    parsed_arch = parse_march(args.march)
    XLEN = parsed_arch['xlen']
    MARCH = parsed_arch['extensions']
    XLEN_STR = str(XLEN)

    directories = config_data['test_directories']
    print(directories[0]['name'][2:4])
    directories = [
        dir
        for dir in directories
        if (dir['name'][2:4] == XLEN_STR or XLEN == 64)
        and dir['name'][4:] in MARCH
    ]
    extra_tests = config_data['extra_tests']
    extra_tests = [
        test for test in extra_tests if test['name'] in extra_tests_parse
    ]

    sync_key_hex = hex_string_to_bytes(args.key)

    p_tester = ProcessorCITest(
        port=args.port,
        baudrate=args.baudrate,
        serial_timeout=args.serial_timeout,
        sync_keyword=sync_key_hex,
        timeout=args.timeout,
        directories=directories,
        extra_tests=extra_tests,
        core_use_two_memories=args.core_use_two_memories,
    )
    p_tester.run_tests()
    p_tester.run_extra_tests()
    p_tester.generate_junit_report()
    print('All tests finished.')


if __name__ == '__main__':
    main()
