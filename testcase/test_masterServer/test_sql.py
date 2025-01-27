from masterServer.comm.sql import sql
import unittest


class SqlTestCase(unittest.TestCase):
    def test_reconnect(self):
        print(sql.query('select * from info where qq=0'))
        print(sql.query('select * from info where qq=0'))

# TODO 增加sql操作相关（金币操作等）的用例
# TODO chat功能的用例
