from communication.client import Client
from tools.log import get_logger, LogLevel
from alicebot import Bot
from alicebot.adapter.mirai import MiraiAdapter
from alicebot.adapter.mirai.message import T_MiraiMSG
import asyncio

__all__ = ['get_bot_client']


class BotProxy:
    def __init__(self, bot: Bot, event_loop: asyncio.AbstractEventLoop):
        self.bot = bot
        self.event_loop = event_loop

    def __run_in_bot_event_loop(self, coro):
        # 不可用self.__event_loop.create_task(coro).result()，这种写法的result不会等待结果，会报错
        return asyncio.run_coroutine_threadsafe(coro, self.event_loop).result()

    def send_friend(self, message: T_MiraiMSG, target: int, quote: int = None):
        return self.__run_in_bot_event_loop(
            self.bot.get_adapter(MiraiAdapter).send(message, 'friend', target, quote)
        )

    def send_group(self, message: T_MiraiMSG, target: int, quote: int = None):
        return self.__run_in_bot_event_loop(
            self.bot.get_adapter(MiraiAdapter).send(message, 'group', target, quote)
        )

    def call_api(self, command: str, sub_command: str = None, **content):
        return self.__run_in_bot_event_loop(
            self.bot.get_adapter(MiraiAdapter).call_api(command, sub_command, **content)
        )


class BotClient(Client):
    logger = get_logger('botClient', LogLevel.DEBUG)  # TODO bot使用另外的logger

    def __init__(self):
        super().__init__('bot')

    def init_bot_proxy(self, bot: Bot, event_loop: asyncio.AbstractEventLoop):
        self.bot_proxy = BotProxy(bot, event_loop)


bot_client = BotClient()


def get_bot_client() -> BotClient:
    return bot_client  # TODO 离线版
