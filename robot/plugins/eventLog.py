from robot.comm import priority
from robot.botClient import get_bot_client
from alicebot import Plugin
from types import FunctionType
from inspect import isfunction, ismethod

logger = get_bot_client().logger


class LogPlugin(Plugin):
    priority = priority.LOG
    block = False

    async def handle(self) -> None:
        d = {k: getattr(self.event, k) for k in dir(self.event) if
             not k.startswith('_') and k not in ['Config', 'adapter', 'messageChain']
             and not isfunction(getattr(self.event, k)) and not ismethod(getattr(self.event, k))}
        logger.debug(f'收到事件：{d}')

    async def rule(self) -> bool:
        return True
