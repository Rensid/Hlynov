

import csv

from file_handler import IncomingReestr


class CsvGenerator:
    def __init__(self, incoming_reestr: IncomingReestr):
        self.incoming_reestr = incoming_reestr
        self.list_of_data = []
        self.create_list_of_data()
        self.csv_path = self.incoming_reestr.file.replace('.xml', '.csv')

    def create_list_of_data(self):
        for payer in self.incoming_reestr.payers:
            self.list_of_data.append([self.incoming_reestr.filename,
                                      self.incoming_reestr.date,
                                      payer.bank_book, payer.full_name,
                                      payer.address, payer.period,
                                      payer.summa])

    def generate_csv(self):
        with open(self.csv_path, 'w', newline='', encoding=self.incoming_reestr.encoding) as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(self.list_of_data)
