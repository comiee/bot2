from public.log import bot_logger
from public.state import State
from collections import deque
import time
import asyncio


class Status:
    options: tuple[str] = ()
    # TODO 写文件


class SessionStatus(Status):
    options = (
        'interval',
        'max_times',
    )

    def __init__(self):
        self.interval: float = 10  # 两次回复间间隔的秒数
        self.max_times: int = 100  # 最大回复次数

        self._last_reply_timestamp: float = 0  # 上次处理的时间戳，用于间隔回复
        self._reply_times: int = 0  # 当前回复次数

    def record_reply(self):
        self._last_reply_timestamp = time.time()
        self._reply_times += 1

    async def can_reply(self):
        # 最大回复次数限制
        if self._reply_times > self.max_times:
            bot_logger.info('回复次数已达上限，将不再回复')
            return False

        # 回复间隔时长限制
        t = self._last_reply_timestamp + self.interval - time.time()  # 需要等待的时长
        if t > 0:
            bot_logger.info(f'间隔时间不足，将等待{t}秒后回复')
            await asyncio.sleep(t)

        return True


class ChatStatus(Status):
    options = (
        'switch',
        'at_switch'
    )

    def __init__(self):
        self.switch: bool = True  # 总开关
        self.at_switch: bool = True  # 是否只有艾特才会回应

        self._history: deque = deque(maxlen=10)  # 聊天记录

    def save_history(self, text):
        self._history.append(text)

    def get_repetitions(self, text):
        n = 0
        for s in reversed(self._history):
            if s == text:
                n += 1
            else:
                break
        return n


class SessionState(State):
    def __init__(self, status_cls: type[Status]):
        super().__init__(default_factory=status_cls)
        self.options = status_cls.options

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self[instance.id]

    def __set__(self, instance, value):
        self[instance.id] = value

    def __delete__(self, instance):
        del self[instance.id]


# Plugin加载会导致类成员被重新实例化，为保证全局唯一，SessionState类的变量统一在这里定义
session_state = SessionState(SessionStatus)
chat_state = SessionState(ChatStatus)
