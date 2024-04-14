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
        cls.server.wait_close()

    async def test_register_arg1(self):
        cmd = 'test_register_arg1'
        a = []

        @self.server.register(cmd)
        async def _(s):
            a.append(s)
            return s

        async with AsyncClient(cmd) as client:
            self.assertEqual(await client.send('1'), '1')
        self.assertEqual(['1'], a)

    async def test_register_arg2(self):
        cmd = 'test_register_arg2'
        a = []

        @self.server.register(cmd)
        async def _(send, recv):
            s = await recv()
            a.append(s)
            await send(s)
            s = await recv()
            a.append(s)
            await send(s)

        async with AsyncClient(cmd) as client:
            self.assertEqual(await client.send('1'), '1')
            self.assertEqual(await client.send('2'), '2')

        self.assertEqual(['1', '2'], a)

    async def test_sync(self):
        cmd = 'test_sync'

        @self.server.register(cmd)
        async def _(s):
            await asyncio.sleep(1)
            print(s)
            return s

        async def f(s):
            async with AsyncClient(cmd) as client:
                return await client.send(s)

        start = time.time()
        ret = await asyncio.gather(f('1'), f('2'), f('3'), f('4'))
        end = time.time()
        self.assertEqual(['1', '2', '3', '4'], ret)
        self.assertLess(end - start, 2)  # 服务端应该并行执行多个消息的处理，总时长应该在1~2秒

    async def test_server_task_list(self):
        cmd = 'test_server_task_list'
        a = []
        task: asyncio.Task | None = None

        async def f():
            await asyncio.sleep(1)
            a.append(2)

        @self.server.register(cmd)
        async def _(s):
            nonlocal task
            task = self.server.add_task(f())
            a.append(1)
            return s

        async with AsyncClient(cmd) as client:
            await client.send("")
        while not task.done():
            pass

        self.assertEqual([1, 2], a)

    async def test_client_task_list(self):
        cmd = 'test_client_task_list'
        a = []

        async def f():
            await asyncio.sleep(1)
            a.append(2)

        # noinspection PyUnusedLocal
        @AsyncServer().register(cmd)
        async def _(send, recv):
            pass

        async with AsyncClient(cmd) as client:
            client.add_task(f())
            a.append(1)

        self.assertEqual([1, 2], a)


if __name__ == '__main__':
    unittest.main()
