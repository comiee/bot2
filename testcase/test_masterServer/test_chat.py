from masterServer.module.chat import chat
import unittest
import time


class TranslateTestCase(unittest.TestCase):
    def test_normal(self):
        self.assertEqual('我的主人最帅！', chat(0, 0, '最帅'))

    def test_random_choice(self):
        result = [chat(0, 0, '你几岁') for _ in range(20)]
        self.assertIn('女孩子的年龄是秘密哦', result)
        self.assertIn('问女孩子年龄是很不礼貌的哦', result)
        self.assertIn('打听女孩子的年龄是不礼貌的行为', result)

    def test_random_report(self):
        result = [chat(0, 0, '名字') for _ in range(20)]
        self.assertIn('我的名字是小魅。', result)
        self.assertIn('', result)

    def test_time_limit(self):
        # 因为会强制中断子线程，这个用例出现 WARNING: 匹配模板时发生错误 是正常现象
        start = time.time()
        self.assertEqual('执行超时', chat(0, 0, '999999**999999'))
        end = time.time()
        print(end - start)
        self.assertLess(end - start, 5)  # 虽然chat函数的限制时间是1秒，但是实际执行时间会花3秒多


if __name__ == '__main__':
    unittest.main()
