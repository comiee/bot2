"""服务端和客户端共用的东西"""
from public.utils import local_ip
from socket import socket

HOST = local_ip()
PORT = 9999
ENCODING = 'utf-8'

RECONNECT_TIME = 3  # 连接失败后的重连等待时间


def send_msg(sock: socket, s: str) -> None:
    msg = s.encode(ENCODING)
    length = str(len(msg)).encode(ENCODING)
    n = f'{len(length):05d}'.encode(ENCODING)
    sock.sendall(n)
    sock.sendall(length)
    sock.sendall(msg)


def recv_msg(sock: socket) -> str:
    s = sock.recv(5).decode(ENCODING)
    if s == '':
        raise ConnectionError()
    n = int(s)
    length = int(sock.recv(n).decode(ENCODING))
    return sock.recv(length).decode(ENCODING)
