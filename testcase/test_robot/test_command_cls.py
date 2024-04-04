from robot.comm.command import *
from robot.plugins.commandPlugin import CommandPlugin
from faker.bot_faker import spread_event, dummy_friend_message_event
from unittest import mock
import unittest


class CommandClassTestCase(unittest.IsolatedAsyncioTestCase):
    # TODO 补充其他类型的命令的用例

    async def test_keyword_command(self):
        fun_mock = mock.Mock()

        @KeywordCommand('test_keyword_command')
        def _(session, a, b, c, d=4):
            fun_mock(session, a, b, c, d)

        event = dummy_friend_message_event('test_keyword_command a=1 b:2 c：3')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_called_with(mock.ANY, '1', '2', '3', 4)

    async def test_arg_command(self):
        fun_mock = mock.Mock()

        @ArgCommand('test_arg_command')
        def _(session, a, b='2'):
            fun_mock(session, a, b)

        event = dummy_friend_message_event('test_arg_command')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_not_called()
        fun_mock.reset_mock()

        event = dummy_friend_message_event('test_arg_command 1')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_called_with(mock.ANY, '1', '2')
        fun_mock.reset_mock()

        event = dummy_friend_message_event('test_arg_command 1 3')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_called_with(mock.ANY, '1', '3')
        fun_mock.reset_mock()

        event = dummy_friend_message_event('test_arg_command 1 2 3')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_not_called()
        fun_mock.reset_mock()

        event = dummy_friend_message_event('test_arg_command(1,2)')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_called_with(mock.ANY, '1', '2')
        fun_mock.reset_mock()


if __name__ == '__main__':
    unittest.main()
