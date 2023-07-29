from public import messageDefine
from communication.comm import *
from communication import message
from public.log import server_logger
from public.exception import MessageException
import socket
from threading import Thread

__all__ = ['Server']


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
        # json格式不能传输Ellipsis对象，用Ellipsis对象表示发送失败
        if client_name not in self.client_dict:
            server_logger.error(f'服务器向客户端[{client_name}]发送消息失败：未注册的客户端')
            return ...
        if 'receiver' not in self.client_dict[client_name]:
            server_logger.error(f'服务器向客户端[{client_name}]发送消息失败：客户端无接收器')
            return ...
        client = self.client_dict[client_name]['receiver']
        try:
            send_msg(client, msg)
            server_logger.debug(f'服务器发送消息到客户端[{client_name}]：{msg}')
            ret = messageDefine.result_msg.parse(recv_msg(client))
            server_logger.debug(f'服务器收到客户端[{client_name}]回响应：{ret}')
            return ret
        except ConnectionError as e:
            server_logger.error(f'服务器向客户端[{client_name}]发送消息失败，即将断开连接：{e}')
            del self.client_dict[client_name]['receiver']
            return ...

    def send_to_all(self, msg: str):
        for name in self.client_dict:
            self.send_to(name, msg)

    def register_client(self, client_name, client_type, sock):
        self.client_dict.setdefault(client_name, {})[client_type] = sock
        server_logger.info(f'客户端[{client_name}]注册{client_type}')

    def listen_client(self, client, name):
        while True:
            try:
                msg = recv_msg(client)
                server_logger.debug(f'服务器收到客户端[{name}]的消息：{msg}')
                ret = message.Message.parse(msg)
                server_logger.debug(f'服务器向客户端[{name}]回响应：{ret}')
                send_msg(client, messageDefine.result_msg.build(ret))
            except MessageException as e:
                server_logger.error(f'服务器解析客户端[{name}]消息失败：{e.args[0]}')
            except ConnectionError as e:
                server_logger.error(f'服务器接收客户端[{name}]消息失败，即将断开连接：{e}')
                break

    def accept_client(self, client, addr):
        server_logger.info("连接地址: %s" % str(addr))
        # 第一条消息为注册消息
        msg = recv_msg(client)
        msg_dict = messageDefine.register_msg.parse(msg)  # 解析消息可能出错，如果在注册阶段出错，此线程抛异常终止，不会影响其他线程
        name, client_type = msg_dict['name'], msg_dict['client_type']
        self.register_client(name, client_type, client)

        if client_type == 'sender':
            self.listen_client(client, name)

    def run(self):
        while True:
            try:
                # 建立客户端连接
                Thread(target=self.accept_client, args=self.sock.accept()).start()
            except BlockingIOError:
                self.sock.close()
                server_logger.warning('已关闭服务器')
                break

    def close(self):
        self.sock.setblocking(False)
        for client_name in self.client_dict:
            for client_type, client in self.client_dict[client_name].items():
                server_logger.warning(f'正在断开与客户端[{client_name}]{client_type}的连接')
                client.close()
