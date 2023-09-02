from public.utils import load_module
from robot.comm.command import get_command_cls_list
import unittest
import os


class ShowBot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir('../source/robot')

        load_module('module')
        load_module('section')

    def test_show_command(self):
        temp = []
        for command_cls in get_command_cls_list():
            for command in command_cls.commands:
                temp.append(repr(command))
        print('\n'.join(temp))

if __name__ == '__main__':
    unittest.main()