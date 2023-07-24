from robot.plugins.commandPlugin import CommandPlugin
from faker import *
import unittest

__import__('robot.plugins.test')


class CommandClassTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @async_test_case
    async def test_split(self):
        result = await dummy_friend_text(CommandPlugin, '/split 1 2')
        self.assertEqual("split x='1', y='2'", result)


if __name__ == '__main__':
    unittest.main()
