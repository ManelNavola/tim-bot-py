from abc import abstractmethod
from enum import unique, Enum
from typing import Optional, Any

from autoslot import Slots

from item_data.stat import Stat


def up_to(x, to: int) -> str:
    tr = f"{round(x, to)}"
    if tr.endswith('.0'):
        return tr.split('.')[0]
    return tr


@unique
class StatModifierOperation(Enum):
    ADD = 0
    MULT = 1


class StatModifier(Slots):
    def __init__(self, stat: Stat, value: float, operation: StatModifierOperation,
                 duration: int = -1, persistent: bool = False, battle_duration: bool = False):
        if persistent:
            assert stat.is_persistent(), 'Stat cannot be persistent'
        self.stat: Stat = stat
        self.value: float = value
        self.operation: StatModifierOperation = operation
        self.per_battle: bool = battle_duration
        self.duration: int = duration
        self.persistent: bool = persistent

    def get_price(self) -> float:
        v: float = 0
        if self.operation == StatModifierOperation.ADD:
            v = pow(self.value, 1.5) * self.stat.get_type().get_weighted_value()
        elif self.operation == StatModifierOperation.MULT:
            v = pow(self.value, 6) * self.stat.get_type().get_weighted_value()
        if self.persistent:
            v *= (1 + self.stat.get_type().get_weighted_value())
        else:
            v *= self.duration
        if self.per_battle:
            v *= 5
        return v

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        d = {
            'Stat': self.stat.get_abv(),
            'Value': self.value,
            'Operation': self.operation.value,
            'Duration': self.duration
        }
        if self.persistent:
            d['Persistent'] = True
        if self.per_battle:
            d['PerBattle'] = True
        return d

    @staticmethod
    def from_dict(data_dict: dict[str, Any]) -> 'StatModifier':
        return StatModifier(Stat.get_by_abv(data_dict['Stat']), data_dict['Value'],
                            StatModifierOperation(data_dict['Operation']), data_dict.get('Duration', 0),
                            'Persistent' in data_dict, 'PerBattle' in data_dict)

    def apply(self, value: float) -> float:
        if self.operation == StatModifierOperation.ADD:
            return value + self.value
        elif self.operation == StatModifierOperation.MULT:
            return value * self.value

    def print(self, include_abv: bool = False) -> str:
        after: str = ''
        if include_abv:
            after = f" {self.stat.get_abv()}"
        if self.operation == StatModifierOperation.ADD:
            if self.value > 0:
                return f"+{up_to(self.value, 2)}{after}"
            else:
                return f"{up_to(self.value, 2)}{after}"
        elif self.operation == StatModifierOperation.MULT:
            return f"x{up_to(self.value, 2)}{after}"

    def clone(self, override_duration: Optional[int] = None) -> 'StatModifier':
        duration = self.duration
        if override_duration is not None:
            duration = override_duration
        return StatModifier(self.stat, self.value, self.operation, duration, self.persistent)
