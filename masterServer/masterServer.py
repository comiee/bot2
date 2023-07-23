from communication.server import Server
from tools.log import get_logger, LogLevel

__all__ = ['get_master_server']


class MasterServer(Server):
    logger = get_logger('masterServer', LogLevel.INFO, LogLevel.DEBUG)


master_server = None  # 不能在这里实例化对象，不然导入这个包就会实例化


def get_master_server() -> MasterServer:
    global master_server
    if master_server is None:
        master_server = MasterServer()
    return master_server
