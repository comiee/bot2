from communication.asyncServer import AsyncServer
from public.config import data_path
from masterServer import server_main
from masterServer.admin.Admin import Admin
from robot.section.h_pic import get_h_pic
from multiprocessing import Process, Value, Queue
import unittest
import asyncio
import time
import re
import os

__import__('robot.section.h_pic')


def wait_download_pic(url):
    name = re.search(r'^.*/(.*?)$', url).group(1)
    size_old = size_new = 0
    while size_new == 0 or size_old != size_new:
        size_old, size_new = size_new, os.stat(data_path('pic', name)).st_size
        time.sleep(1)
    print('downloaded', name)


def test_server_main(running_val, download_pic_queue):
    class TestAdmin(Admin):
        def run(self):
            while running_val.value:
                time.sleep(1)
            for _ in range(download_pic_queue.qsize()):
                url = download_pic_queue.get()
                wait_download_pic(url)
            asyncio.run(AsyncServer().close())
            self.server.close()

    server_main(TestAdmin)


class HPicTestCase(unittest.IsolatedAsyncioTestCase):
    running_val = Value('b', True)
    download_pic_queue = Queue()
    server_process = Process(target=test_server_main, args=[running_val, download_pic_queue])

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
        self.assertNotEqual(0, len(urls))
        for url in urls:
            self.download_pic_queue.put(url)


if __name__ == '__main__':
    unittest.main()
