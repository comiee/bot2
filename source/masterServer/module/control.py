from communication.asyncServer import AsyncServer
from public.message import send_qq_text_msg
from masterServer.masterServer import get_master_server
import asyncio


@AsyncServer().register('debug')
async def debug(send, recv):
    try:
        while True:
            s = await recv()
            print(f'收到：{s}')
            if s.isdigit():
                await asyncio.sleep(int(s))
            await send(s)
            print(f'发送：{s}')
    except ConnectionError:
        pass


@send_qq_text_msg.on_receive
def send_qq_text(user_id, text):
    ret = get_master_server().send_to('bot', send_qq_text_msg.build(user_id=user_id, text=text))
    return False if ret is ... else ret
