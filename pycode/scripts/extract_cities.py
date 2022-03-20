import argparse
from pathlib import Path
from typing import List, Optional, Dict

import django

django.setup()
from pycode.tr_utils import read_from_csv_to_lists, write_to_csv_from_lists


def parse_line(line: str) -> Optional[Dict[str, str]]:
    def norm_val(v: str):
        v = v.replace('\xa0', '')
        return v.replace('Â', '')

    i_col1 = line.find('column-1')

    if i_col1 is not -1:

        i_col1_end = line.find('</td>', i_col1)
        city = line[i_col1 + 10: i_col1_end]

        i_col2 = line.find('column-2')
        i_col2_end = line.find('</td>', i_col2)
        country = line[i_col2 + 10: i_col2_end]

        i_col3 = line.find('column-3')
        i_col3_end = line.find('</td>', i_col3)
        code = line[i_col3 + 10: i_col3_end]

        if code.find('All') is not -1:
            return {'city': norm_val(city),
                    'country': norm_val(country),
                    'code': norm_val(code[:3])}
    return None


def parse_metro_line(line: str) -> List[str]:
    # example: Beijing, China BJS IATA
    i_comma = line.find(',')
    city = line[:i_comma]
    rest = line[i_comma:].split(' ')
    country = rest[1]
    code = rest[-2]

    return [country, city, code]


def parse_airport_line(line: str) -> List[str]:
    # example: Soekarno-Hatta International CGK IATA
    parts = line.split(' ')
    parts.pop()
    code = parts.pop()
    name = ' '.join(parts)
    return [name, code]


def is_metro_line(line: str) -> bool:
    return not line.find(',') == -1


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

    # with open(path) as file_in:
    #     lines = []
    #     for line in file_in:
    #         ans = parse_line(line)
    #         if ans:
    #             lines.append(ans)
    #     header = [['city', 'county', 'code']]
    #     x = list([[v['city'], v['country'], v['code']] for v in lines])
    #     header.extend(x)
    #     write_to_csv_from_lists(args.output_path, header)
    #     print('end')

    with open(path) as file_in:
        lines = []
        current_metro = None
        airports = []
        for line in file_in:
            if is_metro_line(line):
                if current_metro:
                    for a in airports:
                        row = list(current_metro)
                        row.append(a)
                        lines.append(row)
                current_metro = parse_metro_line(line)
                airports = []
            else:
                airport = parse_airport_line(line)
                airports.append(airport[-1])

        header = [['country', 'city', 'metropolitan_code', 'airport_code']]
        header.extend(lines)

    write_to_csv_from_lists(args.output_path, header)


if __name__ == '__main__':
    main()
