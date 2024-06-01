from robot.plugins.commandPlugin import CommandPlugin
from faker.master_server_faker import AsyncServerController
from faker.bot_faker import spread_event, dummy_friend_message_event
import unittest

__import__('robot.section.baike')


class BaikeTestCase(unittest.IsolatedAsyncioTestCase):
    server_controller = AsyncServerController()

    @classmethod
    def setUpClass(cls):
        cls.server_controller.start()

    @classmethod
    def tearDownClass(cls):
        cls.server_controller.close()

    async def test_baike(self):
        event = dummy_friend_message_event('机器人是什么')
        await spread_event(CommandPlugin, event)
        self.assertEqual(1, event.reply.call_count)
        text = event.reply.call_args[0][0]  # call_args的结构是(args, kwargs)
        print(text)
        self.assertEqual(
            '机器人（Robot）是一种能够半自主或全自主工作的智能机器。机器人能够通过编程和自动控制来执行诸如作业或移动等任务。历史上最早的机器人见于隋炀帝命工匠按照柳抃形象所营造的木偶机器人，施有机关，有坐、起、拜、伏等能力。机器人具有感知、决策、执行等基本特征，可以辅助甚至替代人类完成危险、繁重、复杂的工作，提高工作效率与质量，服务人类生活，扩大或延伸人的活动及能力范围。 2021年，美国1/3的手术是使用机器人系统进行的。 2023年，美国亚利桑那州立大学（ASU）科学家研制出了世界上第一个能像人类一样出汗、颤抖和呼吸的户外行走机器人模型。\n————来自百度百科',
            text)
