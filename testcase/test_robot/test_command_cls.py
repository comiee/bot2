from robot.comm.command import *
from robot.comm.pluginBase import Session
from robot.comm.user import User
from robot.plugins.commandPlugin import CommandPlugin
from faker import spread_event, dummy_friend_message_event
from unittest import mock
import unittest


class CommandClassTestCase(unittest.IsolatedAsyncioTestCase):
    # TODO 补充其他类型的命令的用例
    @mock.patch('robot.comm.pluginBase.Session.user', new_callable=mock.PropertyMock)
    async def test_cost_command(self, user_property_mock):
        @cost_command(FullCommand('test_cost_command'), 10, Currency.coin)
        def test_fun(_: Session):
            pass

        user_mock = mock.Mock(User)
        user_property_mock.return_value = user_mock
        Session.inquire = mock.AsyncMock(return_value=True)

        user_mock.query.return_value = 9
        event = dummy_friend_message_event('test_cost_command')
        await spread_event(CommandPlugin, event)
        user_mock.gain.assert_not_called()
        event.reply.assert_called_once_with('命令取消，原因：货币不足')

        user_mock.query.return_value = 10
        event = dummy_friend_message_event('test_cost_command')
        await spread_event(CommandPlugin, event)
        user_mock.gain.assert_called_with(-10, Currency.coin)



if __name__ == '__main__':
    unittest.main()
