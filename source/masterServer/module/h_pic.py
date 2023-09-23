from public.message import h_pic_msg
from public.log import master_server_logger
from public.config import data_path
from threading import Thread
from PIL import Image
from io import BytesIO
import re
import requests
import json


def img_save(url):  # 从url保存图片
    resp = requests.get(url)
    img = Image.open(BytesIO(resp.content))
    name = re.search(r'^.*/(.*?)$', url).group(1)
    img.save(data_path('pic', name))


@h_pic_msg.on_receive
def h_pic(post_json):
    ret = requests.post('https://api.lolicon.app/setu/v2', json=post_json)
    if ret.status_code != 200:
        master_server_logger.warning(f'h_pic 请求失败：{ret.status_code}')
        return f'error: {ret.status_code}', []
    try:
        ret_json = json.loads(ret.text)
    except Exception as e:
        master_server_logger.warning(f'h_pic 解析爬取结果失败：{e}')
        return '解析爬取结果失败', []
    if 'error' not in ret_json or 'data' not in ret_json or \
            any('urls' not in x or 'original' not in x['urls'] for x in ret_json['data']):
        master_server_logger.warning(f'h_pic 爬取结果格式错误：{ret_json}')
        return '爬取结果格式错误', []
    if err := ret_json.get('error', ''):
        master_server_logger.warning(f'h_pic 返回错误：{ret_json}')
        return err, []
    master_server_logger.info(f'h_pic 收到请求：{post_json}，爬取结果：{ret_json}')
    res = []
    for x in ret_json.get('data', []):
        url = x.get('urls', {}).get('original', '')
        res.append(url)
        Thread(target=img_save, args=(url,)).start()
    return err, res
