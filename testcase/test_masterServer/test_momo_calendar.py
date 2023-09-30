from masterServer.module.momo_calendar import momo_calendar
import unittest


class MomoCalendarTestCase(unittest.TestCase):
    def test_generate(self):
        result = momo_calendar()
        print(result)
        self.assertNotEquals('', result)


if __name__ == '__main__':
    unittest.main()
