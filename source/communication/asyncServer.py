from comiee import Singleton
from communication.comm import *
from public.log import server_logger
from functools import partial
from inspect import signature
import asyncio

__all__ = ['AsyncServer']


class AsyncServer(Singleton):
    def __init__(self):
        self.__cmd_dict: dict = {}

    async def run(self):
        self.__server = await asyncio.start_server(self.__handle_client, HOST, ASYNC_PORT)

        addr = self.__server.sockets[0].getsockname()
        server_logger.info(f'异步服务器已开启：{addr}')

        async with self.__server:
            try:
                await self.__server.serve_forever()
            except asyncio.CancelledError:
                server_logger.info('异步服务器已关闭')

    async def __handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        cmd = await async_recv_msg(reader)
        await async_send_msg(writer, 'success')
        server_logger.debug(f'异步服务器建立连接：{addr} {cmd}')

        if cmd not in self.__cmd_dict:
            server_logger.error(f'异步服务器：未知的命令字：{cmd}')
            return
        send = partial(async_send_msg, writer)
        recv = partial(async_recv_msg, reader)
        handler = self.__cmd_dict[cmd]
        if len(signature(handler).parameters) == 1:
            msg = await recv()
            ret = await handler(msg)
            await send(ret)
        else:
            await handler(send, recv)
        writer.close()
        await writer.wait_closed()

    async def close(self):
        self.__server.close()
        await self.__server.wait_closed()

    def register(self, cmd):
        def get_receiver(handler):
            if cmd in self.__cmd_dict:
                server_logger.error(f'异步服务器：重复注册：{cmd}')
            self.__cmd_dict[cmd] = handler

        return get_receiver
