from itertools import count
from functools import partial

_produce_priority = partial(next, count())

# alicebot用type(priority)判断优先级，无法使用IntEnum
LOG = _produce_priority()  # 第一个插件用来记录事件，不会有任何处理
REQUEST = _produce_priority()  # 请求的优先级最高，并阻塞其他事件
CHAT = _produce_priority()  # 聊天的优先级最低，优先处理命令
