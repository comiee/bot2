from robot.comm.command import *
from robot.comm.pluginBase import Session
from robot.comm.user import User
from robot.plugins.commandPlugin import CommandPlugin
from faker.bot_faker import spread_event, dummy_friend_message_event
from unittest import mock
import unittest


class CommandTrimTestCase(unittest.IsolatedAsyncioTestCase):
    # TODO 补充其他类型的命令的用例
    async def test_super_command(self):
        fun_mock = mock.Mock()
        FullCommand('test_super_command').trim_super()(fun_mock)

        event = dummy_friend_message_event('test_super_command')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_not_called()

        User.is_super_user = mock.Mock(return_value=True)
        event = dummy_friend_message_event('test_super_command')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_called_once()

    @mock.patch('robot.comm.pluginBase.Session.user', new_callable=mock.PropertyMock)
    async def test_cost_command(self, user_property_mock):
        fun_mock = mock.Mock()
        FullCommand('test_cost_command').trim_cost((10, Currency.coin))(fun_mock)

        user_mock = mock.Mock(User)
        user_property_mock.return_value = user_mock
        Session.inquire = mock.AsyncMock(return_value=True)

        user_mock.query.return_value = 9
        event = dummy_friend_message_event('test_cost_command')
        await spread_event(CommandPlugin, event)
        user_mock.gain.assert_not_called()
        event.reply.assert_called_once_with('命令取消，原因：货币[金币]不足')

        user_mock.query.return_value = 10
        event = dummy_friend_message_event('test_cost_command')
        await spread_event(CommandPlugin, event)
        user_mock.gain.assert_called_with(-10, Currency.coin)
        fun_mock.assert_called_once()

    async def test_switch_command_change(self):
        fun_mock = mock.Mock()
        FullCommand('test_switch_command_change') \
            .trim_switch(False,
                         'test_switch_command_change_switch_on',
                         'test_switch_command_change_switch_off'
                         )(fun_mock)
        User.is_super_user = mock.Mock(return_value=True)

        event = dummy_friend_message_event('test_switch_command_change')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_not_called()

        fun_mock.reset_mock()
        switch_event = dummy_friend_message_event('test_switch_command_change_switch_on')
        await spread_event(CommandPlugin, switch_event)
        switch_event.reply.assert_called_once_with('test_switch_command_change命令开关：开')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_called_once()

        fun_mock.reset_mock()
        switch_event = dummy_friend_message_event('test_switch_command_change_switch_off')
        await spread_event(CommandPlugin, switch_event)
        switch_event.reply.assert_called_once_with('test_switch_command_change命令开关：关')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_not_called()

    async def test_switch_command_turn(self):
        fun_mock = mock.Mock()
        FullCommand('test_switch_command_turn') \
            .trim_switch(False,
                         'test_switch_command_turn_switch',
                         )(fun_mock)
        User.is_super_user = mock.Mock(return_value=True)

        event = dummy_friend_message_event('test_switch_command_turn')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_not_called()

        fun_mock.reset_mock()
        switch_event = dummy_friend_message_event('test_switch_command_turn_switch')
        await spread_event(CommandPlugin, switch_event)
        switch_event.reply.assert_called_once_with('test_switch_command_turn命令开关：开')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_called_once()

        fun_mock.reset_mock()
        switch_event = dummy_friend_message_event('test_switch_command_turn_switch')
        await spread_event(CommandPlugin, switch_event)
        switch_event.reply.assert_called_once_with('test_switch_command_turn命令开关：关')
        await spread_event(CommandPlugin, event)
        fun_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
