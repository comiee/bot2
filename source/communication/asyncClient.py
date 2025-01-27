from comiee import TaskList
from communication.asyncComm import *
from public.log import async_client_logger
from public.exception import CustomException
import asyncio

__all__ = ['AsyncClient']


class AsyncClient:
    def __init__(self, cmd: str, loop: asyncio.AbstractEventLoop = None):
        self.__cmd = cmd
        self.__reader: asyncio.StreamReader | None = None
        self.__writer: asyncio.StreamWriter | None = None
        self.__task_list = TaskList(loop or asyncio.get_event_loop())

    async def _connection(self):
        async_client_logger.debug(f'异步客户端{self.__cmd}正在连接服务器')
        while True:
            try:
                self.__reader, self.__writer = await asyncio.open_connection(HOST, ASYNC_PORT)
            except Exception:
                continue
            else:
                break

    async def __aenter__(self):
        await self._connection()
        ret = await self.send(self.__cmd)
        if ret != 'success':
            await self.__aexit__(None, None, None)
            raise CustomException(f'异步客户端{self.__cmd}出错：服务器未注册的命令字')
        addr = self.__writer.get_extra_info('peername')
        async_client_logger.debug(f'异步客户端{self.__cmd}建立连接：{addr}')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__task_list.wait()
        if self.__writer is not None:
            self.__writer.close()
            await self.__writer.wait_closed()
        self.__reader = None
        self.__writer = None
        async_client_logger.debug(f'异步客户端{self.__cmd}已关闭连接')

    async def send(self, obj):
        async_client_logger.debug(f'异步客户端{self.__cmd}向服务器发送消息：{obj}')
        await async_send(self.__writer, obj)

        ret = await async_recv(self.__reader)
        async_client_logger.debug(f'异步客户端{self.__cmd}收到服务器响应：{ret}')
        return ret

    def add_task(self, co):
        return self.__task_list.add_task(co)
