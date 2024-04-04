from communication.comm import *
from public.log import client_logger
import asyncio

__all__ = ['AsyncClient']


class AsyncClient:
    def __init__(self, cmd):
        self.__cmd = cmd
        self.__reader: asyncio.StreamReader | None = None
        self.__writer: asyncio.StreamWriter | None = None

    async def _connection(self):
        self.__reader, self.__writer = await asyncio.open_connection(HOST, ASYNC_PORT)

    async def __aenter__(self):
        await self._connection()
        await self.send(self.__cmd)
        addr = self.__writer.get_extra_info('peername')
        client_logger.debug(f'异步客户端{self.__cmd}建立连接：{addr}')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__writer is not None:
            self.__writer.close()
            await self.__writer.wait_closed()
        self.__reader = None
        self.__writer = None
        client_logger.debug(f'异步客户端{self.__cmd}已关闭连接')

    async def send(self, msg: str):
        client_logger.debug(f'异步客户端{self.__cmd}向服务器发送消息：{msg}')
        await async_send_msg(self.__writer, msg)
        ret = await async_recv_msg(self.__reader)
        client_logger.debug(f'异步客户端{self.__cmd}收到服务器响应：{ret}')
        return ret
