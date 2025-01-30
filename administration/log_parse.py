"""log解析工具"""
import re
from datetime import datetime


class LogIter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.it = self.__get_it()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.it)

    def __get_it(self):
        with open(self.file_path, encoding='utf-8') as f:
            t, name, level, msg = '', '', '', ''
            for s in f:
                if m := re.match(r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})] '
                                 r'(.*) (DEBUG|INFO|WARNING|ERROR):(.*)$', s):
                    if t:
                        yield t, name, level, msg
                    t, name, level, msg = m.groups()
                else:
                    msg += s
            yield t, name, level, msg

    def filter_by_level(self, *levels):
        levels = set(levels)
        self.it = filter(lambda x: x[2] in levels, self.it)
        return self

    def filter_by_time(self, start, end):
        self.it = filter(lambda x: start < datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S,%f') < end, self.it)
        return self


if __name__ == '__main__':
    print(*LogIter(r'F:\workspace\pycharm\小魅二代\source\data\log\masterServer.txt')
          .filter_by_level('WARNING')
          .filter_by_time(datetime(2023, 10, 1), datetime(2023, 11, 1))
          , sep='\n')
