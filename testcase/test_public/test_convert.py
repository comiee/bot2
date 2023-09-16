from public.convert import convert_to
from alicebot.adapter.mirai.message import MiraiMessage, MiraiMessageSegment
import unittest


class ConvertTestCase(unittest.TestCase):
    def test_mirai_to_internal(self):
        self.assertEqual(
            '[at:12345]',
            convert_to('internal', MiraiMessageSegment.at(12345))
        )
        # TODO 补充其他type
        self.assertEqual(
            'abc',
            convert_to('internal', MiraiMessageSegment.plain('abc'))
        )
        self.assertEqual(
            '[left]at:12345[right]',
            convert_to('internal', MiraiMessageSegment.plain('[at:12345]'))
        )
        self.assertEqual(
            '[left][at:12345][right]',
            convert_to('internal', MiraiMessageSegment.plain('[') +
                       MiraiMessageSegment.at(12345) +
                       MiraiMessageSegment.plain(']'))
        )

    def test_internal_to_mirai(self):
        self.assertEqual(
            MiraiMessage(MiraiMessageSegment.at(12345)),
            convert_to('mirai', '[at:12345]')
        )
        # TODO 补充其他type
        self.assertEqual(
            MiraiMessage(MiraiMessageSegment.plain('abc')),
            convert_to('mirai', 'abc')
        )
        self.assertEqual(
            MiraiMessage(MiraiMessageSegment.at(12345)+
                         MiraiMessageSegment.plain('a[b]c')),
            convert_to('mirai', '[at:12345]a[left]b[right]c')
        )
        self.assertEqual(
            MiraiMessage(MiraiMessageSegment.plain('[at:12345]')),
            convert_to('mirai', '[left]at:12345[right]')
        )


if __name__ == '__main__':
    unittest.main()
