from communication.comm import *
from communication import message
from tools.log import get_logger, LogLevel
from tools.exception import MessageException
import socket
from threading import Thread

__all__ = ['Client']

logger = get_logger('client', LogLevel.INFO, 'client.txt', LogLevel.DEBUG)


class Client:
    def __init__(self, name):
        self.name = name
        self.sender = self.register('sender')

    def register(self, client_type):
        # 创建 socket 对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 连接服务，指定主机和端口
        while sock.connect_ex((HOST, PORT)):
            pass

        send_msg(sock, message.register_msg.build(name=self.name, client_type=client_type))
        logger.info(f'客户端[{self.name}] {client_type} 成功连接服务器')
        return sock

    def send(self, msg: str):
        send_msg(self.sender, msg)
        logger.debug(f'客户端[{self.name}]发送消息到服务器：{msg}')
        ret = message.result_msg.parse(recv_msg(self.sender))
        logger.debug(f'客户端[{self.name}]收到服务器回响应：{ret}')
        return ret

    def listen_server(self):
        receiver = self.register('receiver')
        while True:
            msg = recv_msg(receiver)
            logger.debug(f'客户端[{self.name}]收到服务器的消息：{msg}')
            try:
                ret = message.Message.parse(receiver, msg)
                logger.debug(f'客户端[{self.name}]向服务器回响应：{ret}')
                send_msg(receiver, message.result_msg.build(ret))
            except MessageException as e:
                logger.error(e.args[0])
