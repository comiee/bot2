from robot.comm.pluginBase import Session
from alicebot.plugin import Plugin
from alicebot.message import BuildMessageType
from alicebot.adapter.mirai.message import MiraiMessage
from alicebot.adapter.mirai.event import FriendMessage, FriendInfo, GroupMessage, GroupMemberInfo, GroupInfo
from alicebot.adapter.mirai import MiraiAdapter
from alicebot.bot import Bot
from alicebot.exceptions import EventException
from unittest.mock import Mock

DUMMY_QQ = 1234567890
DUMMY_GROUP = 987654321


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


def _init_dummy_message_event(event, message: BuildMessageType):
    bot = Mock(Bot)
    bot.config = Mock()
    bot.config.adapter = Mock()
    bot.config.adapter.mirai = Mock()
    bot.config.adapter.mirai.qq = 1790218632
    event.adapter = MiraiAdapter(bot)
    event.message = MiraiMessage(message)
    event.messageChain = MiraiMessage(message)
    event.get_plain_text = event.messageChain.get_plain_text
    # call_args的结构是(args, kwargs)
    event.get_reply = lambda: event.reply.call_args[0][0] if event.reply.call_args else ''
    return event


def dummy_friend_message_event(message: BuildMessageType):
    event = Mock(FriendMessage)
    event.sender = FriendInfo(
        id=DUMMY_QQ,
        nickname='test_nick_name',
        remark='test_remark',
    )
    _init_dummy_message_event(event, message)
    return event


def dummy_group_message_event(message: BuildMessageType):
    event = Mock(GroupMessage)
    event.sender = GroupMemberInfo(
        id=DUMMY_QQ,
        memberName='test_member_name',
        permission="MEMBER",
        specialTitle='test_special_title',
        joinTimestamp=123,
        lastSpeakTimestamp=456,
        muteTimeRemaining=789,
        group=GroupInfo(
            id=DUMMY_GROUP,
            name='test_group_name',
            permission="MEMBER",
        ),
    )
    _init_dummy_message_event(event, message)
    return event
