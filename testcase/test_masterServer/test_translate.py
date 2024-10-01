from masterServer.module.translate import translate
import unittest


class TranslateTestCase(unittest.TestCase):
    def test_translate(self):
        self.assertEqual('robot', translate('中文', '英文', '机器人'))

    def test_multiple_lines(self):
        self.assertEqual('第一\n第二', translate('auto', 'zh', 'first\nsecond'))


if __name__ == '__main__':
    unittest.main()
