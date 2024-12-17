import argparse
import os

from csv_generator import CsvGenerator
from file_handler import IncomingReestr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an XML file.")
    parser.add_argument("-f", type=str)
    args = parser.parse_args()
    if args.f:
        if os.path.isfile(args.f) and args.f.endswith(".xml"):
            file = IncomingReestr(args.f)
            csv = CsvGenerator(file)
            csv.generate_csv()

    else:
        print(os.path.dirname(__file__))
