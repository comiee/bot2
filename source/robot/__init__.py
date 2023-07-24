"""机器人模块，通过qq和用户交互"""
from tools.utils import load_module
from robot.botClient import get_bot_client
from robot.main import run_bot
from alicebot import Bot
from threading import Thread
import os
import asyncio


def bot_main():
    """bot客户端的入口"""
    os.chdir(os.path.dirname(__file__))
    load_module('module')
    bot = Bot()
    bot_client = get_bot_client()

    @bot.bot_run_hook
    async def run_hook(_):
        bot_client.init_bot_proxy(bot, asyncio.get_running_loop())
        Thread(target=get_bot_client().listen_server, daemon=True).start()

    run_bot(bot)
