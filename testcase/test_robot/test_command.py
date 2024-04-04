from robot.comm.status import ChatStatus, SessionStatus, status_load
from robot.plugins.commandPlugin import CommandPlugin
from robot.comm.user import User
from faker.bot_faker import spread_event, dummy_friend_message_event, DUMMY_QQ
from unittest import mock
import unittest

__import__('robot.section.config')


class CommandTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_chat_switch_state(self):
        User.is_super_user = mock.Mock(return_value=True)
        event = dummy_friend_message_event('on')
        event.sender.id = 12345
        await spread_event(CommandPlugin, event)
        self.assertEqual(False, ChatStatus[12345].at_switch)  # 每个id的开关状态独立
        self.assertEqual(True, ChatStatus[67890].at_switch)

        event = dummy_friend_message_event('off')
        event.sender.id = 12345
        await spread_event(CommandPlugin, event)
        self.assertEqual(True, ChatStatus[12345].at_switch)

    async def test_config(self):
        User.is_super_user = mock.Mock(return_value=True)
        event = dummy_friend_message_event('config interval 3')
        await spread_event(CommandPlugin, event)
        self.assertEqual(3, SessionStatus[DUMMY_QQ].interval)

        status_load()
        self.assertEqual(3, SessionStatus[DUMMY_QQ].interval)

    # TODO gain命令用例
    # TODO 禁言功能用例
    # TODO 每个功能单独分一个文件


if __name__ == '__main__':
    unittest.main()
