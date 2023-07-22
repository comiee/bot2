from robot.comm.priority import Priority
from robot.comm.pluginBase import PluginBase
from alicebot.adapter.mirai.event import FriendInputStatusChangedEvent


class FilterPlugin(PluginBase, priority=Priority.Filter):
    async def handle(self) -> None:
        pass

    async def rule(self) -> bool:
        return isinstance(self.event, (
            FriendInputStatusChangedEvent,
        ))
