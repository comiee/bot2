from communication.server import Server

__all__ = ['get_master_server']


class MasterServer(Server):
    pass


_master_server = None  # 不能在这里实例化对象，不然导入这个包就会实例化


def get_master_server() -> MasterServer:
    global _master_server
    if _master_server is None:
        _master_server = MasterServer()
    return _master_server
