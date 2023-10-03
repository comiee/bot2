from robot.plugins.commandPlugin import CommandPlugin
from robot.plugins.chatPlugin import ChatPlugin
from robot.comm.user import User
from test_robot.faker import spread_event, dummy_friend_message_event
from unittest import mock
import unittest

__import__('robot.plugins.test')
__import__('robot.section.config')


class CommandTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_split(self):
        event = dummy_friend_message_event('/split 1 2')
        await spread_event(CommandPlugin, event)
        event.reply.assert_called_once_with("split x='1', y='2'")

    async def test_chat_switch_state(self):
        User.is_super_user = mock.Mock(return_value=True)
        event = dummy_friend_message_event('on')
        event.sender.id = 12345
        await spread_event(CommandPlugin, event)
        self.assertEqual(False, ChatPlugin.chat_state[12345].at_switch)  # 每个id的开关状态独立
        self.assertEqual(True, ChatPlugin.chat_state[67890].at_switch)

        event = dummy_friend_message_event('off')
        event.sender.id = 12345
        await spread_event(CommandPlugin, event)
        self.assertEqual(True, ChatPlugin.chat_state[12345].at_switch)
    # TODO gain命令用例
    # TODO 禁言功能用例
    # TODO 每个功能单独分一个文件


if __name__ == '__main__':
    unittest.main()
