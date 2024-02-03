from masterServer.module.momo_calendar import momo_calendar
import unittest


class MomoCalendarTestCase(unittest.TestCase):
    def test_generate(self):
        path = momo_calendar()
        with open(path, encoding='utf-8') as f:
            self.assertNotEqual('', f.read())


if __name__ == '__main__':
    unittest.main()
