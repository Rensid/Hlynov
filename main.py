import argparse
import os
import shutil
import logging
from typing import Literal

from csv_generator import CsvGenerator
from file_handler import IncomingReestr
from log import LogConfig


def move_to(file: str, subdir: str) -> None:
    match subdir:
        case 'arh':
            base_dir = os.path.dirname(file)
            arh_dir = os.path.join(base_dir, subdir)
            os.makedirs(arh_dir, exist_ok=True)
            shutil.move(file, os.path.join(arh_dir, os.path.basename(file)))

        case 'bad':
            base_dir = os.path.dirname(os.path.abspath(__file__))
            bad_dir = os.path.join(base_dir, subdir)
            os.makedirs(bad_dir, exist_ok=True)
            shutil.move(file, os.path.join(bad_dir, os.path.basename(file)))
        case _:
            raise ValueError("new_path должен быть 'arh' или 'bad'")


def process_file(file: str):
    reestr = IncomingReestr(file)
    csv = CsvGenerator(reestr)
    csv.generate_csv()
    move_to(file, "arh")


def main():
    parser = argparse.ArgumentParser(description="Process an XML file.")
    parser.add_argument("-f", type=str)
    args = parser.parse_args()
    if args.f:
        LogConfig(args.f)
        if os.path.isfile(args.f):
            if args.f.endswith(".xml"):
                process_file(args.f)
            else:
                logging.error(f"Неподходящий файл {os.path.basename(args.f)}")
                move_to(args.f, "bad")
        elif os.path.isdir(args.f):
            for file in os.listdir(args.f):
                file = os.path.join(args.f, file)
                if os.path.isfile(file):
                    if file.endswith(".xml"):
                        try:
                            process_file(file)
                        except Exception as e:
                            logging.error(
                                f"Ошибка при обработке файла {file}: {e}")
                            move_to(file, "bad")
                    else:
                        logging.error(f"Неподходящий файл {file}")
                        move_to(file, "bad")
                else:
                    continue
    else:
        print("Не указан путь к файлу. Укажите путь через параметр -f")


if __name__ == "__main__":
    main()
