from communication.comm import *
from communication.message import Message, register_msg, result_msg
from public.log import client_logger
from public.exception import MessageException
import socket

__all__ = ['Client']


class Client:
    def __init__(self, name):
        self.__name = name
        self.__sender = None
        self.__receiver = None

    @property
    def name(self):
        return self.__name

    def __register(self, client_type):
        client_logger.info(f'客户端[{self.__name}]正在向服务器注册{client_type}')
        # 创建 socket 对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接服务，指定主机和端口
        while sock.connect_ex((HOST, PORT)):
            pass

        send_msg(sock, register_msg.build(name=self.__name, client_type=client_type))
        client_logger.info(f'客户端[{self.__name}] {client_type} 成功连接服务器')
        return sock

    def send(self, msg: str):
        if self.__sender is None:
            self.__sender = self.__register('sender')
        try:
            send_msg(self.__sender, msg)
            client_logger.debug(f'客户端[{self.__name}]发送消息到服务器：{msg}')
            ret = result_msg.parse(recv_msg(self.__sender))
            client_logger.debug(f'客户端[{self.__name}]收到服务器回响应：{ret}')
            return ret
        except ConnectionError as e:
            client_logger.error(f'客户端[{self.__name}]发送消息失败，即将重连：{e}')
            self.__sender = self.__register('sender')
            self.send(msg)

    def listen_server(self):
        self.__receiver = self.__register('receiver')
        while True:
            try:
                msg = recv_msg(self.__receiver)
                client_logger.debug(f'客户端[{self.__name}]收到服务器的消息：{msg}')
                ret = Message.parse(msg)
                client_logger.debug(f'客户端[{self.__name}]向服务器回响应：{ret}')
                send_msg(self.__receiver, result_msg.build(ret))
            except MessageException as e:
                client_logger.error(f'客户端[{self.__name}]解析服务器消息失败：{e.args[0]}')
            except ConnectionError as e:
                client_logger.error(f'客户端[{self.__name}]接受消息失败，即将重连：{e}')
                self.__receiver = self.__register('receiver')

    def close(self):
        if self.__sender is not None:
            self.__sender.close()
        if self.__receiver is not None:
            self.__receiver.close()
