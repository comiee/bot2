from public.log import bot_logger
from public.currency import Currency
from public.exception import CostCurrencyFailedException
from public.convert import convert_to
from robot.comm.priority import Priority
from robot.comm.user import User
from robot.comm.sessionStatus import SessionStatus
from alicebot.plugin import Plugin
from alicebot.typing import T_Config, T_Event, T_State
from alicebot.exceptions import GetEventTimeout
from alicebot.adapter.mirai import MiraiAdapter
from alicebot.adapter.mirai.message import T_MiraiMSG, MiraiMessageSegment
from alicebot.adapter.mirai.event import MessageEvent, GroupMemberInfo, GroupMessage
from abc import ABC
from typing import Generic
import re

__all__ = ['PluginBase', 'Session']


class PluginBase(Plugin[T_Event, T_State, T_Config], ABC, Generic[T_Event, T_State, T_Config]):
    priority = -1  # 用无效的priority强制子类定义自己的priority
    block = False

    def __init_subclass__(cls, /, priority: Priority = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if priority is not None:
            cls.priority = priority.priority
            cls.block = priority.block

    @property
    def call_api(self):
        return self.bot.get_adapter(MiraiAdapter).call_api

    @property
    def send(self):
        return self.bot.get_adapter(MiraiAdapter).send


class Session(PluginBase[MessageEvent, T_State, T_Config], ABC, Generic[T_State, T_Config]):
    session_status = SessionStatus()

    @property
    def user(self) -> User:
        """返回qq号对应的User对象"""
        return User(self.qq)

    @property
    def qq(self) -> int:
        """返回qq号"""
        return self.event.sender.id

    @property
    def id(self) -> int:
        """返回群号，如果没有则返回qq号"""
        if isinstance(self.event.sender, GroupMemberInfo):
            return self.event.sender.group.id
        return self.event.sender.id

    @property
    def plain(self) -> str:
        """返回消息中的纯文本内容"""
        return self.event.get_plain_text()

    @property
    def text(self) -> str:
        """返回转换为internal格式的消息"""
        return convert_to('internal', self.event.message)

    def is_group(self):
        return isinstance(self.event, GroupMessage)

    def at(self, target: int = None):
        if not self.is_group():
            return ''
        if target is None:
            target = self.qq
        return MiraiMessageSegment.at(target)

    @property
    def bot_qq(self):
        return getattr(self.bot.config.adapter, 'mirai').qq

    def is_at_bot(self):
        if not self.is_group():
            return True
        return f'[at:{self.bot_qq}]' in self.text

    def exclude_at_bot_text(self):
        if not self.is_group():
            return self.text
        return re.sub(rf'\[at:{self.bot_qq}]\s*', '', self.text)

    async def reply(self, message: T_MiraiMSG, quote: bool = False, at: bool = False) -> None:
        if at and self.is_group():
            message = MiraiMessageSegment.at(self.qq) + message
        bot_logger.info(f'回复消息：{message}')

        if not await self.session_status.can_reply():
            return
        ret = await self.event.reply(message, quote)
        if ret['code'] != 0 or ret['messageId'] == -1 or ret['msg'] != 'success':
            bot_logger.warning(f'回复消息失败：{ret}')
        else:
            self.session_status.record_reply()

    async def ask(self, prompt: T_MiraiMSG = None, quote: bool = False, at: bool = False,
                  timeout: int | float = None, return_plain_text: bool = True) -> str:
        """
        向用户询问
        :param prompt: 询问的话语，如果为None则直接等待回复
        :param quote: 是否引用消息
        :param at: 是否at对方
        :param timeout: 等待回复的时长，超时会抛出GetEventTimeout异常
        :param return_plain_text: 是否返回plain_text
        """
        if prompt:
            await self.reply(prompt, quote, at)
        event = await self.event.get(timeout=timeout)
        if return_plain_text:
            return event.get_plain_text()
        else:
            return convert_to('internal', event.message)

    async def inquire(self, prompt: str, timeout: int | float = None) -> bool:
        """向用户确认，返回用户是否同意"""
        ret = await self.ask(prompt, quote=True, timeout=timeout)
        return ret in {'是', '继续', 'Y', 'y', 'yes', '确认'}

    async def check_cost(self, currencies: list[tuple[int, Currency]]) -> None:
        """检查是否能扣除self.user的num个current类型的货币，如果对方取消或货币不足，会抛出CostCurrencyFailedException异常"""
        try:
            ret = await self.inquire(f'此操作将花费{"、".join(f"{n}{c.value}" for n, c in currencies)}，是否确认？', 60)
        except GetEventTimeout:
            raise CostCurrencyFailedException('等待超时')
        if not ret:
            raise CostCurrencyFailedException('用户取消')
        for num, currency in currencies:
            if self.user.query(currency) < num:
                raise CostCurrencyFailedException(f'货币[{currency.value}]不足')

    async def ensure_cost(self, currencies: list[tuple[int, Currency]]):
        """实际的扣钱操作，与check_cost配合使用"""
        for num, currency in currencies:
            self.user.gain(-num, currency)


"""api
object Paths {

    // about
    const val about = "about"
    const val sessionInfo = "sessionInfo"
    const val botList = "botList"

    // event
    const val newFriend = "resp_newFriendRequestEvent"
    const val memberJoin = "resp_memberJoinRequestEvent"
    const val botInvited = "resp_botInvitedJoinGroupRequestEvent"

    // friend
    const val deleteFriend = "deleteFriend"

    // group
    const val muteAll = "muteAll"
    const val unmuteAll = "unmuteAll"
    const val mute = "mute"
    const val unmute = "unmute"
    const val kick = "kick"
    const val quit = "quit"
    const val essence = "setEssence"
    const val groupConfig = "groupConfig"
    const val memberInfo = "memberInfo"
    const val memberAdmin = "memberAdmin"

    // base info
    const val friendList = "friendList"
    const val groupList = "groupList"
    const val memberList = "memberList"
    const val latestMemberList = "latestMemberList"
    const val botProfile = "botProfile"
    const val friendProfile = "friendProfile"
    const val memberProfile = "memberProfile"
    const val userProfile = "userProfile"

    // message
    const val messageFromId = "messageFromId"
    const val sendFriendMessage = "sendFriendMessage"
    const val sendGroupMessage = "sendGroupMessage"
    const val sendTempMessage = "sendTempMessage"
    const val sendOtherClientMessage = "sendOtherClientMessage"
    const val sendImageMessage = "sendImageMessage"
    const val sendNudge = "sendNudge"
    const val uploadImage = "uploadImage"
    const val uploadVoice = "uploadVoice"
    const val recall = "recall"
    const val roamingMessages = "roamingMessages"

    // file
    const val fileList = "file_list"
    const val fileInfo = "file_info"
    const val fileMkdir = "file_mkdir"
    const val uploadFile = "file_upload"
    const val fileDelete = "file_delete"
    const val fileMove = "file_move"
    const val fileRename = "file_rename"

    // command
    const val commandExecute = "cmd_execute"
    const val commandRegister = "cmd_register"
    
    // announcement
    const val announcementList = "anno_list"
    const val announcementPublish = "anno_publish"
    const val announcementDelete = "anno_delete"

    fun httpPath(s: String): String {
        val t = s.replace("_", "/")
        if (t.startsWith('/')) {
            return t
        }
        return "/$t"
    }
}
"""
