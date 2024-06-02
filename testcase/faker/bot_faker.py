from robot.comm.pluginBase import Session
from alicebot.plugin import Plugin
from alicebot.message import BuildMessageType
from alicebot.adapter.mirai.message import MiraiMessage
from alicebot.adapter.mirai.event import FriendMessage, FriendInfo
from alicebot.exceptions import EventException
from unittest.mock import Mock

DUMMY_QQ = 1234567890


async def spread_event(plugin_cls: type[Plugin], event):
    plugin = plugin_cls()
    plugin.event = event
    if isinstance(plugin, Session):
        plugin.reply = plugin.event.reply
    try:
        if await plugin.rule():
            await plugin.handle()
    except EventException:
        pass


def dummy_friend_message_event(message: BuildMessageType):
    event = Mock(FriendMessage)
    event.sender = FriendInfo(id=DUMMY_QQ, nickname='test_nick_name', remark='test_remark')
    event.message = MiraiMessage(message)
    event.messageChain = MiraiMessage(message)
    event.get_plain_text = event.messageChain.get_plain_text
    event.get_reply = lambda: event.reply.call_args[0][0]  # call_args的结构是(args, kwargs)
    return event

# TODO 群消息
