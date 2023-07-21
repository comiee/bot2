from robot.comm.command import get_command_cls_list
from robot.comm.session import Session
from robot.comm.priority import Priority
from alicebot.adapter.mirai.event import MessageEvent


class CommandPlugin(Session,priority=Priority.Command):
    async def handle(self) -> None:
        await self.command.run(self)

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False

        for command_cls in get_command_cls_list():
            if command := command_cls.mate(self):
                self.command = command
                return True
        return False
