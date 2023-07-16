from communication.comm import *
from communication import message
from tools.log import get_logger, LogLevel
from tools.exception import MessageException, InteractException
import socket
from threading import Thread

__all__ = ['Server']

logger = get_logger('server', LogLevel.INFO, LogLevel.DEBUG)


class Server:
    def __init__(self):
        # 创建 socket 对象
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定端口号
        self.sock.bind((HOST, PORT))
        # 设置最大连接数，超过后排队
        self.sock.listen(32)

        # 保存注册的客户端
        self.client_dict = {}

    def send_to(self, client_name: str, msg: str):
        if client_name not in self.client_dict:
            raise InteractException('发送失败：未注册的客户端')
        if 'receiver' not in self.client_dict[client_name]:
            raise InteractException('发送失败：客户端无接收器')
        client = self.client_dict[client_name]['receiver']
        send_msg(client, msg)
        logger.debug(f'服务器发送消息到客户端[{client_name}]：{msg}')
        ret = message.result_msg.parse(recv_msg(client))
        logger.debug(f'服务器收到客户端[{client_name}]回响应：{ret}')
        return ret

    def register_client(self, client_name, client_type, sock):
        self.client_dict.setdefault(client_name, {})[client_type] = sock
        logger.info(f'客户端[{client_name}]注册{client_type}')

    def listen_client(self, client, name):
        while True:
            msg = recv_msg(client)
            logger.debug(f'服务器收到客户端[{name}]的消息：{msg}')
            try:
                ret = message.Message.parse(msg)
                logger.debug(f'服务器向客户端[{name}]回响应：{ret}')
                send_msg(client, message.result_msg.build(ret))
            except MessageException as e:
                logger.error(e.args[0])

    def accept_client(self, client, addr):
        logger.info("连接地址: %s" % str(addr))
        # 第一条消息为注册消息
        msg = recv_msg(client)
        msg_dict = message.register_msg.parse(msg)  # 解析消息可能出错，如果在注册阶段出错，此线程抛异常终止，不会影响其他线程
        name, client_type = msg_dict['name'], msg_dict['client_type']
        self.register_client(name, client_type, client)

        if client_type == 'sender':
            self.listen_client(client, name)

    def run(self):
        while True:
            # 建立客户端连接
            Thread(target=self.accept_client, args=self.sock.accept()).start()
