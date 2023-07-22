from robot.comm.user import User
from robot.comm.pluginBase import PluginBase
from alicebot.adapter.mirai.event import MessageEvent
from alicebot.adapter.mirai.event import GroupMemberInfo
from abc import ABC

__all__ = ['Session']


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

    @property
    def msg(self) -> str:
        """返回转换为字符串的消息"""
        return str(self.event.message) # TODO 转换成自己的格式
