from communication.asyncServer import AsyncServer
from selenium.webdriver.common.by import By
from masterServer.comm.FirefoxBrowser import FirefoxBrowser
from queue import Queue
import asyncio

_in_queue=Queue()
_out_queue=Queue()

def ascii2d():
    with FirefoxBrowser() as browser:
        for url in _in_queue.get_nowait():
            browser.get('https://www.ascii2d.net/search/url/' + url)
            items = browser.wait_elements(By.XPATH, '//*[@class="detail-box gray-link"]/h6/a[1]')
            _out_queue.put_nowait([x.get_attribute('href') for x in items])


@AsyncServer().register('identify_image')
async def identify_image(url):
    async with asyncio.Lock():
        return await asyncio.to_thread(ascii2d, url)
