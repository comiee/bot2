from robot.comm.command import get_command_cls_list
from robot.comm.pluginBase import Session
from robot.comm.priority import Priority
from alicebot.adapter.mirai.event import MessageEvent


class CommandPlugin(Session, priority=Priority.Command):
    async def handle(self) -> None:
        await self.command.run(self)
        self.stop()  # 使用stop阻碍其他插件，如果命令中途退出需要继续执行其他插件，使用skip解决

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False

        for command_cls in get_command_cls_list():
            if command := command_cls.mate(self):
                self.command = command
                return True
        return False
