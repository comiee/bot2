from public.log import qq_bot_logger
from abc import abstractmethod


class _CommandMeta(type):
    def __init__(cls, name, bases, attrs):  # 定义新类的时候执行
        super().__init__(name, bases, attrs)
        cls.__commands: dict[str, Command] = {}

    def __call__(cls, *args, **kwargs):  # 新类实例化时执行
        obj = super().__call__(*args, **kwargs)
        cls.__commands[obj.cmd] = obj
        return obj

    def find(cls, cmd):
        return cls.__commands.get(cmd, None)


class Command(metaclass=_CommandMeta):
    def __init__(self, cmd):
        self.cmd = cmd

    def __call__(self, fun):
        self._fun = fun
        return fun

    def __repr__(self):
        return f'{type(self).__name__}<{self.cmd}>'

    @abstractmethod
    async def handle(self, message, text):
        pass


class SingleCommand(Command):
    """单次命令，接收一个输入返回一个输出"""
    async def handle(self, message, text):
        result = self._fun(text)
        await message.reply(content=result)
        qq_bot_logger.info(f'qqbot 执行命令：{self.cmd}，参数：{text}，回复：{result}')
