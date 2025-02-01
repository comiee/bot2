from robot.plugins.commandPlugin import CommandPlugin
from faker.master_server_faker import ServerController
from faker.bot_faker import spread_event, dummy_friend_message_event
from webpage import web_main
from multiprocessing import Process
import unittest
import asyncio

__import__('robot.section.web_entrance')


class WebEntranceTestCase(unittest.IsolatedAsyncioTestCase):
    server_controller = ServerController()

    @classmethod
    def setUpClass(cls):
        cls.server_controller.start()

    @classmethod
    def tearDownClass(cls):
        cls.server_controller.close()

    async def test_get_url(self):
        Process(target=web_main).start()
        await asyncio.sleep(3)
        event = dummy_friend_message_event('网页版')
        await spread_event(CommandPlugin, event)
        print(event.get_reply())
        self.assertTrue(event.get_reply())
        self.assertNotEquals('未找到网址，natapp可能未启动', event.get_reply())


if __name__ == '__main__':
    unittest.main()
