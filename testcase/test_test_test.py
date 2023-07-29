from unittest import mock
import unittest
from test_test import *

class TestTestCase(unittest.TestCase):
    #@mock.patch('test_test.User')
    def test_test(self):
        coin = 233

        def query():
            print('query mock')
            return coin

        def gain(num: int):
            nonlocal coin
            print('gain mock')
            coin += num

        with mock.patch('test_test.User') as user_cls_mock:
            user_mock=mock.Mock()
            user_cls_mock.return_value=user_mock
            user_mock.query.side_effect=query
            user_mock.gain.side_effect = gain

            session = Session()
            #session.user.query.return_value = coin
            session.user.gain(-10)
            self.assertEqual(223, session.user.query())


if __name__ == '__main__':
    unittest.main()
