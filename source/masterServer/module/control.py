from communication.asyncServer import AsyncServer
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
