import time
import os
import sys

# processor_ci_communication/core/serial.py
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)
from processor_ci_communication.core.serial import ProcessorCIInterface
from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error, Failure

# TEST_CATEGORIES = ['basic', 'advanced', 'invalid']
TEST_CATEGORIES = ['basic']


class ProcessorCITest:
    def __init__(
        self,
        port: str = '/dev/ttyUSB0',
        baudrate: int = 115200,
        serial_timeout: int = 1,
        sync_keyword: int = 0x4E455859,
        timeout: int = 1000,
        directories: list[dict] = [],
        extra_tests: list[dict] = [],
        core_use_two_memories: bool = False,
    ):
        self.port = port
        self.baudrate = baudrate
        self.serial_timeout = serial_timeout
        self.sync_keyword = sync_keyword
        self.timeout = timeout
        self.directories = directories
        self.extra_tests = extra_tests
        self.core_use_two_memories = core_use_two_memories

        self.xml = JUnitXml()

        self.processor_ci = ProcessorCIInterface(
            self.port, self.baudrate, self.serial_timeout
        )

        id = self.processor_ci.get_module_id()

        if id is None:
            print('Failed to get module ID. Exiting.')
            sys.exit(1)

        print(f'Connected to FPGA with ID: {id}')

        print('Checking for sync keyword...')
        if id != self.sync_keyword:
            print(
                f'Sync keyword mismatch. Expected: {self.sync_keyword}, Got: {id}'
            )
            sys.exit(1)

        print('Sync keyword matched.')
        self.processor_ci.set_timeout(self.timeout)
        self.processor_ci.load_msb_accumulator(0)
        self.processor_ci.load_lsb_accumulator(0)

        print('Testsuite configurated.')

    def _execute_test(
        self, test_path: str, reference_path: str, breakpoint: int
    ) -> tuple[bool, int, int]:   # result, expected, received
        test_file = open(test_path, 'r')
        reference_file = open(reference_path, 'r')

        test_content = []
        test_lines = test_file.readlines()
        test_len = len(test_lines)

        for i in range(0, breakpoint + 4, 4):
            shiffted = i >> 2
            if shiffted >= test_len:
                test_content.append(0)
            else:
                test_content.append(int(test_lines[shiffted], 16))
        test_file.close()

        self.processor_ci.write_from_accumulator(
            (breakpoint + 4) >> 2, test_content
        )

        if(self.core_use_two_memories):
            self.processor_ci.write_memory(
                breakpoint, 0, self.core_use_two_memories)

        self.processor_ci.execute_until_stop()

        reference_lines = reference_file.readlines()
        reference_content = [int(data, 16) for data in reference_lines]

        ok = True
        expected = 0
        received = 0

        difference_address = (len(reference_content) - 1) << 2

        for i in reference_content:
            received = int.from_bytes(
                self.processor_ci.read_memory(
                    breakpoint - difference_address, self.core_use_two_memories
                )
            )
            expected = i

            if expected != received:
                ok = False
                break

            difference_address -= 4

        return ok, expected, received

    def _run_test_dir(self, config: dict) -> None:
        path = config['path']
        name = config['name']

        print(f'Running tests: {name} in {path}')

        if not os.path.exists(path):
            raise FileNotFoundError(f'Test directory {path} does not exist.')

        for category in TEST_CATEGORIES:
            suite = TestSuite(f'{name}.{category}')

            category_path = os.path.join(path, category)
            category_breakpoint = config.get(f'{category}_breakpoint', 50)
            memory_files_path = os.path.join(category_path, 'memory')
            referece_files_path = os.path.join(category_path, 'reference')

            self.processor_ci.set_execution_end_address(category_breakpoint)

            print(
                f'Running {category} tests in {category_path}, with breakpoint {category_breakpoint}'
            )

            memory_files = sorted(os.listdir(memory_files_path))
            reference_files = sorted(os.listdir(referece_files_path))

            if len(memory_files) != len(reference_files):
                raise ValueError(
                    f'Memory files and reference files count mismatch in {category_path}.'
                )

            for memory_file, reference_file in zip(
                memory_files, reference_files
            ):
                memory_file_path = os.path.join(memory_files_path, memory_file)
                reference_file_path = os.path.join(
                    referece_files_path, reference_file
                )

                print(f'Running test: {memory_file}')

                result, expected, received = self._execute_test(
                    memory_file_path, reference_file_path, category_breakpoint
                )

                if result:
                    test_case = TestCase(
                        name=f'{memory_file}', classname=f'{name}.{category}'
                    )
                    suite.add_testcase(test_case)
                else:
                    test_case = TestCase(
                        name=f'{memory_file}',
                        classname=f'{name}.{category}',
                    )
                    test_case.result = [Failure(
                        f'Expected: {expected}, Received: {received}'
                    )]
                    suite.add_testcase(test_case)

            self.xml.add_testsuite(suite)

    def run_tests(self):
        for dir in self.directories:
            self._run_test_dir(dir)

    def run_extra_tests(self):
        ...

    def generate_junit_report(self):
        # Generate JUnit XML report
        current_time = time.time()
        self.xml.write(f'test_results_{current_time}.xml')
        print(f'JUnit XML report generated: test_results_{current_time}.xml')
