from robot.comm.session import Session
from robot.botClient import get_bot_client
from abc import ABCMeta, abstractmethod
from inspect import iscoroutinefunction

logger = get_bot_client().logger


class CommandMeta(type, metaclass=ABCMeta):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.commands: list[Command] = []

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        cls.commands.append(obj)
        return obj

    def mate(cls, session: Session):
        for command in cls.commands:
            logger.debug(f'尝试匹配{command}')
            if command.judge(session):
                logger.info(f'匹配到{command}')
                return command


class Command(metaclass=CommandMeta):
    def __init__(self, cmd):
        self.cmd = cmd
        self.args = ()
        self.kwargs = {}

    def __call__(self, fun):
        """fun的类型为函数或异步函数，第一个参数为session，其余参数为set_args设置的参数"""
        self.fun = fun
        return fun

    def __repr__(self):
        return f'{type(self).__name__}<{self.cmd}>'

    @abstractmethod
    def judge(self, session: Session) -> bool:
        """判断是否需要执行此命令，可同时设置执行fun时的参数"""
        pass

    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def run(self, session: Session):
        if iscoroutinefunction(self.fun):
            await self.fun(session, *self.args, **self.kwargs)
        self.fun(session, *self.args, **self.kwargs)


class FullCommand(Command):
    """全匹配命令，只有与文本完全匹配才会生效"""

    def judge(self, session: Session) -> bool:
        return session.text == self.cmd


class NormalCommand(Command):
    """普通命令，用空格分割，分割后的第一项为命令，其余项为参数，参数会被传入回调函数"""

    def __init__(self, cmd, *names):
        super().__init__(cmd)
        self.names = (cmd, *names)

    def judge(self, session: Session) -> bool:
        if not session.text:
            return False
        cmd, *args = session.text.strip().split()
        if all(name != cmd for name in self.names):
            return False
        self.set_args(*args)
        return True


class SuperCommand(NormalCommand):
    """管理员命令，除了限定使用者以外和普通命令一样"""

    def judge(self, session: Session) -> bool:
        if not session.user.is_super_user():
            return False
        return super().judge(session)


class RegexCommand(Command):
    """正则命令"""

    def judge(self, session: Session) -> bool:
        return False  # TODO


def get_command_cls_list():
    # 下面的顺序决定了命令匹配的优先级
    return [
        FullCommand,
        SuperCommand,
        NormalCommand,
        RegexCommand,
    ]
