from public.log import public_logger
from public.convert import convert_to
import pkgutil
import netifaces
import os
from datetime import datetime
import aiohttp
from PIL import Image
from io import BytesIO


def load_module(path):
    """加载路径下的所有py文件，不包括__init__.py和子包"""
    dirs = [path]
    pkgutil.extend_path(dirs, path)
    flag = True
    for loader, module_name, is_pkg in pkgutil.iter_modules(dirs):
        if not is_pkg:
            public_logger.info(f'正在从{loader.path}加载{module_name}')
            loader.find_module(module_name).load_module()
            flag = False
    if flag:
        public_logger.error(f'从{path}中什么也没有找到')


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


async def fetch_image(url):
    async with aiohttp.ClientSession() as aio_session:
        async with aio_session.get(url) as resp:
            if resp.status != 200:
                raise ConnectionError(f'连接{url}失败，错误码：{resp.status}')
            return await resp.read()


async def save_image(url, path):
    data = await fetch_image(url)
    with open(path, 'wb') as f:
        f.write(data)


async def open_image(url):
    return Image.open(BytesIO(await fetch_image(url)))


def get_pic_url_from_internal(pic_internal: str):
    pic_data = convert_to('data', pic_internal)
    assert len(pic_data) >= 1
    pic_dict = pic_data[0]
    assert 'imageId' in pic_dict and 'url' in pic_dict
    return pic_dict['url']
