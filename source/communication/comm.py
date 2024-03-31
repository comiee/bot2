"""服务端和客户端共用的东西"""
from public.utils import local_ip
from asyncio import StreamReader, StreamWriter
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


async def async_send_msg(writer: StreamWriter, s: str) -> None:
    msg = s.encode(ENCODING)
    length = str(len(msg)).encode(ENCODING)
    n = f'{len(length):05d}'.encode(ENCODING)
    writer.write(n)
    writer.write(length)
    writer.write(msg)
    await writer.drain()


async def async_recv_msg(reader: StreamReader) -> str:
    s = (await reader.read(5)).decode(ENCODING)
    if s == '':
        raise ConnectionError()
    n = int(s)
    length = int((await reader.read(n)).decode(ENCODING))
    return (await reader.read(length)).decode(ENCODING)
