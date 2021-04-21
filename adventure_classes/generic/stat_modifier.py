from abc import abstractmethod
from typing import Optional

from autoslot import Slots

from item_data.stat import Stat


def up_to(x, to: int) -> str:
    tr = f"{round(x, to)}"
    if tr.endswith('.0'):
        return tr.split('.')[0]
    return tr


class StatModifier(Slots):
    def __init__(self, stat: Stat, value: float, duration: int = -1):
        self.stat: Stat = stat
        self.value: float = value
        self.duration: int = duration

    @abstractmethod
    def apply(self, value: float) -> float:
        raise NotImplemented()

    @abstractmethod
    def print(self) -> str:
        raise NotImplemented()

    @abstractmethod
    def clone(self, override_duration: Optional[int] = None):
        raise NotImplemented()


class StatModifierMultiply(StatModifier):
    def apply(self, value: float) -> float:
        return value * self.value

    def print(self) -> str:
        return f"x{up_to(self.value, 2)}"

    def clone(self, override_duration: Optional[int] = None):
        if override_duration is None:
            override_duration = self.duration
        return StatModifierMultiply(self.stat, self.value, override_duration)


class StatModifierAdd(StatModifier):
    def apply(self, value: float) -> float:
        return value + self.value

    def print(self) -> str:
        if self.value > 0:
            return f"+{up_to(self.value, 2)}"
        else:
            return f"{up_to(self.value, 2)}"

    def clone(self, override_duration: Optional[int] = None):
        if override_duration is None:
            override_duration = self.duration
        return StatModifierAdd(self.stat, self.value, override_duration)
