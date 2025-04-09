import argparse
import json
import Directory


def main():
    parser = argparse.ArgumentParser()
    # Directory json file with the directories to run
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--port', type=str, required=True)
    args = parser.parse_args()
    with open(args.config) as f:
        data = json.load(f)
    for directory in data['test_directories']:
        print(f'Running tests in {directory}')
        dir = Directory.Directory(directory.get('path'), args.port)
        dir.run()


if __name__ == '__main__':
    main()
