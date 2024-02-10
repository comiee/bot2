"""网页模块，通过网页和用户交互"""
from django.core.management import execute_from_command_line
import os

def web_main():
    """web客户端的入口"""
    os.chdir(os.path.dirname(__file__))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpage.mei.settings')
    execute_from_command_line([__file__, 'migrate'])
    execute_from_command_line([__file__, 'runserver', '192.168.1.105:1234'])