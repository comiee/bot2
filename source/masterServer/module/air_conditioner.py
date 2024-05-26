from comiee import Singleton
from communication.asyncServer import AsyncServer
from masterServer.comm.sql import sql
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


def bytes_to_hex_str(b: bytes) -> str:
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
        assert ret == wish, f'返回值校验失败，预期{bytes_to_hex_str(wish)}，实际{bytes_to_hex_str(ret)}'

    async def wait_and_check(self, timeout: int, wish: bytes) -> None:
        ret = await self.wait(len(wish), timeout)
        assert ret == wish, f'接收值校验失败，预期{bytes_to_hex_str(wish)}，实际{bytes_to_hex_str(ret)}'


class TTLSerialIR03T(TTLSerial):
    async def learn_cmd(self, index: int) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        await self.send_and_check(bytes([0xFA, 0xFD, 0x01, index, 0xDF]), bytes([0xA1]))
        await self.wait_and_check(30, bytes([0xA2]))
        await asyncio.sleep(1)  # 等待指令执行完成

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
            f'读取到的数据格式不对，数据为{bytes_to_hex_str(res)}'
        return res[4:-2]

    async def write_cmd(self, index: int, data: bytes) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        assert len(data) == 230, f'写入数据的长度应该为230，当前为{len(data)}'
        await self.send_and_check(bytes([0xFA, 0xFD, 0x07, index, *data, 0xDF, 0xDF]), bytes([0xA7]))
        res = await self.read_cmd(index)
        assert res == data, f'回读校验失败，写入数据为{bytes_to_hex_str(data)}，读出数据为{bytes_to_hex_str(res)}'


class AirConditioner(Singleton):
    def append_sql(self, index: int, cmd: str, data: bytes) -> None:
        sql.execute('insert into air_conditioner(`index`,cmd,data) values(%s,%s,%s);', (index, cmd, data))

    def find_index(self, cmd: str) -> int:
        index = sql.query(f'select `index` from air_conditioner where cmd="{cmd}";')
        assert index is not None
        return index

    def get_next_index(self) -> int:
        return sql.query('select count(*) from air_conditioner;') + 0x10

    async def learn(self, cmd: str) -> None:
        index = self.get_next_index()
        with TTLSerialIR03T() as ser:
            await ser.learn_cmd(index)
            data = await ser.read_cmd(index)
            self.append_sql(index, cmd, data)

    async def run(self, cmd: str) -> None:
        index = self.find_index(cmd)
        with TTLSerialIR03T() as ser:
            await ser.run_cmd(index)

    async def remove(self, cmd: str) -> None:
        index = self.find_index(cmd)
        with TTLSerialIR03T() as ser:
            await ser.remove_cmd(index)

    async def check(self) -> list[tuple[int, str, bytes]]:
        result = []
        for index, cmd, data in sql.query_all('select `index`,cmd,data from air_conditioner;'):
            with TTLSerialIR03T() as ser:
                if data != ser.read_cmd(index):
                    result.append((index, cmd, data))
        return result


@AsyncServer().register('air_conditioner_learn')
async def air_conditioner_learn(cmd: str) -> str:
    try:
        await AirConditioner().learn(cmd)
        return '命令学习成功'
    except Exception as e:
        return e.args[0]


@AsyncServer().register('air_conditioner_run')
async def air_conditioner_run(cmd: str) -> str:
    try:
        await AirConditioner().run(cmd)
        return '命令执行成功'
    except Exception as e:
        return e.args[0]


@AsyncServer().register('air_conditioner_remove')
async def air_conditioner_remove(cmd: str) -> str:
    try:
        await AirConditioner().remove(cmd)
        return '命令删除成功'
    except Exception as e:
        return e.args[0]


@AsyncServer().register('air_conditioner_check')
async def air_conditioner_check(_) -> str:
    try:
        result = await AirConditioner().check()
        if not result:
            return '检查完毕，所有命令均与数据库一致'
        else:
            return '检查完毕，以下数据与数据库不一致：\n' + \
                '\n'.join(f'{index}\t{cmd}\t{bytes_to_hex_str(data)}' for index, cmd, data in result)
    except Exception as e:
        return e.args[0]
