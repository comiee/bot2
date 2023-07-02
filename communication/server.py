from communication.comm import *
from communication import message
from tools.log import get_logger, LogLevel
from tools.exception import MessageException, InteractException
import socket
from threading import Thread

__all__ = ['Server', 'send_to']

logger = get_logger('server', LogLevel.INFO, 'server.txt', LogLevel.DEBUG)

# 保存注册的客户端
client_dict = {}


@message.register_msg.on_receive
def _register(sock, name, client_type):
    client_dict.setdefault(name, {})[client_type] = sock
    logger.info(f'客户端[{name}]注册{client_type}')
    return name, client_type


def send_to(client_name: str, msg: str):
    if client_name not in client_dict:
        raise InteractException('发送失败：未注册的客户端')
    if 'receiver' not in client_dict[client_name]:
        raise InteractException('发送失败：客户端无接收器')
    client = client_dict[client_name]['receiver']
    send_msg(client, msg)
    logger.debug(f'服务器发送消息到客户端[{client_name}]：{msg}')
    ret = message.result_msg.parse(recv_msg(client))
    logger.debug(f'服务器收到客户端[{client_name}]回响应：{ret}')
    return ret


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
        name, client_type = message.register_msg.parse(client, msg)  # 解析消息可能出错，如果在注册阶段出错，此线程抛异常终止，不会影响其他线程
        if client_type != 'sender':
            return

        while True:
            msg = recv_msg(client)
            logger.debug(f'服务器收到客户端[{name}]的消息：{msg}')
            try:
                ret = message.Message.parse(client, msg)
                logger.debug(f'服务器向客户端[{name}]回响应：{ret}')
                send_msg(client, message.result_msg.build(ret))
            except MessageException as e:
                logger.error(e.args[0])

    def run(self):
        while True:
            # 建立客户端连接
            Thread(target=self.listen_client, args=self.sock.accept()).start()
