from public.currency import Currency
from public.log import bot_logger
from public.state import State
from robot.comm.pluginBase import Session
from alicebot.exceptions import GetEventTimeout
from abc import abstractmethod
from inspect import iscoroutinefunction, signature
from typing import Callable, Awaitable
import re
import asyncio
import traceback


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
    JudgeFun = Callable[[Session], bool]
    RunFun = Callable[[Session], Awaitable[None]]

    def __init__(self, cmd):
        # 不设置别名系统，多个cmd用嵌套装饰器或正则命令解决
        # 如果有多个命令匹配，只会执行第一个命令
        self._cmd = cmd
        self._args = ()
        self._kwargs = {}

    def __call__(self, fun):
        """fun的类型为函数或异步函数，第一个参数为session，其余参数为set_args设置的参数"""
        self._fun = fun
        return fun

    def __repr__(self):
        return f'{type(self).__name__}<{self._cmd}>'

    @abstractmethod
    def judge(self, session: Session) -> bool:
        """判断是否需要执行此命令，可同时设置执行fun时的参数"""
        pass

    def set_args(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    async def run(self, session: Session) -> None:
        if iscoroutinefunction(self._fun):
            await self._fun(session, *self._args, **self._kwargs)
        else:
            self._fun(session, *self._args, **self._kwargs)

    def _before_judge(self, judge_fun: JudgeFun):
        judge = self.judge

        def new_judge(session: Session):
            return judge_fun(session) and judge(session)

        self.judge = new_judge
        return judge_fun

    def _after_judge(self, judge_fun: JudgeFun):
        judge = self.judge

        def new_judge(session: Session):
            return judge(session) and judge_fun(session)

        self.judge = new_judge
        return judge_fun

    def _replace_judge(self, judge_fun: Callable[[JudgeFun, Session], bool]):
        judge = self.judge

        def new_judge(session: Session):
            return judge_fun(judge, session)

        self.judge = new_judge
        return judge_fun

    def _before_run(self, run_fun: RunFun):
        run = self.run

        async def new_run(session: Session):
            await run_fun(session)
            await run(session)

        self.run = new_run
        return run_fun

    def _after_run(self, run_fun: RunFun):
        run = self.run

        async def new_run(session: Session):
            await run(session)
            await run_fun(session)

        self.run = new_run
        return run_fun

    def _replace_run(self, run_fun: Callable[[RunFun, Session], Awaitable[None]]):
        run = self.run

        async def new_run(session: Session):
            await run_fun(run, session)

        self.run = new_run
        return run_fun

    def trim_super(self):
        """将命令变为管理员命令，限定使用者为管理员并在执行出错时返回错误"""

        @self._after_judge
        def judge_super(session: Session) -> bool:
            return session.user.is_super_user()

        @self._replace_run
        async def run_super(run: Command.RunFun, session: Session) -> None:
            try:
                await run(session)
            except Exception as e:
                await session.reply(str(e))
                traceback.print_exc()

        return self

    def trim_cost(self, *currencies: tuple[int, Currency]):
        """将命令变为需要花费货币的命令，限制命令在执行时先扣除一定的货币。
        如果回调函数中使用了stop、skip等中途退出的操作则不会扣钱"""

        # 也可以嵌套使用，但是分开询问是否扣钱
        @self._replace_run
        async def run_cost(run: Command.RunFun, session: Session) -> None:
            await session.check_cost(*currencies)
            await run(session)
            await session.ensure_cost(*currencies)

        return self

    def trim_white_list(self, users: set[int] = (), groups: set[int] = (), friends: set[int] = ()):
        """将命令变为白名单命令"""

        @self._after_judge
        def judge_white_list(session: Session) -> bool:
            if session.is_group():
                return session.qq in users or session.id in groups
            else:
                return session.qq in users or session.id in friends

        return self

    def trim_black_list(self, users: set[int] = (), groups: set[int] = (), friends: set[int] = ()):
        """将命令变为黑名单命令"""

        @self._after_judge
        def judge_black_list(session: Session) -> bool:
            if session.is_group():
                return session.qq not in users and session.id not in groups
            else:
                return session.qq not in users and session.id not in friends

        return self

    def trim_friend(self, tip: str = None):
        """将命令变为私聊命令，如果tip不为None，会在非私聊场景下回复tip"""

        @self._after_judge
        def judge_friend(session: Session) -> bool:
            if session.is_group():
                if tip is not None:
                    asyncio.create_task(session.reply(tip))
                return False
            return True

        return self

    def trim_group(self, tip: str = None):
        """将命令变为群聊命令，如果tip不为None，会在非群聊场景下回复tip"""

        @self._after_judge
        def judge_group(session: Session) -> bool:
            if not session.is_group():
                if tip is not None:
                    asyncio.create_task(session.reply(tip))
                return False
            return True

        return self

    def trim_administrator(self, tip: str = None):
        """限制命令的使用条件为只有机器人是群管理或群主时才能使用，如果tip不为None，会在不满足条件时回复tip"""

        @self._after_judge
        def judge_administrator(session: Session) -> bool:
            if not session.is_group() or session.event.sender.group.permission not in {"OWNER", "ADMINISTRATOR"}:
                if tip is not None:
                    asyncio.create_task(session.reply(tip))
                return False
            return True

        return self

    def trim_user_times(self, times: int):
        """TODO 限制单用户使用命令的次数"""

    def trim_friend_times(self, times: int):
        """TODO 限制私聊中使用命令的次数"""

    def trim_group_times(self, times: int):
        """TODO 限制群聊中使用命令的次数"""

    def trim_user_cd(self, second: int):
        """TODO 限制单用户使用间隔时间"""

    def trim_group_cd(self, second: int):
        """TODO 限制群组使用间隔时间"""

    def trim_switch(self, default_state: bool, cmd_on: str, cmd_off: str = '', cmd_name: str = ''):
        """
        使该命令可被开关（只有管理员才能操作开关）
        :param default_state: 开关的默认状态
        :param cmd_on: 开启用的命令
        :param cmd_off: 关闭用的命令，如果为空字符串，则和cmd_on相同
        :param cmd_name: 对外显示开关状态时使用的名字，如果为空字符串则使用self.cmd
        :return: 装饰后的command
        """
        switch = State(default_value=default_state)
        if not cmd_name:
            cmd_name = self._cmd

        async def switch_change(session: Session, switch_state: bool):
            switch[session.id] = switch_state
            await session.reply(f'{cmd_name}命令开关：' + '关开'[switch_state])

        if cmd_off:
            @FullCommand(cmd_on).trim_super()
            async def switch_on(session: Session):
                await switch_change(session, True)

            @FullCommand(cmd_off).trim_super()
            async def switch_off(session: Session):
                await switch_change(session, False)
        else:
            @FullCommand(cmd_on).trim_super()
            async def switch_turn(session: Session):
                await switch_change(session, not switch[session.id])

        @self._before_judge  # 开关的优先级优于原来的judge
        def judge_switch(session: Session) -> bool:
            return switch[session.id]

        return self


class FullCommand(Command):
    """全匹配命令，只有与文本完全匹配才会生效"""

    def judge(self, session: Session) -> bool:
        return session.text == self._cmd


class NormalCommand(Command):
    """普通命令，判断是否以命令开头，将其余的部分作为参数传入回调函数"""

    def judge(self, session: Session) -> bool:
        if not session.text.startswith(self._cmd):
            return False
        arg = session.text[len(self._cmd):]
        self.set_args(arg)
        return True


class RegexCommand(Command):
    """正则命令，回调函数的参数为解包后的groups。比较复杂的表达式可以使用re.compile"""

    def judge(self, session: Session) -> bool:
        m = re.search(self._cmd, session.text)
        if not m:
            return False
        self.set_args(*m.groups())
        return True


class SplitCommand(Command):
    """分割命令，用空格分割，分割后的第一项为命令，其余项为会被set_args设置为参数，参数的个数和回调函数的参数个数不匹配时不会执行，可以通过定义多个的形式重载"""

    def judge(self, session: Session) -> bool:
        if not session.text.strip():
            return False
        cmd, *args = session.text.strip().split()
        if cmd != self._cmd:
            return False
        if len(args) != len(signature(self._fun).parameters) - 1:
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
        if not session.text.strip():
            return False
        cmd, *args = session.text.strip().split()
        if cmd != self._cmd:
            return False
        self.set_args(*args)
        return True

    async def run(self, session: Session) -> None:
        args = list(self._args)
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


class KeywordCommand(Command):
    """关键字命令，用空格每个参数，用冒号或等号分割k和v，结果会用关键字传参传到回调函数里"""

    def judge(self, session: Session) -> bool:
        cmd, *args = session.text.strip().split()
        if cmd != self._cmd:
            return False
        kwargs = {}
        for s in args:
            if m := re.search(r'^(.+?)[=:：](.+?)$', s):
                k, v = m.groups()
                kwargs[k] = v
            else:
                return False
        try:
            signature(self._fun).bind(session, **kwargs)
        except TypeError:
            return False
        self.set_args(**kwargs)
        return True


def get_command_cls_list() -> list[type[Command]]:
    # 下面的顺序决定了命令匹配的优先级
    return [
        FullCommand,
        SplitCommand,
        SplitArgCommand,
        NormalCommand,
        KeywordCommand,
        RegexCommand,
    ]
