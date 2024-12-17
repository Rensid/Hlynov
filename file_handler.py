from datetime import datetime
import os
import re
import xml.etree.ElementTree as ET

from exceptions import InvalidFileFormatException


class File:
    def __init__(self, file):
        self.file = file
        self.filename = os.path.basename(self.file)
        self.directory = os.path.dirname(self.file)
        self.encoding = self.get_encoding(self.file)
        print(self.directory)

    def get_encoding(self, file):
        with open(file, 'rb') as file:
            text = file.readline()
            match = re.search(
                br'encoding=["\'](.*?)["\']', text)
            if match:
                return match.group(1).decode('ascii')

    def read_file(self):
        with open(self.file, "rb") as file:
            try:
                tree = ET.parse(file)
                root = tree.getroot()
                return root
            except InvalidFileFormatException as e:
                print(f"Failed to parse XML: {e}")


class IncomingReestr(File):

    def __init__(self, file):
        super().__init__(file)
        self.root = super().read_file()
        self.date = None
        self.payers: list[Payer] = []
        self.set_payers()
        self.filter_payers()
        self.set_date()

    def set_date(self):
        try:
            date = self.root.find('.//ДатаФайл').text
            datetime.strptime(date, "%d.%m.%Y")
            self.date = date
        except Exception as e:
            print(f"Invalid date format: {e}")

    def set_payers(self):
        for payer in self.root.findall('ИнфЧаст/Плательщик'):
            try:
                bank_book = payer.find('ЛицСч').text if payer.find(
                    'ЛицСч') is not None else ''
                full_name = payer.find('ФИО').text if payer.find(
                    'ФИО') is not None else ''
                address = payer.find('Адрес').text if payer.find(
                    'Адрес') is not None else ''
                period = payer.find('Период').text if payer.find(
                    'Период') is not None else ''
                summa = payer.find('Сумма').text if payer.find(
                    'Сумма') is not None else ''
                self.payers.append(
                    Payer(bank_book, full_name, address, period, summa))
            except Exception as e:
                print(f"Invalid payer data: {e}")

    def filter_payers(self):
        counter = dict()
        for payer in self.payers:
            key = payer.get_key()
            counter.setdefault(key, 0)
            counter[key] += 1
        self.payers = [
            payer for payer in self.payers if counter[payer.get_key()] == 1]


class Payer():
    def __init__(self, bank_book, full_name, address, period, summa):
        self.bank_book: str | None = bank_book
        self.full_name: str | None = full_name
        self.address: str | None = address
        self.period: str | None = None
        self.summa: str | None = summa
        self.validate_period(period)

    def validate_period(self, period):

        try:
            datetime.strptime(period, '%m%Y')
            self.period = period
        except Exception as e:
            print("Invalid period")

    def get_key(self):
        return (self.bank_book, self.period)
