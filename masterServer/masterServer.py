from communication.server import Server
from tools.log import get_logger, LogLevel

__all__ = ['get_master_server']


class MasterServer(Server):
    logger = get_logger('masterServer', LogLevel.INFO, LogLevel.DEBUG)


master_server = MasterServer()


def get_master_server():
    return master_server
