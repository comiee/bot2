from robot.comm.priority import Priority
from robot.comm.pluginBase import PluginBase
from robot.botClient import get_bot_client
from inspect import isfunction, ismethod

logger = get_bot_client().logger


class LogPlugin(PluginBase, priority=Priority.Log):
    async def handle(self) -> None:
        d = {k: getattr(self.event, k) for k in dir(self.event) if
             not k.startswith('_') and k not in ['Config', 'adapter', 'messageChain']
             and not isfunction(getattr(self.event, k)) and not ismethod(getattr(self.event, k))}
        logger.debug(f'收到事件：{d}')

    async def rule(self) -> bool:
        return True