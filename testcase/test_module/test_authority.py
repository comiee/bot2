from public.message import sql_msg
from robot.plugins.commandPlugin import CommandPlugin
from robot.botClient import get_bot_client
from robot.comm.user import User
from faker.master_server_faker import ServerController
from faker.bot_faker import spread_event, dummy_friend_message_event
from unittest import mock
import unittest

__import__('robot.section.config')

class AuthorityTestCase(unittest.IsolatedAsyncioTestCase):
    server_controller = ServerController()

    @classmethod
    def setUpClass(cls):
        cls.server_controller.start()

    @classmethod
    def tearDownClass(cls):
        get_bot_client().send(sql_msg.build(
            'delete from authority where id=0 and type="friend";'
        ))
        cls.server_controller.close()

    async def test_auth_get_default(self):
        User.is_super_user = mock.Mock(return_value=True)
        event = dummy_friend_message_event('auth_get 0 chat')
        await spread_event(CommandPlugin, event)
        self.assertEqual(
            '用户0的chat权限等级为：0',
            event.get_reply()
        )

    async def test_auth_set(self):
        User.is_super_user = mock.Mock(return_value=True)
        event = dummy_friend_message_event('auth_set 0 chat 5')
        await spread_event(CommandPlugin, event)
        self.assertEqual(
            '用户0的chat权限等级已设为：5',
            event.get_reply()
        )
        event = dummy_friend_message_event('auth_get 0 chat')
        await spread_event(CommandPlugin, event)
        self.assertEqual(
            '用户0的chat权限等级为：5',
            event.get_reply()
        )