from robot.plugins.commandPlugin import CommandPlugin
from robot.plugins.chatPlugin import ChatPlugin
from faker.master_server_faker import ServerController
from faker.bot_faker import spread_event, dummy_friend_message_event, dummy_group_message_event
from alicebot.adapter.mirai.message import MiraiMessageSegment
import unittest

__import__('robot.section.ai_chat')


class HPicTestCase(unittest.IsolatedAsyncioTestCase):
    server_controller = ServerController()

    @classmethod
    def setUpClass(cls):
        cls.server_controller.start()

    @classmethod
    def tearDownClass(cls):
        cls.server_controller.close()

    async def test_ai_chat_by_command(self):
        event = dummy_friend_message_event('ai 你叫什么名字？')
        await spread_event(CommandPlugin, event)
        self.assertIn('小魅', event.get_reply())

        event = dummy_friend_message_event('AI 苹果用英语怎么说')
        await spread_event(CommandPlugin, event)
        self.assertIn('apple', event.get_reply().lower())

    async def test_ai_chat_by_friend_chat(self):
        event = dummy_friend_message_event('你的生日是哪天')
        await spread_event(ChatPlugin, event)
        self.assertIn('2019年11月21日', event.get_reply().lower())

    async def test_ai_chat_by_group_at(self):
        event = dummy_group_message_event(MiraiMessageSegment.at(1790218632) + '你的生日是哪天')
        await spread_event(ChatPlugin, event)
        self.assertIn('2019年11月21日', event.get_reply().lower())


if __name__ == '__main__':
    unittest.main()