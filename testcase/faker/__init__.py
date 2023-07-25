from alicebot.plugin import Plugin
from alicebot.adapter.mirai.message import T_MiraiMSG, MiraiMessage
from alicebot.adapter.mirai.event import FriendMessage, FriendInfo
from unittest.mock import Mock


async def spread_event(plugin_cls: type[Plugin], event):
    plugin = plugin_cls()
    plugin.event = event
    if await plugin.rule():
        await plugin.handle()


def dummy_friend_message_event(message: T_MiraiMSG):
    event = Mock(FriendMessage)
    event.sender = FriendInfo(id=1234567890, nickname='test_nick_name', remark='test_remark')
    event.messageChain = MiraiMessage(message)
    event.get_plain_text = event.messageChain.get_plain_text
    return event

# TODO 群消息
