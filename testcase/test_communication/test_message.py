from communication.server import Server
from communication.client import Client
from public.message import *
from public.currency import Currency
from public.log import server_logger, client_logger, LogLevel
from threading import Thread
import unittest
import time
import logging

server_logger.setLevel(LogLevel.DEBUG)
client_logger.setLevel(LogLevel.DEBUG)
for handler in server_logger.handlers:
    handler.setLevel(LogLevel.DEBUG)
for handler in client_logger.handlers:
    handler.setLevel(LogLevel.DEBUG)


class MyTestCase(unittest.TestCase):
    server = Server()
    client = Client('test')

    @classmethod
    def setUpClass(cls) -> None:
        Thread(target=cls.server.run, daemon=True).start()
        Thread(target=cls.client.listen_server, daemon=True).start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.close()
        cls.client.close()

    def test_multi_msg(self):
        # 此用例的目的在于验证多条消息同时发送时不会错乱，校验方式为运行过程不报错，不需要用assert系列方法
        self.test_debug()
        ts = [Thread(target=self.test_debug) for _ in range(30)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()

    def test_time(self):
        test_msg = Message('test', {}, None)

        @test_msg.on_receive
        def _():
            time.sleep(2)

        with self.assertLogs('public', logging.DEBUG) as cm:
            self.client.send(test_msg.build())

        self.assertIn('WARNING:public:命令字<test>执行回调函数时间过长', cm.output[0])

    def test_debug(self):
        result = self.client.send(debug_msg.build('test'))
        self.assertEqual('test', result)

    def test_big_msg(self):
        text = 'x' * 1000000
        result = self.server.send_to_all(debug_msg.build(text))
        for s in result.values():
            self.assertEqual(text, s)

    def test_chat(self):
        pass  # TODO

    def test_sql_query_currency(self):
        user_id_ = 233
        currency_ = Currency.coin.name
        result_ = 666

        @query_currency_msg.on_receive
        def _(user_id, currency):
            self.assertEqual(user_id_, user_id)
            self.assertEqual(currency_, currency)
            return result_

        result = self.client.send(query_currency_msg.build(
            user_id=user_id_,
            currency=currency_,
        ))
        self.assertEqual(result_, result)


if __name__ == '__main__':
    unittest.main()
