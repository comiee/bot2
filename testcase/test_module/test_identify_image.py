from robot.plugins.commandPlugin import CommandPlugin
from faker.master_server_faker import ServerController
from faker.bot_faker import spread_event, dummy_friend_message_event
from alicebot.adapter.mirai.message import MiraiMessageSegment
import unittest

__import__('robot.section.identify_image')


class IdentifyImageTestCase(unittest.IsolatedAsyncioTestCase):
    server_controller = ServerController()

    @classmethod
    def setUpClass(cls):
        cls.server_controller.start()

    @classmethod
    def tearDownClass(cls):
        cls.server_controller.close()

    async def test_identify_image(self):
        url = 'https://i.pximg.net/img-master/img/2024/04/10/08/35/31/117709975_p0_master1200.jpg'
        message = MiraiMessageSegment.plain('识图 ') + MiraiMessageSegment.image(url=url)
        event = dummy_friend_message_event(message)
        await spread_event(CommandPlugin, event)
        self.assertEqual(1, event.reply.call_count)
        text = event.get_reply()
        print(text)
        self.assertIn('https://www.pixiv.net/artworks/117709975', text)
