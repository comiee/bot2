from robot.comm.priority import Priority
from robot.comm.pluginBase import PluginBase
from robot.botClient import get_bot_client
from alicebot.adapter.mirai.event import RequestEvent

logger = get_bot_client().logger


class RequestPlugin(PluginBase[RequestEvent, None, None], priority=Priority.Request):
    async def handle(self) -> None:
        await self.event.approve()

    async def rule(self) -> bool:
        if isinstance(self.event, RequestEvent):
            return True
