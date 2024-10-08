"""主服务器模块，与交互解耦"""
from public.utils import load_module
from communication.asyncServer import AsyncServer
from masterServer.admin import Admin
from masterServer.masterServer import get_master_server
from threading import Thread
import asyncio
import os


def server_main(admin_: Admin):
    """服务器模块的入口"""
    os.chdir(os.path.dirname(__file__))
    load_module('module')
    server = get_master_server()
    Thread(target=server.run, daemon=True).start()
    Thread(target=asyncio.run, args=[AsyncServer().run()], daemon=True).start()
    admin_(server).run()
