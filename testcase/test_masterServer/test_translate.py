from masterServer.module.translate import translate
import unittest


class TranslateTestCase(unittest.TestCase):
    def test_translate(self):
        self.assertEqual('robot', translate('中文', '英文', '机器人'))


if __name__ == '__main__':
    unittest.main()
