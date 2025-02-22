from comiee import overload, lazy
from public.config import data_path
from enum import IntEnum
import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import current_process

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

    a = file_name.split('.')
    name = f'{".".join(a[:-1])}_{current_process().name}.{a[-1]}'
    fh = RotatingFileHandler(str(data_path('log', name)),
                             encoding='utf-8', maxBytes=1024 * 1024, backupCount=5)
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


# 底层的client和server使用logger
client_logger: logging.Logger = lazy(get_logger, 'client', LogLevel.INFO, LogLevel.DEBUG)
server_logger: logging.Logger = lazy(get_logger, 'server', LogLevel.DEBUG)
async_client_logger: logging.Logger = lazy(get_logger, 'asyncClient', LogLevel.DEBUG)
async_server_logger: logging.Logger = lazy(get_logger, 'asyncServer', LogLevel.INFO, LogLevel.DEBUG)

# 公共部分使用的logger
public_logger: logging.Logger = lazy(get_logger, 'public', LogLevel.DEBUG)

# 服务器各组件使用的logger
master_server_logger: logging.Logger = lazy(get_logger, 'masterServer', LogLevel.INFO, LogLevel.DEBUG)
admin_logger: logging.Logger = lazy(get_logger, 'admin', LogLevel.DEBUG)

# bot客户端各组件使用的logger
bot_client_logger: logging.Logger = lazy(get_logger, 'botClient', LogLevel.DEBUG)
bot_logger: logging.Logger = lazy(get_logger, 'bot', LogLevel.DEBUG)

# web客户端各组件使用的logger
web_logger: logging.Logger = lazy(get_logger, 'webClient', LogLevel.DEBUG)
