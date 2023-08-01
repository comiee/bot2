"""主服务器模块，与交互解耦"""
from public.utils import load_module
from masterServer.masterServer import get_master_server
from masterServer.admin.CmdAdmin import CmdAdmin
from threading import Thread
import os


def server_main():
    """服务器模块的入口"""
    os.chdir(os.path.dirname(__file__))
    load_module('module')
    server = get_master_server()
    Thread(target=server.run, daemon=True).start()
    CmdAdmin(server).run()
