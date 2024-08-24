from masterServer.module.identify_image import ascii2d_aiohttp, ascii2d_selenium, identify_image
import unittest


class AirConditionerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_ascii2d_aiohttp(self):
        url = 'https://i.pximg.net/img-master/img/2024/04/10/08/35/31/117709975_p0_master1200.jpg'
        res = await ascii2d_aiohttp(url)
        print(res)
        self.assertIn('https://www.pixiv.net/artworks/117709975', res)

    async def test_identify_image(self):
        url = 'https://i.pximg.net/img-master/img/2024/04/10/08/35/31/117709975_p0_master1200.jpg'
        res = await identify_image(url)
        print(res)
        self.assertIn('https://www.pixiv.net/artworks/117709975', res)
