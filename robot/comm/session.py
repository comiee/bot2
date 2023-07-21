from robot.comm.user import User
from robot.comm.pluginBase import PluginBase
from alicebot.adapter.mirai.event import MessageEvent
from abc import ABC

__all__ = ['Session']


class Session(PluginBase[MessageEvent, None, None], ABC):
    @property
    def user(self) -> User:
        return User(self.qq)

    @property
    def qq(self) -> int:
        return self.event.sender.id

    @property
    def text(self) -> str:
        return self.event.get_plain_text()
