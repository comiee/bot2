from public.log import master_server_logger, LogLevel
from robot.plugins.commandPlugin import CommandPlugin
from robot.plugins.chatPlugin import ChatPlugin
from faker.master_server_faker import ServerController
from faker.bot_faker import spread_event, dummy_friend_message_event, dummy_group_message_event
from alicebot.adapter.mirai.message import MiraiMessageSegment
import unittest

__import__('robot.section.ai_chat')

master_server_logger.setLevel(LogLevel.DEBUG)


class AITestCase(unittest.IsolatedAsyncioTestCase):
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

        event = dummy_friend_message_event('AI “苹果”用英语怎么说')
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

    async def test_ai_cat(self):
        event = dummy_friend_message_event('猫娘，你好')
        await spread_event(CommandPlugin, event)
        self.assertIn('喵', event.get_reply())

    async def test_ai_deepseek(self):
        event = dummy_friend_message_event('deepseek 苹果的英语是什么？其中有几个p？')
        await spread_event(CommandPlugin, event)
        self.assertIn('<think>', event.get_reply())
        self.assertIn('</think>', event.get_reply())

    async def test_brackets_text(self):
        event = dummy_group_message_event(
            MiraiMessageSegment.at(1790218632) + '请输出以下python脚本的结果：print([111,222][1])')
        await spread_event(ChatPlugin, event)
        self.assertIn('222', event.get_reply().lower())

        event = dummy_friend_message_event('ai 请输出以下python脚本的结果：print([111,222][0])')
        await spread_event(CommandPlugin, event)
        self.assertIn('111', event.get_reply())


if __name__ == '__main__':
    unittest.main()
