from robot.comm.priority import Priority
from alicebot.plugin import Plugin
from alicebot.typing import T_Config, T_Event, T_State
from abc import ABC
from typing import Generic

__all__ = ['PluginBase']


class PluginBase(Plugin, ABC, Generic[T_Event, T_State, T_Config]):
    priority = -1  # 用无效的priority强制子类定义自己的priority
    block = False

    def __init_subclass__(cls, /, priority: Priority = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if priority is not None:
            cls.priority = priority.priority
            cls.block = priority.block
