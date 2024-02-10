"""网页模块，通过网页和用户交互"""
from public.utils import local_ip
from django.core.management import execute_from_command_line
import os


def web_main():
    """web客户端的入口"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpage.mei.settings')
    execute_from_command_line([__file__, 'migrate'])
    execute_from_command_line([__file__, 'runserver', f'{local_ip()}:{1234}', '--noreload'])
