from robot.section.h_pic import get_h_pic
from faker.master_server_faker import AsyncServerController
import unittest
import asyncio
import time

__import__('robot.section.h_pic')


class HPicTestCase(unittest.IsolatedAsyncioTestCase):
    server_controller = AsyncServerController()

    @classmethod
    def setUpClass(cls):
        cls.server_controller.start()

    @classmethod
    def tearDownClass(cls):
        cls.server_controller.close()

    async def test_h_pic(self):
        res = await get_h_pic(2, 2)
        self.assertEqual(False, 'error' in res)
        urls = res['data']
        self.assertEqual(2, len(urls))

    async def test_mul(self):
        async def f():
            res = await get_h_pic(2, 1)
            self.assertEqual(False, 'error' in res)
            urls = res['data']
            self.assertEqual(1, len(urls))
            return time.time()

        arr = await asyncio.gather(f(), f(), f(), f())
        print(arr)
        self.assertLess(max(arr) - min(arr), 2)  # 服务器应该同步处理多人请求，返回结果的时间应该是接近的


if __name__ == '__main__':
    unittest.main()
