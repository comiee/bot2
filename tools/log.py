from comiee import overload
import os
import logging
from enum import IntEnum

LOG_PATH = os.path.join(os.getcwd(), 'data/log/')


class LogLevel(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


@overload
def get_logger(name, level) -> logging.Logger:
    return get_logger(name, level, name + '.txt', level)


@overload
def get_logger(name, level, file_level) -> logging.Logger:
    return get_logger(name, level, name + '.txt', file_level)


@overload
def get_logger(name, level, file_name, file_level) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LogLevel.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    fh = logging.FileHandler(os.path.join(LOG_PATH, file_name), encoding='utf-8')
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
