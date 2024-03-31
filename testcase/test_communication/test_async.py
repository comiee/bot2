from communication.asyncServer import AsyncServer
from communication.asyncClient import AsyncClient
from threading import Thread
import unittest
import asyncio
import time


class AsyncTestCase(unittest.IsolatedAsyncioTestCase):
    server = AsyncServer()

    @classmethod
    def setUpClass(cls):
        Thread(target=asyncio.run, args=[cls.server.run()]).start()

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.server.close())

    async def test_sync(self):
        @self.server.register('test')
        async def _(s):
            await asyncio.sleep(1)
            print(s)
            return s

        async def f(s):
            async with AsyncClient('test') as client:
                return await client.send(s)

        start = time.time()
        ret = await asyncio.gather(f('1'), f('2'), f('3'), f('4'))
        end = time.time()
        self.assertEqual(['1', '2', '3', '4'], ret)
        self.assertLess(end - start, 2)  # 服务端应该并行执行多个消息的处理，总时长应该在1~2秒
