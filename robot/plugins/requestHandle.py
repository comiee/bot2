from robot.comm import priority
from robot.botClient import get_bot_client
from alicebot import Plugin
from alicebot.adapter.mirai.event import RequestEvent

logger = get_bot_client().logger


class RequestPlugin(Plugin):
    priority = priority.REQUEST
    block = True

    async def handle(self) -> None:
        await self.event.approve()

    async def rule(self) -> bool:
        if isinstance(self.event, RequestEvent):
            return True
