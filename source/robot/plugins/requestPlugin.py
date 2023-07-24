from robot.comm.priority import Priority
from robot.comm.pluginBase import PluginBase
from alicebot.adapter.mirai.event import RequestEvent


class RequestPlugin(PluginBase[RequestEvent, None, None], priority=Priority.Request):
    async def handle(self) -> None:
        await self.event.approve()

    async def rule(self) -> bool:
        if isinstance(self.event, RequestEvent):
            return True
