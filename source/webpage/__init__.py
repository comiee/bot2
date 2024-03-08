"""网页模块，通过网页和用户交互"""
from public.utils import local_ip
from public.message import exit_msg
from public.log import web_logger
from webpage.webClient import get_web_client
from django.core.management import execute_from_command_line
from threading import Thread
import os
import time


def web_main():
    """web客户端的入口"""

    def run_django():
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpage.mei.settings')
        execute_from_command_line([__file__, 'migrate'])
        execute_from_command_line([__file__, 'runserver', f'{local_ip()}:{1234}', '--noreload'])

    @exit_msg.on_receive
    def exit_django():
        nonlocal running
        web_logger.info('收到服务器的命令，即将退出程序')
        running = False

    running = True
    Thread(target=run_django, daemon=True).start()
    Thread(target=get_web_client().listen_server, daemon=True).start()

    while running:
        time.sleep(1)
