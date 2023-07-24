from robot.comm.priority import Priority
from robot.comm.user import User
from alicebot.plugin import Plugin
from alicebot.typing import T_Config, T_Event, T_State
from alicebot.adapter.mirai import MiraiAdapter, MiraiMessage
from alicebot.adapter.mirai.event import MessageEvent, GroupMemberInfo
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

    @property
    def reply(self):
        return self.event.reply

    async def ask(self, prompt: str = None, timeout: int | float = None, return_plain_text: bool = True):
        if prompt:
            event = await self.event.ask(prompt, timeout=timeout)
        else:
            event = await self.event.get(timeout=timeout)
        if return_plain_text:
            return event.get_plain_text()
        else:
            return self.to_msg(event.message)
