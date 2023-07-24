from alicebot.plugin import Plugin
from alicebot.adapter.mirai.message import T_MiraiMSG, MiraiMessage, MiraiMessageSegment
from alicebot.adapter.mirai.event import MessageEvent, FriendInfo
from unittest.mock import Mock
import asyncio


def async_test_case(co):
    def wrapper(*args, **kwargs):
        asyncio.run(co(*args, **kwargs))

    return wrapper


async def dummy_event(plugin_cls: type[Plugin], event):
    plugin = plugin_cls()
    plugin.event = event
    if await plugin.rule():
        await plugin.handle()


async def dummy_friend_message(plugin_cls: type[Plugin], message: T_MiraiMSG):
    event = Mock(MessageEvent)

    async def reply_stub(msg: "T_MiraiMSG", _: bool = False):
        event.result = msg
        return {}

    event.reply = reply_stub
    event.sender = FriendInfo(id=233, nickname='test_nickname', remark='test_remark')
    event.messageChain = message
    event.get_plain_text = message.get_plain_text

    await dummy_event(plugin_cls, event)
    return event.result


async def dummy_friend_text(plugin_cls: type[Plugin], text: str):
    return await dummy_friend_message(plugin_cls, MiraiMessage(MiraiMessageSegment.plain(text)))
