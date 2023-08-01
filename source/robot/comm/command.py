from public.currency import Currency
from public.log import bot_logger
from public.exception import CostCurrencyFailedException
from robot.comm.pluginBase import Session
from alicebot.exceptions import GetEventTimeout
from abc import abstractmethod
from inspect import iscoroutinefunction, signature
import re


class _CommandMeta(type):
    def __init__(cls, name, bases, attrs):  # 定义新类的时候执行
        super().__init__(name, bases, attrs)
        cls.commands: list[Command] = []

    def __call__(cls, *args, **kwargs):  # 新类实例化时执行
        obj = super().__call__(*args, **kwargs)
        cls.commands.append(obj)
        return obj

    def mate(cls, session: Session):  # 新类的类方法
        for command in cls.commands:
            if command.judge(session):
                bot_logger.info(f'匹配到{command}')
                return command


class Command(metaclass=_CommandMeta):
    def __init__(self, cmd):
        # 不设置别名系统，多个cmd用嵌套装饰器或正则命令解决
        # 如果有多个命令匹配，只会执行第一个命令
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

    async def run(self, session: Session) -> None:
        if iscoroutinefunction(self.fun):
            await self.fun(session, *self.args, **self.kwargs)
        else:
            self.fun(session, *self.args, **self.kwargs)

    def trim_super(self):
        """将命令变为管理员命令，除了限定使用者以外和原命令一样"""
        judge = self.judge

        def judge_wrapper(session: Session) -> bool:
            if not session.user.is_super_user():
                return False
            return judge(session)

        self.judge = judge_wrapper
        return self

    def trim_cost(self, num: int, currency: Currency, *args):
        """将命令变为需要花费货币的命令，限制命令在执行时先扣除一定的货币，可同时传入多个num和currency，如cost_command(Command, 1, A, 2, B)。
        如果回调函数中抛出CostCurrencyFailedException异常或使用了stop、skip等中途退出的操作则不会扣钱"""
        # 也可以嵌套使用，但是分开询问是否扣钱
        run = self.run
        currencies = [(num, currency), *((args[i], args[i + 1]) for i in range(0, len(args), 2))]

        async def run_wrapper(session: Session) -> None:
            try:
                await session.check_cost(currencies)
                await run(session)
            except CostCurrencyFailedException as e:
                await session.reply(f'命令取消，原因：{e.args[0]}')
            else:
                await session.ensure_cost(currencies)

        self.run = run_wrapper
        return self

    def trim_white_list(self, users: set[int], groups: set[int]):
        """TODO 将命令变为白名单命令"""

    def trim_black_list(self, users: set[int], groups: set[int]):
        """TODO 将命令变为黑名单命令"""

    def trim_friend(self, tip: str = None):
        """TODO 将命令变为私聊命令，如果tip不为None，会在非私聊场景下回复tip"""

    def trim_group(self, tip: str = None):
        """TODO 将命令变为群聊命令，如果tip不为None，会在非群聊场景下回复tip"""


class FullCommand(Command):
    """全匹配命令，只有与文本完全匹配才会生效"""

    def judge(self, session: Session) -> bool:
        return session.text == self.cmd


class SplitCommand(Command):
    """分割命令，用空格分割，分割后的第一项为命令，其余项为会被set_args设置为参数，参数的个数和回调函数的参数个数不匹配时不会执行，可以通过定义多个的形式重载"""

    def judge(self, session: Session) -> bool:
        if not session.text:
            return False
        cmd, *args = session.text.strip().split()
        if cmd != self.cmd:
            return False
        if len(args) != len(signature(self.fun).parameters) - 1:
            return False
        self.set_args(*args)
        return True


class SplitArgCommand(Command):
    """分割参数命令，与SplitCommand的不同在于如果参数不足会询问"""

    def __init__(self, cmd, prompts: list[str], too_many_arg_reply: str = None,
                 timeout: int | float = 10 * 60, timeout_reply: str = '等待参数超时，命令终止。'):
        """
        :param prompts: prompts[i]为缺少第i个参数时的询问语句
        :param too_many_arg_reply: 当参数过多时的回复，如果为None会忽略多余的参数
        :param timeout: 每次询问的等待时间
        :param timeout_reply: 超时后的回复
        """
        super().__init__(cmd)
        self.prompts = prompts
        self.too_many_arg_reply = too_many_arg_reply
        self.timeout = timeout
        self.timeout_reply = timeout_reply

    def judge(self, session: Session) -> bool:
        if not session.text:
            return False
        cmd, *args = session.text.strip().split()
        if cmd != self.cmd:
            return False
        self.set_args(*args)
        return True

    async def run(self, session: Session) -> None:
        args = list(self.args)
        while len(args) < len(self.prompts):
            try:
                text = await session.ask(self.prompts[len(args)], timeout=self.timeout)
                args.extend(text.split())
            except GetEventTimeout:
                await session.reply(self.timeout_reply)
                return
        if len(args) > len(self.prompts) and self.too_many_arg_reply is not None:
            await session.reply(self.too_many_arg_reply)
            return
        self.set_args(*args[:len(self.prompts)])
        await super().run(session)


class NormalCommand(Command):
    """普通命令，判断是否以命令开头，将其余的部分作为参数传入回调函数"""

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


def get_command_cls_list() -> list[type[Command]]:
    # 下面的顺序决定了命令匹配的优先级
    return [
        FullCommand,
        SplitCommand,
        NormalCommand,
        SplitArgCommand,
        RegexCommand,
    ]
