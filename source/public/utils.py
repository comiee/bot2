from public.log import public_logger
import pkgutil
import netifaces
import os
from datetime import datetime


def load_module(path):
    """加载路径下的所有py文件，不包括__init__.py和子包"""
    dirs = [path]
    pkgutil.extend_path(dirs, path)
    for loader, module_name, is_pkg in pkgutil.iter_modules(dirs):
        if not is_pkg:
            public_logger.info(f'正在从{loader.path}加载{module_name}')  # 这个阶段在启动前，报错直接打印，不用记到日志文件里
            loader.find_module(module_name).load_module()


def local_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface == 'lo':
            continue
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ip = addresses[netifaces.AF_INET][0]['addr']
            return ip
    return '127.0.0.1'


def is_file_today(path):
    if not os.path.exists(path):
        return False
    if datetime.fromtimestamp(os.path.getmtime(path)).date() != datetime.now().date():
        return False
    return True
