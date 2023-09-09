from comiee import overload
from public.config import data_path
from enum import IntEnum
import os
import logging

LOG_PATH = data_path('log')


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


# 底层的client和server使用logger
client_logger: logging.Logger = get_logger('client', LogLevel.INFO, LogLevel.DEBUG)
server_logger: logging.Logger = get_logger('server', LogLevel.DEBUG)

# 各组件使用的logger
master_server_logger: logging.Logger = get_logger('masterServer', LogLevel.INFO, LogLevel.DEBUG)
admin_logger: logging.Logger = get_logger('admin', LogLevel.DEBUG)

bot_client_logger: logging.Logger = get_logger('botClient', LogLevel.DEBUG)
bot_logger: logging.Logger = get_logger('bot', LogLevel.DEBUG)

# 外层启动器使用的logger
main_logger: logging.Logger = get_logger('main', LogLevel.DEBUG)
