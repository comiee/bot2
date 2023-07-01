from communication.comm import *
from communication import message
from tools.log import get_logger, LogLevel
import socket
from threading import Thread

__all__ = ['Client']

logger = get_logger('client', LogLevel.DEBUG)


class Client:
    def __init__(self, name):
        self.name = name
        # 创建 socket 对象
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 连接服务，指定主机和端口
        while self.sock.connect_ex((HOST, PORT)):
            pass

        self.send(message.register_msg.build(name=self.name))

    def send(self, s: str):
        send_msg(self.sock, s)

    def run(self):
        while True:
            msg = recv_msg(self.sock)
            logger.debug(f'客户端[{self.name}]收到服务器的消息：' + msg)
            try:
                message.Message.parse(self.sock, msg)
            except Exception as e:
                logger.error(e.args[0])


if __name__ == '__main__':
    client = Client('test')
    Thread(target=client.run).start()
    while True:
        client.send(message.debug_msg.build(string=input()))
