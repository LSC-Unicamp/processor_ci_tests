test_path = 'processor_ci_tests/testing_tests/TEST2'

import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import Test


class Directory:
    def __init__(self, path, port):
        self.port = port
        self.path = path
        self.tests = {'basic': [], 'advanced': [], 'invalid': []}
        self.categories = ['basic', 'advanced', 'invalid']

    # loads a test from a file
    def _load_test(self, category, test_path, reference_path):
        try:
            name = os.path.basename(test_path).split('.')[0]
            with open(reference_path, 'r') as reference_file:
                reference = int(reference_file.read(), 16)
            with open(test_path, 'r') as hex_test_file:
                hex_test = [
                    int(line, 16)
                    for line in hex_test_file.read().split('\n')
                    if line
                ]
            test = Test.Test(name, reference, hex_test, self.port)
            self.tests[category].append(test)
        except Exception as e:
            print(f'Error loading test {test_path}: {e}')

    # searchs for the tests in the given path
    def load_tests(self):
        for root, dirs, files in os.walk(self.path):
            if 'memory' in root:
                for file in files:
                    if file.endswith('.hex'):
                        test_path = os.path.join(root, file)
                        reference_path = os.path.join(
                            root.replace('memory', 'reference'), file
                        )
                        if os.path.exists(reference_path):
                            for category in self.categories:
                                if category in root:
                                    self._load_test(
                                        category, test_path, reference_path
                                    )
                                    break

    def run_tests(self):
        for category in self.tests:
            for test in self.tests[category]:
                test.run_test()
                print(test.result)
                print(test.actual)
                print(test.run_time)

    def create_xml_report(self, output_file='test_results.xml'):
        if os.path.exists(output_file):
            tree = ET.parse(output_file)
            testsuites = tree.getroot()
        else:
            testsuites = ET.Element('testsuites')

        for category in self.tests:
            testsuite = ET.SubElement(
                testsuites,
                'testsuite',
                name=f'{self.port}-{category}-{os.path.basename(self.path)}',
            )
            # Sort the tests by name
            sorted_tests = sorted(
                self.tests[category], key=lambda test: test.name
            )
            for test in sorted_tests:
                testcase = ET.SubElement(testsuite, 'testcase', name=test.name)
                if not test.result:
                    failure = ET.SubElement(
                        testcase, 'failure', message='Test failed'
                    )
                    failure.text = (
                        f'Expected: {test.expected}, Actual: {test.actual}'
                    )
                ET.SubElement(
                    testcase, 'system-out'
                ).text = f'Run time: {test.run_time}'

        # Convert the ElementTree to a string
        rough_string = ET.tostring(testsuites, 'utf-8')
        # Parse the string using minidom
        reparsed = xml.dom.minidom.parseString(rough_string)
        # Pretty print the XML
        pretty_xml_as_string = '\n'.join(
            [
                line
                for line in reparsed.toprettyxml(indent='  ').split('\n')
                if line.strip()
            ]
        )

        # Write the pretty-printed XML to the file
        with open(output_file, 'w') as f:
            f.write(pretty_xml_as_string)

    def run(self):
        self.load_tests()
        self.run_tests()
        self.create_xml_report()


def main():
    dir_test = Directory(test_path)
    dir_test.load_tests()
    dir_test.run_tests()
    dir_test.create_xml_report()
    print(dir_test.tests)


if __name__ == '__main__':
    main()
