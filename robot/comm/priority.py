from itertools import count
from enum import Enum

_count_iter = count()


def _produce_priority(block):
    return next(_count_iter), block


class Priority(Enum):
    # 不能用直接赋值block，值重复的枚举会合并
    Log = _produce_priority(False)
    Request = _produce_priority(True)
    Command = _produce_priority(True)
    Chat = _produce_priority(False)

    def __init__(self, priority, block):
        self.priority = priority
        self.block = block
