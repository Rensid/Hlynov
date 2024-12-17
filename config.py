import os


class Config:

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.__name__)

    def get_base_dir(self):
        return self.BASE_DIR
