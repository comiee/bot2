from masterServer.module.air_conditioner import TTLSerialIR03T, bytes_hex, AirConditioner, sql
import unittest


class AirConditionerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_read(self):
        with TTLSerialIR03T() as ser:
            res = await ser.read_cmd(5)
            print(bytes_hex(res))

    async def test_learn(self):
        with TTLSerialIR03T() as ser:
            await ser.learn_cmd(5)
            data = await ser.read_cmd(5)
            print(data)

    async def test_run(self):
        with TTLSerialIR03T() as ser:
            await ser.run_cmd(5)

    async def test_remove(self):
        with TTLSerialIR03T() as ser:
            await ser.remove_cmd(5)

    async def test_next_index(self):
        count = sql.query('select count(*) from air_conditioner;')
        indexes = sql.query_col('select `index` from air_conditioner;')
        self.assertEqual(count, len(indexes))
        next_index = AirConditioner().get_next_index()
        print(next_index, indexes)
        self.assertNotIn(next_index, indexes)
        self.assertTrue(0x10 <= next_index < 0xFF)

    async def test_cannot_find(self):
        err = ''
        try:
            AirConditioner().find_index('test')
        except Exception as e:
            err = e.args[0]
        self.assertEqual("未找到此命令，当前已学习的命令：('关机', '制冷', '制冷26', '制热', '自动', '除湿')", err)
