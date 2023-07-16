"""主服务器模块，与交互解耦"""
from masterServer.masterServer import get_master_server
from masterServer.admin.CmdAdmin import CmdAdmin
from threading import Thread
import os

# 用于注册回调函数
import masterServer.chat


def server_main():
    """服务器模块的入口"""
    os.chdir(os.path.dirname(__file__))
    server = get_master_server()
    Thread(target=server.run).start()
    CmdAdmin(server).run()
