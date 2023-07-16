from itertools import count
from functools import partial

_produce_priority = partial(next,count())


#alicebot用type(priority)判断优先级，无法使用IntEnum
CHAT = _produce_priority()  # 聊天的优先级最低，优先处理命令
