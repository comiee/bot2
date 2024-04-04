from public.message import translate_msg
from robot.plugins.commandPlugin import CommandPlugin
from robot.botClient import get_bot_client
from faker.bot_faker import spread_event, dummy_friend_message_event
from unittest import mock
import unittest

__import__('robot.section.translate')


class TranslateCommandTestCase(unittest.IsolatedAsyncioTestCase):
    async def translate_command_test(self, msg, from_, to_, text):
        bot_client = get_bot_client()
        bot_client.send = mock.Mock()
        event = dummy_friend_message_event(msg)
        await spread_event(CommandPlugin, event)
        bot_client.send.assert_called_once_with(translate_msg.build({
            'from_': from_,
            'to_': to_,
            'text': text,
        }))

    async def test_translate1(self):
        await self.translate_command_test('翻译测试', 'auto', 'en', '测试')

    async def test_translate2(self):
        await self.translate_command_test('测试是什么意思', 'auto', 'en', '测试')

    async def test_translate3(self):
        await self.translate_command_test('测试用英语怎么说', 'auto', '英', '测试')

    async def test_translate4(self):
        await self.translate_command_test('中译英 测试', '中', '英', '测试')


if __name__ == '__main__':
    unittest.main()
