"""主服务器模块，与交互解耦"""
from communication.server import Server
from threading import Thread

# 用于注册回调函数
import master_server.chat


def server_main():
    """服务器模块的入口"""
    server = Server()
    Thread(target=server.run).start()
