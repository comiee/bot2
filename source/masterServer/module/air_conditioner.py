from comiee import Singleton
from communication.asyncServer import AsyncServer
from masterServer.comm.TTLSerial import TTLSerialIR03T, bytes_hex
from masterServer.comm.sql import sql


class AirConditioner(Singleton):
    def append_sql(self, index: int, cmd: str, data: bytes) -> None:
        old = sql.query(f'select `index` from air_conditioner where `index`={index}')
        assert old is None, f'添加sql失败，重复的索引：{index}'
        sql.execute('insert into air_conditioner(`index`,cmd,data) values(%s,%s,%s);', (index, cmd, data))

    def find_index(self, cmd: str) -> int:
        index = sql.query(f'select `index` from air_conditioner where cmd="{cmd}";')
        cmds = sql.query_col(f"select cmd from air_conditioner;")
        assert index is not None, f'未找到此命令，当前已学习的命令：{cmds}'
        return index

    def get_next_index(self) -> int:
        indexes = set(sql.query_col('select `index` from air_conditioner;'))
        for i in range(0x10, 0xFF):
            if i not in indexes:
                return i

    async def learn(self, cmd: str) -> None:
        cmds = sql.query_col(f"select cmd from air_conditioner;")
        assert cmd not in cmds, f'已有同名命令，当前已学习的命令：{cmds}'
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

    async def check(self) -> list[tuple[int, str, bytes, bytes]]:
        result = []
        for index, cmd, data in sql.query_all('select `index`,cmd,data from air_conditioner;'):
            with TTLSerialIR03T() as ser:
                ret = await ser.read_cmd(index)
                if data != ret:
                    result.append((index, cmd, data, ret))
        return result


@AsyncServer().register('air_conditioner_learn')
async def air_conditioner_learn(cmd: str) -> str:
    try:
        await AirConditioner().learn(cmd)
        return '命令学习成功'
    except Exception as e:
        return str(e)


@AsyncServer().register('air_conditioner_run')
async def air_conditioner_run(cmd: str) -> str:
    try:
        await AirConditioner().run(cmd)
        return '命令执行成功'
    except Exception as e:
        return str(e)


@AsyncServer().register('air_conditioner_remove')
async def air_conditioner_remove(cmd: str) -> str:
    try:
        await AirConditioner().remove(cmd)
        return '命令删除成功'
    except Exception as e:
        return str(e)


@AsyncServer().register('air_conditioner_check')
async def air_conditioner_check(_) -> str:
    try:
        result = await AirConditioner().check()
        if not result:
            return '检查完毕，所有命令均与数据库一致'
        else:
            return '检查完毕，以下数据与数据库不一致：\n' + \
                '\n'.join(f'{index}\t{cmd}\t{bytes_hex(data)}\t{bytes_hex(ret)}' for index, cmd, data, ret in result)
    except Exception as e:
        return str(e)
