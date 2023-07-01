from communication.comm import *
from communication import message
from tools.log import get_logger, LogLevel
import socket
from threading import Thread

__all__ = ['Server', 'send_to']

logger = get_logger('server', LogLevel.DEBUG)

# 保存注册的客户端
client_dict = {}


@message.register_msg.on_receive
def _register_client(sock, name):
    client_dict[name] = sock
    return name


def get_client(name: str):
    return client_dict[name]


def send_to(client_name: str, s: str):
    send_msg(get_client(client_name), s)


class Server:
    def __init__(self):
        # 创建 socket 对象
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定端口号
        self.sock.bind((HOST, PORT))
        # 设置最大连接数，超过后排队
        self.sock.listen(32)

    @staticmethod
    def listen_client(client, addr):
        logger.info("连接地址: %s" % str(addr))
        # 第一条消息为注册消息
        msg = recv_msg(client)
        client_name = message.register_msg.parse(client, msg)  # 解析消息可能出错，如果在注册阶段出错，此线程抛异常终止，不会影响其他线程

        while True:
            msg = recv_msg(client)
            logger.debug(f'服务器收到客户端[{client_name}]的消息：' + msg)
            try:
                message.Message.parse(client, msg)
            except Exception as e:
                logger.error(e.args[0])

    def run(self):
        while True:
            # 建立客户端连接
            Thread(target=self.listen_client, args=self.sock.accept()).start()


if __name__ == '__main__':
    server = Server()
    Thread(target=server.run).start()
    while True:
        send_to('test', message.debug_msg.build(string=input()))
        send_to('test2', message.debug_msg.build(string=input()))
