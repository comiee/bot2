from communication.comm import *
from communication.message import Message, register_msg, result_msg
from public.log import server_logger
from public.exception import MessageException
from threading import Thread
import socket

__all__ = ['Server']


class Server:
    def __init__(self):
        # 创建 socket 对象
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定端口号
        self.__sock.bind((HOST, PORT))
        # 设置最大连接数，超过后排队
        self.__sock.listen(32)

        # 保存注册的客户端
        self.__client_dict = {}

    def send_to(self, client_name: str, msg: str):
        # json格式不能传输Ellipsis对象，用Ellipsis对象表示发送失败
        if client_name not in self.__client_dict:
            server_logger.error(f'服务器向客户端[{client_name}]发送消息失败：未注册的客户端')
            return ...
        if 'receiver' not in self.__client_dict[client_name]:
            server_logger.error(f'服务器向客户端[{client_name}]发送消息失败：客户端无接收器')
            return ...
        client = self.__client_dict[client_name]['receiver']
        try:
            send_msg(client, msg)
            server_logger.debug(f'服务器发送消息到客户端[{client_name}]：{msg}')
            ret = result_msg.parse(recv_msg(client))
            server_logger.debug(f'服务器收到客户端[{client_name}]回响应：{ret}')
            return ret
        except ConnectionError as e:
            server_logger.error(f'服务器向客户端[{client_name}]发送消息失败，即将断开连接：{e}')
            del self.__client_dict[client_name]['receiver']
            return ...

    def send_to_all(self, msg: str):
        for name in self.__client_dict:
            self.send_to(name, msg)

    def __register_client(self, client_name, client_type, sock):
        self.__client_dict.setdefault(client_name, {})[client_type] = sock
        server_logger.info(f'客户端[{client_name}]注册{client_type}')

    def __listen_client(self, client, name):
        while True:
            try:
                msg = recv_msg(client)
                server_logger.debug(f'服务器收到客户端[{name}]的消息：{msg}')
                ret = Message.parse(msg)
                server_logger.debug(f'服务器向客户端[{name}]回响应：{ret}')
                send_msg(client, result_msg.build(ret))
            except MessageException as e:
                server_logger.error(f'服务器解析客户端[{name}]消息失败：{e.args[0]}')
            except ConnectionError as e:
                server_logger.error(f'服务器接收客户端[{name}]消息失败，即将断开连接：{e}')
                break

    def __accept_client(self, client, addr):
        server_logger.info("连接地址: %s" % str(addr))
        # 第一条消息为注册消息
        msg = recv_msg(client)
        name, client_type = register_msg.parse(msg)  # 解析消息可能出错，如果在注册阶段出错，此线程抛异常终止，不会影响其他线程
        self.__register_client(name, client_type, client)

        if client_type == 'sender':
            self.__listen_client(client, name)

    def run(self):
        server_logger.info('等待客户端连接……')
        while True:
            try:
                # 建立客户端连接
                Thread(target=self.__accept_client, args=self.__sock.accept()).start()
            except BlockingIOError:
                self.__sock.close()
                server_logger.warning('已关闭服务器')
                break

    def close(self):
        self.__sock.setblocking(False)
        for client_name in self.__client_dict:
            for client_type, client in self.__client_dict[client_name].items():
                server_logger.warning(f'正在断开与客户端[{client_name}]{client_type}的连接')
                client.close()
