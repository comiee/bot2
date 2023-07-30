from public import message
from communication.comm import *
from public.log import client_logger
from public.exception import MessageException
import socket

__all__ = ['Client']


class Client:
    def __init__(self, name):
        self.name = name
        self.sender = self.register('sender')
        self.receiver = None

    def register(self, client_type):
        client_logger.info(f'客户端[{self.name}]正在向服务器注册{client_type}')
        # 创建 socket 对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接服务，指定主机和端口
        while sock.connect_ex((HOST, PORT)):
            pass

        send_msg(sock, message.register_msg.build(name=self.name, client_type=client_type))
        client_logger.info(f'客户端[{self.name}] {client_type} 成功连接服务器')
        return sock

    def send(self, msg: str):
        try:
            send_msg(self.sender, msg)
            client_logger.debug(f'客户端[{self.name}]发送消息到服务器：{msg}')
            ret = message.result_msg.parse(recv_msg(self.sender))
            client_logger.debug(f'客户端[{self.name}]收到服务器回响应：{ret}')
            return ret
        except ConnectionError as e:
            client_logger.error(f'客户端[{self.name}]发送消息失败，即将重连：{e}')
            self.sender = self.register('sender')
            self.send(msg)

    def listen_server(self):
        self.receiver = self.register('receiver')
        while True:
            try:
                msg = recv_msg(self.receiver)
                client_logger.debug(f'客户端[{self.name}]收到服务器的消息：{msg}')
                ret = message.Message.parse(msg)
                client_logger.debug(f'客户端[{self.name}]向服务器回响应：{ret}')
                send_msg(self.receiver, message.result_msg.build(ret))
            except MessageException as e:
                client_logger.error(f'客户端[{self.name}]解析服务器消息失败：{e.args[0]}')
            except ConnectionError as e:
                client_logger.error(f'客户端[{self.name}]接受消息失败，即将重连：{e}')
                self.receiver = self.register('receiver')

    def close(self):
        self.sender.close()
        if self.receiver is not None:
            self.receiver.close()
