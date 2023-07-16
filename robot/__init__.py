"""机器人模块，通过qq和用户交互"""

from robot.botClient import get_bot_client
from robot.main import run_bot
from threading import Thread
import os


def bot_main():
    """bot客户端的入口"""
    os.chdir(os.path.dirname(__file__))
    bot_client = get_bot_client()
    Thread(target=bot_client.listen_server).start()
    run_bot()
