from communication.asyncServer import AsyncServer
from public.log import master_server_logger
from public.exception import CustomException
from public.config import get_config
from masterServer.comm.FirefoxBrowser import FirefoxBrowser
from selenium.webdriver.common.by import By
import asyncio
import aiohttp
from lxml import etree


async def ascii2d_aiohttp(url):
    async with aiohttp.ClientSession() as clientSession:
        async with clientSession.get('https://www.ascii2d.net/search/url/' + url) as resp:
            if resp.status != 200:
                raise CustomException(f'连接失败：{resp.status} {resp.reason}')
            html = etree.HTML(await resp.text(encoding='utf-8'))
            items = html.xpath('//*[@class="detail-box gray-link"]/h6/a[1]')
            return [x.get('href') for x in items]


async def saucenao(url):
    async with aiohttp.ClientSession() as clientSession:
        params = {
            'api_key': get_config('saucenao', 'api_key'),
            'db': 999,
            'output_type': 2,
            'numres': 3,
            'url': url,
        }
        async with clientSession.get('https://saucenao.com/search.php', params=params) as resp:
            res = await resp.json()
            return [x['data']['ext_urls'][0] for x in res['results']]


def ascii2d_selenium(url):
    with FirefoxBrowser() as browser:
        browser.get('https://www.ascii2d.net/search/url/' + url)
        items = browser.wait_elements(By.XPATH, '//*[@class="detail-box gray-link"]/h6/a[1]')
        return [x.get_attribute('href') for x in items]


@AsyncServer().register('identify_image')
async def identify_image(url):
    try:
        res = await ascii2d_aiohttp(url)
        assert res
        return res
    except Exception as e:
        master_server_logger.warning(f'使用ascii2d_aiohttp识图失败，将使用其他方案，原因：{e}')

    try:
        res = await saucenao(url)
        assert res
        return res
    except Exception as e:
        master_server_logger.warning(f'使用saucenao识图失败，将使用其他方案，原因：{e}')

    return await asyncio.to_thread(ascii2d_selenium, url)

# TODO 识字（OCR）
# TODO 识码（QR)
# TODO 识番（https://trace.moe）
# TODO 识本（danbooru）
