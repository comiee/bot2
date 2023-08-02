import os

DATA_PATH = os.path.join(os.getcwd(), 'data')


def data_path(path):
    return os.path.join(DATA_PATH, path)
