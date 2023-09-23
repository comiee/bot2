from robot.comm.command import *
from robot.plugins.commandPlugin import CommandPlugin
from test_robot.faker import spread_event, dummy_friend_message_event
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


if __name__ == '__main__':
    unittest.main()
