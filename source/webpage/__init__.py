"""网页模块，通过网页和用户交互"""
from public.utils import local_ip, load_module
from public.message import exit_msg
from public.log import web_logger
from public.config import data_path, get_config
from webpage.webClient import get_web_client
from django.core.management import execute_from_command_line
from threading import Thread
import os
import time
import platform
import subprocess


def run_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpage.mei.settings')
    execute_from_command_line([__file__, 'migrate'])
    execute_from_command_line([__file__, 'runserver', f'{local_ip()}:{1234}', '--noreload'])


def start_natapp():
    if platform.system() == 'Windows':
        return subprocess.Popen([
            'start',
            'natapp.exe',
            f'-authtoken={get_config("natapp", "authtoken")}',
            f'-log={data_path("web", "natapp.txt")}',  # 与robot/section/web_entrance.py内保持一致
            '-loglevel=INFO',
        ], shell=True)
    else:
        return subprocess.Popen([
            './natapp',
            f'-authtoken={get_config("natapp", "authtoken")}',
            f'-log={data_path("web", "natapp.txt")}',  # 与robot/section/web_entrance.py内保持一致
            '-loglevel=INFO',
        ])


def web_main():
    """web客户端的入口"""
    os.chdir(os.path.dirname(__file__))
    load_module('views')

    @exit_msg.on_receive
    def exit_web():
        nonlocal running
        web_logger.info('收到服务器的命令，即将退出程序')
        running = False

    running = True
    Thread(target=get_web_client().listen_server, daemon=True).start()
    Thread(target=run_django, daemon=True).start()
    natapp_process = start_natapp()

    while running:
        time.sleep(1)

    natapp_process.kill()
    web_logger.info('已退出程序')
