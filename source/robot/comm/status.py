from comiee import InfiniteDict
from public.log import bot_logger
from public.config import data_path
from collections import deque, defaultdict
from threading import Lock
import time
import asyncio
import json
import os

_STATUS_FILE = data_path('status.json')

_file_lock = Lock()

status_dict: dict[str, type['Status']] = {}  # 用于config命令


def status_load():
    if _file_lock.locked():
        return
    with _file_lock:
        if not os.path.exists(_STATUS_FILE):
            return
        with open(_STATUS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for name in data:
            for option in data[name]:
                for ids in data[name][option]:
                    if ids.isdigit():
                        setattr(status_dict[name][int(ids)], option, data[name][option][ids])


def status_save():
    if _file_lock.locked():
        return
    with _file_lock:
        data = InfiniteDict()
        for name, status_cls in status_dict.items():
            for option in status_cls.options:
                for id in status_cls.data:
                    data[name][option][id] = getattr(status_cls[id], option)
        with open(_STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)


class StatusMeta(type):
    def __init__(cls, name, bases, attrs, **kwargs):  # 定义新类的时候执行
        super().__init__(name, bases, attrs, **kwargs)
        cls.data = defaultdict(cls)

    def __call__(cls, *args, **kwargs):  # 新类实例化时执行
        if _file_lock.locked():
            return super().__call__(*args, **kwargs)
        else:
            with _file_lock:
                return super().__call__(*args, **kwargs)

    def __getitem__(cls, item):
        return cls.data[item]

    def __setitem__(cls, key, value):
        cls.data[key] = value

    def __delitem__(cls, key):
        del cls.data[key]

    def __get__(cls, instance, owner):
        if instance is None:
            return cls
        return cls[instance.id]

    def __set__(cls, instance, value):
        cls[instance.id] = value

    def __delete__(cls, instance):
        del cls[instance.id]


class Status(metaclass=StatusMeta):
    """两种用法：
    1、将子类设置为Session类的类变量，使用Session类实例.类变量名的方式访问此Session的Status
    2、通过类名[id]的方式访问对应id的Status
    """

    # options中的变量会备份到文件中
    # options中的变量可以用config命令修改，注意需要同时在status_dict里面注册
    options: tuple[str] = ()

    def __init_subclass__(cls, **kwargs):
        # 初始化子类时使用config_name指定用于config命令和保存文件的名字
        status_dict[kwargs.get('config_name', cls.__name__)] = cls

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        status_save()


class SessionStatus(Status, config_name='session'):
    options = (
        'interval',
        'max_times',
    )

    def __init__(self):
        self.interval: float = 10  # 两次回复间间隔的秒数
        self.max_times: int = 100  # 最大回复次数

        self._reply_lock: asyncio.Lock = asyncio.Lock()
        self._last_reply_timestamp: float = 0  # 上次处理的时间戳，用于间隔回复
        self._reply_times: int = 0  # 当前回复次数

    def _record_reply(self):
        self._last_reply_timestamp = time.time()
        self._reply_times += 1

    async def __aenter__(self):
        await self._reply_lock.acquire()
        # 回复间隔时长限制
        while (t := self._last_reply_timestamp + self.interval - time.time()) > 0:  # 需要等待的时长
            bot_logger.info(f'间隔时间不足，将等待{t}秒后回复')
            await asyncio.sleep(t)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._record_reply()
        self._reply_lock.release()

    def can_reply(self):
        # 最大回复次数限制
        last_date = time.strftime("%Y-%m-%d", time.gmtime(self._last_reply_timestamp))
        this_date = time.strftime("%Y-%m-%d", time.gmtime(time.time()))
        if last_date != this_date:
            self._reply_times = 0
            bot_logger.info('回复次数已清零')
        if self._reply_times > self.max_times:
            bot_logger.info('回复次数已达上限，将不再回复')
            return False
        return True


class ChatStatus(Status, config_name='chat'):
    options = (
        'switch',
        'at_switch',
        # TODO 增加ai回复类型
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


class P24GameStatus(Status):
    def __init__(self):
        self.in_game: bool = False  # 是否在游戏中
        self.question: list = []  # 存储当前的问题
        self.wrong_count: int = 0  # 答错的次数
        self.MAX_COUNT = 5  # 最大可以答错的次数

    def add_count_and_check_has_limited(self):
        self.wrong_count += 1
        return self.wrong_count > self.MAX_COUNT


status_load()
