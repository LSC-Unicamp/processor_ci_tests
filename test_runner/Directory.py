test_path = 'processor_ci_tests/testing_tests/TEST1'

import Test
import os

class Directory:

    def __init__(self, path):
        self.path = path
        self.tests = {
            'basic': [],
            'advanced': [],
            'invalid': []
        }

    # loads a test from a file
    def _load_test(self, category, test_path, reference_path):
        name = os.path.basename(test_path).split('.')[0]
        with open(reference_path, 'r') as reference_file:
            reference = int(reference_file.read(), 16)
        with open(test_path, 'r') as hex_test_file:
            hex_test = [int(line, 16) for line in hex_test_file.read().split('\n') if line]
        test = Test.Test(name, reference, hex_test)
        self.tests[category].append(test)
    
    # searchs for the tests in the given path
    def load_tests(self):
        for root, dirs, files in os.walk(self.path):
            if 'memory' in root:
                for file in files:
                    if file.endswith('.hex'):
                        test_path = os.path.join(root, file)
                        reference_path = os.path.join(root.replace('memory', 'reference'), file)
                        if os.path.exists(reference_path):
                            if 'basic' in root:
                                self._load_test('basic', test_path, reference_path)
                            elif 'advanced' in root:
                                self._load_test('advanced', test_path, reference_path)
                            elif 'invalid' in root:
                                self._load_test('invalid', test_path, reference_path)
        
    def run_tests(self):
        pass

    def create_xml_report(self):
        pass

def main():
    dir_test = Directory(test_path)
    dir_test.load_tests()
    print(dir_test.tests)

if __name__ == '__main__':
    main()
