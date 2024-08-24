from comiee import Singleton, TaskList
from communication.asyncComm import *
from public.log import async_server_logger
from public.exception import CustomException
from functools import partial
from inspect import signature
import asyncio

__all__ = ['AsyncServer']


class AsyncServer(Singleton):
    def __init__(self):
        self.__cmd_dict = {}

    async def run(self):
        self.__server = await asyncio.start_server(self.__handle_client, HOST, ASYNC_PORT)
        self.__task_list = TaskList(self.__server.get_loop())

        addr = self.__server.sockets[0].getsockname()
        async_server_logger.info(f'异步服务器已开启：{addr}')

        async with self.__server:
            try:
                await self.__server.serve_forever()
            except asyncio.CancelledError:
                async_server_logger.info('异步服务器已关闭')

    async def __handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            addr = writer.get_extra_info('peername')
            cmd = await async_recv(reader)
            if cmd not in self.__cmd_dict:
                await async_send(writer, 'fail')
                raise CustomException(f'异步服务器：未知的命令字：{cmd}')
            await async_send(writer, 'success')
            async_server_logger.debug(f'异步服务器建立连接：{addr} {cmd}')

            send = partial(async_send, writer)
            recv = partial(async_recv, reader)
            handler = self.__cmd_dict[cmd]
            if len(signature(handler).parameters) == 1:
                msg = await recv()
                ret = await handler(msg)
                await send(ret)
            else:
                await handler(send, recv)
        except Exception as e:
            async_server_logger.exception(f'异步服务器出错：{e.args[0]}')
        finally:
            writer.close()
            await writer.wait_closed()

    async def close(self):
        await self.__task_list.wait()
        await asyncio.sleep(1)  # 需要多等一会，不然task的析构访问event_loop会出错
        self.__server.close()
        await self.__server.wait_closed()

    def wait_close(self):
        """用于在其他线程中等待异步服务器关闭"""
        asyncio.run_coroutine_threadsafe(AsyncServer().close(), AsyncServer().get_loop()).result()

    def register(self, cmd):
        def get_handler(handler):
            if cmd in self.__cmd_dict:
                raise CustomException(f'异步服务器：重复注册：{cmd}')
            self.__cmd_dict[cmd] = handler
            return handler

        return get_handler

    def add_task(self, co):
        return self.__task_list.add_task(co)

    def get_loop(self):
        return self.__server.get_loop()
