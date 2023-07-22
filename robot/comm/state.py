from collections import defaultdict
from typing import Generic, TypeVar

__all__ = ['State']

T_Value = TypeVar('T_Value')


class State(Generic[T_Value]):
    def __init__(self, default: T_Value):
        self.data: dict[int, T_Value] = defaultdict(lambda: default)

    def __setitem__(self, key: int, value: T_Value):
        self.data[key] = value

    def __getitem__(self, key: int) -> T_Value:
        return self.data[key]

    def __delitem__(self, key: int):
        if key in self.data:
            del self.data[key]
