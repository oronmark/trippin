import argparse
from pathlib import Path
from typing import Any, List
from pycode.tr_utils import read_from_csv_to_lists, write_to_csv

IATA_INDEX = 13
SCHEDULED_SERVICE_INDEX = 11


def filter_list_by_condition(data: List[Any], filt) -> List[List[Any]]:
    filtered_data = []
    for row in data:
        if filt(row):
            filtered_data.append(row)

    return filtered_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-path', required=True, help='absolute path to airports file')
    parser.add_argument('--output-path', help='absolute path to output file')
    parser.add_argument('--override', help='indicates whether the output should override the original file')
    args = parser.parse_args()

    path = Path(args.input_path)

    if not args.output_path and not args.override:
        raise Exception("must include either an output-path or allow override")

    if args.output_path and args.override:
        raise Exception("cannot override original file with new output-path")

    data = read_from_csv_to_lists(Path(path))
    # filtered_data = filter_list_by_condition(data, lambda r: r[IATA_INDEX])
    filtered_data = filter_list_by_condition(data, lambda r: r[SCHEDULED_SERVICE_INDEX] != 'no')

    output_path = path if args.override else Path(args.output_path)
    write_to_csv(output_path, filtered_data)


if __name__ == '__main__':
    main()
