from comiee import overload
from collections import defaultdict
from typing import Generic, TypeVar

__all__ = ['Status']

T_Value = TypeVar('T_Value')


class Status(Generic[T_Value]):
    @overload
    def __init__(self, *, default_value):
        self.__init__(default_factory=lambda: default_value)

    @overload
    def __init__(self, *, default_factory):
        self.data: dict[int, T_Value] = defaultdict(default_factory)

    def __setitem__(self, key: int, value: T_Value):
        self.data[key] = value

    def __getitem__(self, key: int) -> T_Value:
        return self.data[key]

    def __delitem__(self, key: int):
        if key in self.data:
            del self.data[key]
