from public.currency import Currency
from public.exception import CostCurrencyFailedException
from robot.comm.priority import Priority
from robot.comm.user import User
from alicebot.plugin import Plugin
from alicebot.typing import T_Config, T_Event, T_State
from alicebot.exceptions import GetEventTimeout
from alicebot.adapter.mirai import MiraiAdapter
from alicebot.adapter.mirai.message import MiraiMessage, T_MiraiMSG, MiraiMessageSegment
from alicebot.adapter.mirai.event import MessageEvent, GroupMemberInfo, GroupMessage
from abc import ABC
from typing import Generic

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


class Session(PluginBase[MessageEvent, None, None], ABC):
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
    def text(self) -> str:
        """返回消息中的纯文本内容"""
        return self.event.get_plain_text()

    @staticmethod
    def to_msg(message: MiraiMessage):
        return str(message)  # TODO 转换成自己的格式

    @property
    def msg(self) -> str:
        """返回转换为字符串的消息"""
        return self.to_msg(self.event.message)

    def is_group(self):
        return isinstance(self.event, GroupMessage)

    def at(self, target: int = None):
        if not self.is_group():
            return ''
        if target is None:
            target = self.qq
        return MiraiMessageSegment.at(target)

    async def reply(self, message: T_MiraiMSG, quote: bool = False, at: bool = False) -> dict[str, None]:
        if at and self.is_group():
            message = MiraiMessageSegment.at(self.qq) + message
        return await self.event.reply(message, quote)

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
            return self.to_msg(event.message)

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
