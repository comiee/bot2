from masterServer.module.air_conditioner import TTLSerialIR03T, bytes_hex
import unittest


class AirConditionerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_read(self):
        with TTLSerialIR03T() as ser:
            res = ser.read_cmd(5)
            print(bytes_hex(res))

    async def test_learn(self):
        with TTLSerialIR03T() as ser:
            await ser.learn_cmd(5)
            data = ser.read_cmd(5)
            print(data)

    def test_run(self):
        with TTLSerialIR03T() as ser:
            ser.run_cmd(5)

    def test_remove(self):
        with TTLSerialIR03T() as ser:
            ser.remove_cmd(5)
