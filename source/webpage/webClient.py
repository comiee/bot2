from communication.client import Client

__all__ = ['get_web_client']


class WebClient(Client):
    def __init__(self):
        super().__init__('web')


_web_client = None


def get_web_client() -> WebClient:
    global _web_client
    if _web_client is None:
        _web_client = WebClient()
    return _web_client
