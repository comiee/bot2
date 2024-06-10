from communication.asyncServer import AsyncServer
from selenium.webdriver.common.by import By
from masterServer.comm.FirefoxBrowser import FirefoxBrowser
import asyncio


def ascii2d(url):
    with FirefoxBrowser() as browser:
        browser.get('https://www.ascii2d.net/search/url/' + url)
        items = browser.wait_elements(By.XPATH, '//*[@class="detail-box gray-link"]/h6/a[1]')
        return [x.get_attribute('href') for x in items]


@AsyncServer().register('identify_image')
async def identify_image(url):
    return await asyncio.to_thread(ascii2d, url)
