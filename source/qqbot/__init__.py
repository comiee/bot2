"""qq官方机器人模块"""
from public.utils import load_module
from qqbot.main import run_qqbot
import os


def qqbot_main():
    os.chdir((os.path.dirname(__file__)))
    load_module('command')

    run_qqbot()