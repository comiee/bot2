import logging


class LogLevel:
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


def get_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch=logging.StreamHandler()
    ch.setLevel(level)
    formatter=logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
