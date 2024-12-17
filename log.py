import logging
from functools import wraps


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        filename="my_logging.log",
        format="%(levelname)-7s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
        datefmt="%d/%m/%Y %I:%M:%S",
        encoding="utf-8",
        filemode="w",
    )


configure_logging()
