import unittest
import os


class Path(os.PathLike):
    def __fspath__(self):
        return '/'.join(self.dirs)

    def __init__(self, *dirs):
        self.dirs = list(dirs)

    def __add__(self, other):
        return Path(*self.dirs, other)

    def __str__(self):
        return '.'.join(filter('.'.__ne__, self.dirs))


def find_test_file(path: Path | None):
    for name in os.listdir(path):
        sub_path = path + name
        if os.path.isdir(sub_path) and name.startswith('test'):
            yield from find_test_file(sub_path)
        elif os.path.isfile(sub_path) and name.endswith('.py'):
            yield sub_path


def load_test_case(suite: unittest.TestSuite, path: str):
    for name in os.listdir(path):
        print(name)
        if not name.startswith('test'):
            continue
        sub_path = path + '/' + name
        if os.path.isdir(sub_path):
            print(path, name)
            suite.addTest(unittest.defaultTestLoader.discover(sub_path, "*.py"))
            load_test_case(suite, sub_path)


def main():
    suite = unittest.TestSuite()
    for folder in find_test_file(Path('.')):
        suite.addTest(unittest.defaultTestLoader.discover(folder, "*.py"))

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    for x in find_test_file(Path('.')):
        if str(x) != 'test_all.py':
            s=f'from {str(x).split(".py")[0]} import *'
            exec(s)
            # y=__import__(s)
            # print(s, y)
            # suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(y))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    unittest.main()
