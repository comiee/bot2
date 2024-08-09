from communication.client import Client

__all__ = ['get_qq_bot_client']


class QQBotClient(Client):
    def __init__(self):
        super().__init__('qqbot')


_qq_bot_client = None  # 不能在这里实例化对象，不然导入这个包就会实例化


def get_qq_bot_client() -> QQBotClient:
    global _qq_bot_client
    if _qq_bot_client is None:
        _qq_bot_client = QQBotClient()
    return _qq_bot_client
