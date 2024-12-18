import logging
import os


class LogConfig:
    def __init__(self, path):
        self.log_file = self.create_dir_for_logs(path)
        self.configure_logging(self.log_file)

    def create_dir_for_logs(self, path):
        base_dir = os.path.dirname(path)
        print(base_dir)
        log_dir = os.path.join(base_dir, "log")
        print(log_dir)
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "logs.log")

    def configure_logging(self, log_file):
        logging.basicConfig(
            level=logging.INFO,
            filename=log_file,
            format="%(levelname)-7s (%(asctime)s): %(message)s",
            datefmt="%d/%m/%Y %I:%M:%S",
            encoding="utf-8",
            filemode="a",
        )
