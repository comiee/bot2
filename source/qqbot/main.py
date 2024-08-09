from public.config import get_config
from public.log import qq_bot_logger
from qqbot.comm.Command import SingleCommand
import botpy
from botpy.message import GroupMessage, C2CMessage
from threading import Thread
import asyncio


class MyClient(botpy.Client):
    async def on_ready(self):
        qq_bot_logger.info(f"qqbot 「{self.robot.name}」 on_ready!")

    async def handle_message(self, message):
        content = message.content.strip()
        if content.startswith('/'):
            cmd, text, *_ = *content[1:].split(maxsplit=1), ''
            # TODO 当前仅考虑单次命令，后续添加其他命令的适配
            if command := SingleCommand.find(cmd):
                await command.handle(message, text)
                return
        # TODO chat

    async def on_group_at_message_create(self, message: GroupMessage):
        await self.handle_message(message)

    async def on_c2c_message_create(self, message: C2CMessage):
        await self.handle_message(message)


def run_qqbot():
    intents = botpy.Intents(public_messages=True)
    appid = get_config('qqbot', 'appid')
    secret = get_config('qqbot', 'secret')

    def run_client(is_sandbox):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = MyClient(intents=intents, is_sandbox=is_sandbox)
            client.run(appid=appid, secret=secret)
        except Exception as e:
            name = "沙箱" if is_sandbox else "正式"
            qq_bot_logger.error(f'qqbot 运行{name}环境出错：{e}')

    thread1 = Thread(target=run_client, args=(False,), daemon=True)
    thread2 = Thread(target=run_client, args=(True,), daemon=True)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
