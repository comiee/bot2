from communication.asyncServer import AsyncServer
from public.log import master_server_logger
from public.config import data_path
from public.utils import save_image
from public.exception import CustomException
import re
import aiohttp


async def save_pic(url):
    name = re.search(r'^.*/(.*?)$', url).group(1)
    try:
        await save_image(url, data_path('pic', name))
    except Exception as e:
        master_server_logger.warning(f'h_pic 保存图片失败：{e.args[0]}')
    else:
        master_server_logger.info(f'h_pic 图片已保存为 {name}')


@AsyncServer().register('h_pic')
async def h_pic(post_json):
    try:
        async with aiohttp.ClientSession() as aio_session:
            async with aio_session.post('https://api.lolicon.app/setu/v2', json=post_json) as resp:
                if resp.status != 200:
                    master_server_logger.warning(f'h_pic 请求失败：{resp.status}')
                    raise CustomException(f'error: {resp.status}')
                try:
                    ret_json = await resp.json()
                except Exception as e:
                    master_server_logger.warning(f'h_pic 解析爬取结果失败：{e}')
                    raise CustomException('解析爬取结果失败')
        if 'error' not in ret_json or 'data' not in ret_json or \
                any('urls' not in x or 'original' not in x['urls'] for x in ret_json['data']):
            master_server_logger.warning(f'h_pic 爬取结果格式错误：{ret_json}')
            raise CustomException('爬取结果格式错误')
        if err := ret_json.get('error', ''):
            master_server_logger.warning(f'h_pic 返回错误：{ret_json}')
            raise CustomException(err)
        master_server_logger.info(f'h_pic 收到请求：{post_json}，爬取结果：{ret_json}')
        data = []
        for x in ret_json.get('data', []):
            url = x.get('urls', {}).get('original', '')
            data.append(url)
            AsyncServer().add_task(save_pic(url))
        res = {'data': data}
    except CustomException as e:
        res = {'error': e.args[0]}
    return res
