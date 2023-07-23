from tools.log import bot_logger
from robot.comm.pluginBase import Session
from abc import abstractmethod
from inspect import iscoroutinefunction
import re


class _CommandMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.commands: list[Command] = []

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        cls.commands.append(obj)
        return obj

    def mate(cls, session: Session):
        for command in cls.commands:
            if command.judge(session):
                bot_logger.info(f'匹配到{command}')
                return command


class Command(metaclass=_CommandMeta):
    def __init__(self, cmd):
        # 不设置别名系统，多个cmd用嵌套装饰器解决
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
        else:
            self.fun(session, *self.args, **self.kwargs)


class FullCommand(Command):
    """全匹配命令，只有与文本完全匹配才会生效"""

    def judge(self, session: Session) -> bool:
        return session.text == self.cmd


class SplitCommand(Command):
    """分割命令，用空格分割，分割后的第一项为命令，其余项为参数，参数会被传入回调函数"""

    def judge(self, session: Session) -> bool:
        if not session.text:
            return False
        cmd, *args = session.text.strip().split()
        if cmd != self.cmd:
            return False
        self.set_args(*args)
        return True


class NormalCommand(Command):
    """普通命令，判断是否已命令开头，将其余的部分作为参数传入回调函数"""

    def judge(self, session: Session) -> bool:
        if not session.text.startswith(self.cmd):
            return False
        arg = session.text[len(self.cmd):]
        self.set_args(arg)
        return True


class RegexCommand(Command):
    """正则命令，回调函数的参数为解包后的groups。比较复杂的表达式可以使用re.compile"""

    def judge(self, session: Session) -> bool:
        m = re.search(self.cmd, session.text)
        if not m:
            return False
        self.set_args(*m.groups())
        return True


def super_command(command: Command):
    """将命令变为管理员命令，除了限定使用者以外和原命令一样"""
    command_judge = command.judge

    def judge_wrapper(session: Session) -> bool:
        if not session.user.is_super_user():
            return False
        return command_judge(session)

    command.judge = judge_wrapper
    return command


def get_command_cls_list():
    # 下面的顺序决定了命令匹配的优先级
    return [
        FullCommand,
        NormalCommand,
        RegexCommand,
    ]
