"""服务端和客户端共用的东西"""
import socket

HOST = socket.gethostname()
PORT = 9999
ENCODING = 'utf-8'


def send_msg(sock, s: str) -> None:
    msg = s.encode(ENCODING)
    sock.sendall(f'{len(msg):05d}'.encode(ENCODING))
    sock.sendall(msg)


def recv_msg(sock) -> str:
    length = int(sock.recv(5).decode(ENCODING))
    return sock.recv(length).decode(ENCODING)

