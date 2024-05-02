from masterServer.module.momo_calendar import CalendarBrowser
import unittest
import os


class MomoCalendarTestCase(unittest.TestCase):
    def test_generate(self):
        CalendarBrowser.generate()
        self.assertFalse(CalendarBrowser.need_update())
        with open(CalendarBrowser.ICS_PATH, encoding='utf-8') as f:
            self.assertNotEqual('', f.read())

    def test_need_update(self):
        if os.path.exists(CalendarBrowser.ICS_PATH):
            os.remove(CalendarBrowser.ICS_PATH)
        self.assertTrue(CalendarBrowser.need_update())
        with getattr(CalendarBrowser, '_CalendarBrowser__update_lock'):
            self.assertFalse(CalendarBrowser.need_update())


if __name__ == '__main__':
    unittest.main()
