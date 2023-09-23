import os

DATA_PATH = os.path.join(os.getcwd(), 'data')


def data_path(*paths):
    p = DATA_PATH
    for path in paths:
        if not os.path.exists(p):
            os.makedirs(p)
        p = os.path.join(p, path)
    return p
