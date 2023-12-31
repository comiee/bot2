from functools import reduce
import operator as op
import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

DATA_PATH = os.path.join(os.getcwd(), 'data')


def data_path(*paths):
    p = DATA_PATH
    for path in paths:
        if not os.path.exists(p):
            os.makedirs(p)
        p = os.path.join(p, path)
    return p


def get_config(*keys):
    with open(data_path('config.toml'), 'rb') as f:
        config = tomllib.load(f)

    return reduce(op.getitem, keys, config)
