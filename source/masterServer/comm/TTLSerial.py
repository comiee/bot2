from serial import Serial
from serial.tools.list_ports import comports
import asyncio

PORT_KEY = 'SERIAL'
BAUD_RATE = 9600
MAX_READ_SIZE = 256


def find_all_ports(key: str) -> list[str]:
    return [port for port, name, *_ in comports() if key.lower() in name.lower()]


def find_one_port(key: str) -> str:
    ports = find_all_ports(key)
    assert len(ports) > 0, '未找到结果'
    assert len(ports) < 2, '找到多个结果'
    return ports[0]


def bytes_hex(b: bytes) -> str:
    return '<' + ' '.join(f'{c:02X}' for c in b) + '>'


class TTLSerial(Serial):
    def __init__(self, port: str = None, baud_rate: int = BAUD_RATE):
        if port is None:
            port = find_one_port(PORT_KEY)
        super().__init__(port, baud_rate, timeout=0)

    def __enter__(self):
        super().__enter__()
        assert self.is_open, f'打开串口{self.port}失败'
        return self

    async def wait(self, size=1, timeout=3) -> bytes:
        res = bytearray()
        for _ in range(timeout):
            buf = self.read(size)
            res.extend(buf)
            size -= len(buf)
            if size == 0:
                break
            await asyncio.sleep(1)
        return bytes(res)

    async def send(self, data: bytes) -> bytes:
        self.write(data)
        return await self.wait(MAX_READ_SIZE)

    async def send_and_check(self, data: bytes, wish: bytes) -> None:
        self.write(data)
        ret = await self.wait(len(wish))
        assert ret == wish, f'返回值校验失败，预期{bytes_hex(wish)}，实际{bytes_hex(ret)}'

    async def wait_and_check(self, timeout: int, wish: bytes) -> None:
        ret = await self.wait(len(wish), timeout)
        assert ret == wish, f'接收值校验失败，预期{bytes_hex(wish)}，实际{bytes_hex(ret)}'


class TTLSerialIR03T(TTLSerial):
    async def learn_cmd(self, index: int) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        await self.send_and_check(bytes([0xFA, 0xFD, 0x01, index, 0xDF]), bytes([0xA1]))
        await self.wait_and_check(30, bytes([0xA2]))

    async def run_cmd(self, index: int) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        await self.send_and_check(bytes([0xFA, 0xFD, 0x02, index, 0xDF]), bytes([0xF1]))

    async def remove_cmd(self, index: int) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        await self.send_and_check(bytes([0xFA, 0xFD, 0x05, index, 0xDF]), bytes([0xA5]))

    async def read_cmd(self, index: int) -> bytes:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        res = await self.send(bytes([0xFA, 0xFD, 0x06, index, 0xDF]))
        assert len(res) == 236 and res[:4] == bytes([0xFA, 0xFD, 0x07, index]) and res[-2:] == bytes([0xDF, 0xDF]), \
            f'读取到的数据格式不对，数据为{bytes_hex(res)}'
        return res[4:-2]

    async def write_cmd(self, index: int, data: bytes) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        assert len(data) == 230, f'写入数据的长度应该为230，当前为{len(data)}'
        await self.send_and_check(bytes([0xFA, 0xFD, 0x07, index, *data, 0xDF, 0xDF]), bytes([0xA7]))
        res = await self.read_cmd(index)
        assert res == data, f'回读校验失败，写入数据为{bytes_hex(data)}，读出数据为{bytes_hex(res)}'
