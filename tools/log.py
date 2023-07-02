from comiee import overload
import os
import logging

LOG_PATH = os.path.join(os.getcwd(), 'data/log/')


class LogLevel:
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


@overload
def get_logger(name, level):
    return get_logger(name, level, name + '.txt', level)


@overload
def get_logger(name, level, file_name, file_level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    fh = logging.FileHandler(os.path.join(LOG_PATH, file_name))
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
