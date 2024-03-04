from itertools import count
from enum import Enum

_count_iter = count()


def _produce_priority(block):
    return next(_count_iter), block


class Priority(Enum):
    # 不能用直接赋值block，值重复的枚举会合并
    Filter = _produce_priority(True)
    Log = _produce_priority(False)
    Request = _produce_priority(True)
    Anti = _produce_priority(True)
    Command = _produce_priority(False)  # Command插件结束固定调用stop来阻塞其他插件执行，如果中途使用了skip则不阻塞
    Game = _produce_priority(True)
    Chat = _produce_priority(False)  # Chat在handle中判断是否需要回复，如果需要则使用stop阻塞其他插件

    def __init__(self, priority, block):
        self.priority = priority
        self.block = block
