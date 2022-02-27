import argparse
import csv
from pathlib import Path


def parse_airports_csv(path: Path):
    airports = []
    with open('C:\\Users\\Vicki\\projects\\trippin\\trippin\\resources\\airports.csv', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            print(', '.join(row))


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--input-path', required=True, help='absolute path to airports file')
    # parser.add_argument('--output-path', help='absolute path to output file')
    # parser.add_argument('--override', help='indicates whether the output should override the original file')
    # args = parser.parse_args()
    #
    # path = args.input_path
    #
    # if args.output_path and args.override:
    #     raise Exception("cannot override original file with new output-path")
    print('bla')
    parse_airports_csv(Path('C:\\Users\\Vicki\\projects\\trippin\\trippin\\resources\\airports.csv'))
    print('bla')


if __name__ == '__main__':
    main()