test_program = [0x00F00593, 0x00500613, 0x40C586B3, 0x02D02E23]

import time
import os
import sys

# processor_ci_communication/core/serial.py
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)
from processor_ci_communication.core.serial import ProcessorCIInterface


class Test:
    """
    Construct
    """

    def __init__(self, name, expected, hex_program, port):
        self.name = name
        self.program_hex = hex_program
        self.expected = expected
        self.actual = None
        self.result = False
        self.run_time = 0
        self.port = port

    """
    Run the test and save results to its object
    """

    def run_test(self):
        # Create the communication interface with the processor
        interface = ProcessorCIInterface(
            self.port, 115200, 2
        )   # serial communication timeout
        id = interface.get_module_id()
        interface.set_timeout(1000)   # processor timeout
        interface.set_execution_end_address(60)

        # Run test
        size = len(self.program_hex)
        print(f'Size: {size}')
        interface.write_from_accumulator(size, self.program_hex)
        time_start = time.time()
        interface.execute_until_stop()
        time_end = time.time()
        # Excution time
        self.run_time = time_end - time_start

        # Test result
        self.actual = int.from_bytes(
            interface.read_memory(60, False), byteorder='big'
        )
        self.result = self.actual == self.expected
        print(f'Test {self.name}: {self.result}')
        print(f'Expected: {self.expected}, Actual: {self.actual}')

        interface.close()


# Example usage
if __name__ == '__main__':
    test_obj = Test('Name_test', 0x0000000A, test_program)
    test_obj.run_test()
