from public.log import bot_logger
from public.currency import Currency
from public.exception import CostCurrencyFailedException
from public.convert import convert_to
from public.error_code import ErrorCode
from robot.comm.priority import Priority
from robot.comm.user import User
from robot.comm.status import SessionStatus
from alicebot.plugin import Plugin
from alicebot.typing import ConfigT, EventT, StateT
from alicebot.exceptions import GetEventTimeout
from alicebot.message import BuildMessageType
from alicebot.adapter.mirai import MiraiAdapter
from alicebot.adapter.mirai.message import MiraiMessageSegment
from alicebot.adapter.mirai.event import MessageEvent, GroupMemberInfo, GroupMessage
from abc import ABC
from typing import Generic
import re

__all__ = ['PluginBase', 'Session']


class PluginBase(Plugin[EventT, StateT, ConfigT], ABC, Generic[EventT, StateT, ConfigT]):
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


class Session(PluginBase[MessageEvent, StateT, ConfigT], ABC, Generic[StateT, ConfigT]):
    session_state: SessionStatus = SessionStatus

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

    async def reply(self, message: BuildMessageType, quote: bool = None, at: bool = False) -> None:
        if quote is None:
            quote = self.is_group()
        if at and self.is_group():
            message = MiraiMessageSegment.at(self.qq) + message
        bot_logger.info(f'回复消息：{message}')

        if not self.session_state.can_reply():
            return
        async with self.session_state:
            ret = await self.event.reply(message, quote)
            if ret['code'] != 0 or ret['messageId'] == -1 or ret['msg'] != 'success':
                bot_logger.warning(f'回复消息失败：{ret}')

    async def ask(self, prompt: BuildMessageType = None, quote: bool = None, at: bool = False,
                  timeout: int | float = None, return_plain_text: bool = False) -> str:
        """
        向用户询问
        :param prompt: 询问的话语，如果为None则直接等待回复
        :param quote: 是否引用消息，None为群聊引用，私聊不引用
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

    async def __check_cost(self, *currencies: list[tuple[int, Currency]]) -> None:
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

    async def check_cost(self, *currencies: tuple[int, Currency]) -> None:
        try:
            await self.__check_cost(*currencies)
        except CostCurrencyFailedException as e:
            await self.reply(f'命令取消，原因：{e.args[0]}')
            self.skip()

    async def ensure_cost(self, *currencies: tuple[int, Currency]):
        """实际的扣钱操作，与check_cost配合使用"""
        for num, currency in currencies:
            self.user.gain(-num, currency)

    async def handle_error(self, error_code: ErrorCode):
        """处理一些通用错误码，如果错误码不在这里面或者不希望用这种方式处理，需要在外层用别的分支处理"""
        match error_code:
            case ErrorCode.success:
                return
            case ErrorCode.black_list_user:
                await self.reply('你已被列入黑名单，无法使用此命令')
            case ErrorCode.not_super_user:
                await self.reply('权限不足，只有管理员才能使用此命令')
            case ErrorCode.sql_disconnected:
                await self.reply('数据库连接失败，请联系小魅的主人。')
            case ErrorCode.insufficient_coin:
                await self.reply('金币不足！\n签到和玩游戏可以获得金币哦。')
            case ErrorCode.insufficient_stamina:
                await self.reply('体力不足！\n签到可以获得体力哦。')
            case ErrorCode.insufficient_stock:
                await self.reply('持有的股份不足！')
            case _:
                bot_logger.error(f'预期外的错误码：{error_code}')
                await self.reply(f'遇到了预期外的错误，请联系小魅的主人，错误码：{error_code}')


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
