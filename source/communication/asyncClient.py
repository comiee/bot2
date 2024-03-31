from communication.comm import *
import asyncio

__all__ = ['AsyncClient']


class AsyncClient:
    def __init__(self, cmd):
        self.__cmd = cmd
        self.__reader: asyncio.StreamReader | None = None
        self.__writer: asyncio.StreamWriter | None = None

    async def _connection(self):
        self.__reader, self.__writer = await asyncio.open_connection(HOST, PORT)

    async def __aenter__(self):
        await self._connection()
        await self.send(self.__cmd)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__writer is not None:
            self.__writer.close()
            await self.__writer.wait_closed()
        self.__reader = None
        self.__writer = None

    async def send(self, msg: str):
        await async_send_msg(self.__writer, msg)
        return await async_recv_msg(self.__reader)
