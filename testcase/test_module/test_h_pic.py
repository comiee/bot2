from communication.asyncServer import AsyncServer
from masterServer import server_main
from masterServer.admin.Admin import Admin
from robot.section.h_pic import get_h_pic
from multiprocessing import Process, Value
import unittest
import asyncio
import time

__import__('robot.section.h_pic')


def test_server_main(running_val):
    class TestAdmin(Admin):
        def run(self):
            while running_val.value:
                time.sleep(1)
            AsyncServer().wait_close()
            self.server.close()

    server_main(TestAdmin)


class HPicTestCase(unittest.IsolatedAsyncioTestCase):
    running_val = Value('b', True)
    server_process = Process(target=test_server_main, args=[running_val])

    @classmethod
    def setUpClass(cls):
        cls.server_process.start()

    @classmethod
    def tearDownClass(cls):
        cls.running_val.value = False

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
