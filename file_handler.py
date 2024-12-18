from datetime import datetime
import os
import re
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import logging


class File:

    def __init__(self, file: str):
        self.file: str = file
        self.filename: str = os.path.basename(self.file)
        self.directory: str = os.path.dirname(self.file)
        self.encoding: Optional[str] = self.get_encoding(self.file) or 'UTF-8'

    def get_encoding(self, file: str) -> Optional[str]:
        # пытается определить кодировку файла с помощью регулярного выражения
        try:
            with open(file, "rb") as file:
                text = file.readline()
                # ищет первое вхождение после encoding между ковычек
                match = re.search(br'encoding=["\'](.*?)["\']', text)
                return match.group(1).decode("ascii") if match else None
        except Exception:
            logging.error(
                f"Ошибка при получении кодировки файла {self.filename}")
            return None

    def read_file(self) -> ET.Element:
        try:
            with open(self.file, "rb") as file:
                tree = ET.parse(file)
                return tree.getroot()
        except ET.ParseError as e:
            logging.error(f"Ошибка обработки файла {self.filename}: {e}")
        except Exception as e:
            logging.error(
                f"Произошла ошибка при чтении файла {self.filename}: {e}")


class IncomingReestr(File):
    def __init__(self, file: str):
        super().__init__(file)
        self.root: ET.Element = self.read_file()
        self.date: str = self._set_date()
        self.payers: List[Payer] = []
        self.fill_data()

    def _set_date(self) -> str:
        # вытаскивает дату из файла по ключу ДатаФайл, где бы он не находился
        try:
            date = self.root.find(".//ДатаФайл").text
            datetime.strptime(date, "%d.%m.%Y")
            return date
        except ValueError:
            logging.error(f"Неверный формат даты: {date}")
            raise ValueError("Invalid date format")

    def _find_payer_parametr(self, payer: ET.Element, key: str) -> str:
        # ищет тег по ключу. если находит, то возвращает его, а если нет, то пустую строку
        return payer.find(key).text if payer.find(key) is not None else ''

    def set_payers(self):
        self.payers = []
        try:
            for index, payer in enumerate(self.root.findall("ИнфЧаст/Плательщик")):
                bank_book = self._find_payer_parametr(payer, "ЛицСч")
                full_name = self._find_payer_parametr(payer, "ФИО")
                address = self._find_payer_parametr(payer, "Адрес")
                period = self._find_payer_parametr(payer, "Период")
                summa = self._find_payer_parametr(payer, "Сумма")

                payer = Payer(bank_book, full_name, address, period, summa)
                # проверяет на отсутствие ключевые элементы
                if not all([payer.bank_book, payer.period]) or payer.summa is None:
                    logging.error(
                        f"Строка номер {index} не имеет одного или более ключевых реквизитов")
                    continue
                self.payers.append(payer)
        except ValueError as e:
            logging.error(
                f"Не удалось создать объект плательщика: {e} (данные: {bank_book}, {full_name}, {address}, {period}, {summa})")

    def count_repeat(self) -> Dict[str, int]:
        counter = {}
        for payer in self.payers:
            key = payer.get_key()
            counter[key] = counter.get(key, 0) + 1
        return counter

    def filter_payers(self, counter: Dict[str, int]) -> None:
        self.payers = [
            payer for payer in self.payers if counter[payer.get_key()] == 1]

    def log_removed_payers(self, counter: Dict[str, int]) -> None:
        duplicates = set([payer.get_key()
                         for payer in self.payers if counter[payer.get_key()] > 1])
        if duplicates:
            logging.info(f"Дублирующиеся данные: {duplicates}")

    def fill_data(self) -> None:
        self.set_payers()
        counter = self.count_repeat()
        self.filter_payers(counter)
        self.log_removed_payers(counter)


class Payer:
    def __init__(self, bank_book, full_name, address, period, summa):
        self.bank_book = bank_book
        self.full_name = full_name
        self.address = address
        self.period = self.validate_period(period)
        self.summa = self.validate_summa(summa)

    def validate_period(self, period):
        try:
            datetime.strptime(period, "%m%Y")
            return period
        except ValueError:
            logging.error(
                f"Неверный формат периода: {period} у пользователя {self.full_name}")
            raise

    def validate_summa(self, summa):
        # функция сначала проверяет не пустое ли значение было передано
        # если значение пустое, то вернет пустую строку, что нужно будет для определения пропуска строки или просто записи пустого значения
        # если значение не пустое, то пытается преобразовать его в число
        # если преобразование завершается успешно, то возвращает число с двумя знаками после запятой
        # если преобразование не удалось, то выводится сообщение об ошибке и возвращается пустая строка
        # таким образом мы обрабаатываем случай, когда сумма не указана или указана неправильно
        try:
            if summa:
                summa = float(summa)
                if summa <= 0:
                    logging.error(
                        f"Сумма должна быть положительной: {summa} у пользователя {self.full_name}")
                    return None
                return f"{summa:.2f}"
            return ''
        except ValueError:
            logging.error(
                f"Неверный формат суммы: {summa} у пользователя {self.full_name}")
            return None

    def get_key(self):
        return self.bank_book, self.period
