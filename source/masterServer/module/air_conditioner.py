from comiee import Singleton
from communication.asyncServer import AsyncServer
from public.log import master_server_logger
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
    return '<' + ' '.join(f'{c:X}' for c in b) + '>'


class TTLSerial(Serial):
    def __init__(self, port: str = None, baud_rate: int = BAUD_RATE, timeout=1):
        if port is None:
            port = find_one_port(PORT_KEY)
        super().__init__(port, baud_rate, timeout=timeout)

    def __enter__(self):
        super().__enter__()
        assert self.is_open, f'打开串口{self.port}失败'
        return self

    def send(self, data: bytes) -> bytes:
        self.write(data)
        return self.read(MAX_READ_SIZE)

    def send_and_check(self, data: bytes, wish: bytes) -> None:
        self.write(data)
        ret = self.read(len(wish))
        assert ret == wish, f'返回值校验失败，预期{bytes_to_hex_str(wish)}，实际{bytes_to_hex_str(ret)}'

    async def wait(self, timeout: int) -> bytes:
        for _ in range(timeout):
            ret = self.read(MAX_READ_SIZE)
            if ret:
                return ret
            await asyncio.sleep(1)
        return bytes()

    async def wait_for(self, wish: bytes, timeout: int):
        for _ in range(timeout):
            ret = self.read(len(wish))
            if ret == wish:
                return
            if ret:
                master_server_logger.warning(f'air_conditioner等待期间读取到了预期外的结果{bytes_to_hex_str(ret)}')
            await asyncio.sleep(1)


class TTLSerialIR03T(TTLSerial):
    async def learn_cmd(self, index: int) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        self.send_and_check(bytes([0xFA, 0xFD, 0x01, index, 0xDF]), bytes([0xA1]))
        await self.wait_for(bytes([0xA2]), 120)

    def run_cmd(self, index: int) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        self.send_and_check(bytes([0xFA, 0xFD, 0x02, index, 0xDF]), bytes([0xF1]))

    def remove_cmd(self, index: int) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        self.send_and_check(bytes([0xFA, 0xFD, 0x05, index, 0xDF]), bytes([0xA5]))

    def read_cmd(self, index: int) -> bytes:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        res = self.send(bytes([0xFA, 0xFD, 0x06, index, 0xDF]))
        assert len(res) == 236 and res[:4] == bytes([0xFA, 0xFD, 0x07, index]) and res[-2:] == bytes([0xDF, 0xDF]), \
            f'读取到的数据格式不对，数据为{bytes_to_hex_str(res)}'
        return res[4:-2]

    def write_cmd(self, index: int, data: bytes) -> None:
        assert 0 <= index <= 0xFE, f'index的范围为[0x00,0xFE]，当前为{index}'
        assert len(data) == 230, f'写入数据的长度应该为230，当前为{len(data)}'
        self.send_and_check(bytes([0xFA, 0xFD, 0x07, index, *data, 0xDF, 0xDF]), bytes([0xA7]))
        res = self.read_cmd(index)
        assert res == data, f'回读校验失败，写入数据为{data}，读出数据为{res}'


class AirConditioner(Singleton):
    def append_sql(self, index: int, cmd: str, data: bytes) -> None:
        sql.execute('insert into air_conditioner(index,cmd,data) values(%d,%s,%s);', (index, cmd, data))

    def get_next_index(self) -> int:
        return sql.query('select count(*) from air_conditioner;') + 0x10

    async def learn(self, cmd: str):
        index = self.get_next_index()
        with TTLSerialIR03T() as ser:
            await ser.learn_cmd(index)
            data = ser.read_cmd(index)
            self.append_sql(index, cmd, data)

    def run(self, cmd: str):
        index = sql.query(f'sql select `index` from air_conditioner where cmd={cmd};', default=0)
        with TTLSerialIR03T() as ser:
            ser.run_cmd(index)


# TODO 写入数据库或文件（考虑到格式更像表格，优先使用数据库），自动生成索引（从0x10开始，防止按到学习键导致命令被覆盖）
#  需要记录的数据：命令对应的索引、命令对应的中文字符串、编码数据备份
#  添加检查功能，检查单板中的编码数据与电脑中记录的是否一致，不一致则想办法重录或者重新写入备份


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
        AirConditioner().run(cmd)
        return '命令执行成功'
    except Exception as e:
        return e.args[0]
