from communication.client import Client
from tools.log import get_logger, LogLevel

__all__ = ['get_bot_client']


class BotClient(Client):
    logger = get_logger('botClient', LogLevel.DEBUG)

    def __init__(self):
        super().__init__('bot')


bot_client = BotClient()


def get_bot_client():
    return bot_client
