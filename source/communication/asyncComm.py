from communication.comm import *
from public.exception import CustomException
from asyncio import StreamReader, StreamWriter
import json
import pickle

ASYNC_PORT = 9998
PATCH_LEN = 1024


async def async_send_bytes(writer: StreamWriter, msg: bytes) -> None:
    length = str(len(msg)).encode(ENCODING)
    n = f'{len(length):05d}'.encode(ENCODING)
    writer.write(n)
    writer.write(length)
    writer.write(msg)
    await writer.drain()


async def async_send(writer: StreamWriter, obj) -> None:
    if isinstance(obj, str):
        await async_send_bytes(writer, b'str:' + obj.encode(ENCODING))
    elif isinstance(obj, dict):
        await async_send_bytes(writer, b'json:' + json.dumps(obj).encode(ENCODING))
    else:
        await async_send_bytes(writer, b'pickle:' + pickle.dumps(obj))


async def async_recv_bytes(reader: StreamReader) -> bytes:
    s = (await reader.read(5)).decode(ENCODING)
    if s == '':
        raise ConnectionError()
    n = int(s)
    length = int((await reader.read(n)).decode(ENCODING))
    return await reader.read(length)


async def async_recv(reader: StreamReader) -> str:
    msg = await async_recv_bytes(reader)
    type_, val = msg.split(b':', 1)
    if type_ == b'str':
        return val.decode(ENCODING)
    elif type_ == b'json':
        return json.loads(val.decode(ENCODING))
    elif type_ == b'pickle':
        return pickle.loads(val)
    else:
        raise CustomException('未知的消息类型')
