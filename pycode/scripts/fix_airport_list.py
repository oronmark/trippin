# import argparse
# import csv
# from pathlib import Path
# from typing import Any, List
# import csv
#
# IATA_INDEX = 13
#
#
# def parse_csv(path: Path) -> List[List[Any]]:
#     data = []
#     with open(path, newline='', encoding='UTF-8') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             if row:
#                 data.append(row)
#         return data
#
#
# def write_csv(path: Path, data: List[List[Any]]):
#     with open(path, 'w+', newline='', encoding='UTF-8') as file:
#         write = csv.writer(file)
#         write.writerows(data)
#
#
# def filter_list_by_condition(data: List[Any], filt) -> List[List[Any]]:
#     filtered_data = []
#     for row in data:
#         if filt(row):
#             filtered_data.append(row)
#
#     return filtered_data
#
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--input-path', required=True, help='absolute path to airports file')
#     parser.add_argument('--output-path', help='absolute path to output file')
#     parser.add_argument('--override', help='indicates whether the output should override the original file')
#     args = parser.parse_args()
#
#     path = Path(args.input_path)
#
#     if not args.output_path and not args.override:
#         raise Exception("must include either an output-path or allow override")
#
#     if args.output_path and args.override:
#         raise Exception("cannot override original file with new output-path")
#
#     data = parse_csv(Path(path))
#     filtered_data = filter_list_by_condition(data, lambda r: r[IATA_INDEX])
#
#     output_path = path if args.override else Path(args.output_path)
#     write_csv(output_path, filtered_data)
#
#
# if __name__ == '__main__':
#     main()
