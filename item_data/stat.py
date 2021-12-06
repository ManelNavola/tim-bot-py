from enum import Enum, unique
from typing import Optional, Any, List

from autoslot import Slots

from enums.emoji import Emoji


@unique
class StatType(Enum):
    MAIN = 0
    CHANCE = 1
    SECONDARY = 2

    def get_weighted_value(self) -> float:
        return {
            StatType.MAIN: 1.0,
            StatType.CHANCE: 0.7,
            StatType.SECONDARY: 0.6
        }[self]


class StatInstance(Slots):
    def __init__(self, abv: str, name: str, icon: Emoji, stat_type: StatType = StatType.MAIN,
                 multiplier: Any = 1, limit_per_item: int = 9999, is_persistent: bool = False):
        self.name: str = name
        self.abv: str = abv
        self.type: StatType = stat_type
        self.icon: Emoji = icon
        self.limit: int = limit_per_item
        self.multiplier: Any = multiplier
        self.is_persistent: bool = is_persistent

    def get_value(self, value: int) -> Any:
        return value * self.multiplier

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value}"

    def print(self, value: int, base: int = 0, short: bool = False, persistent_value: Optional[int] = None) -> str:
        tp: List[str] = []
        if short:
            tp.append(f"{self.abv}: ")
        else:
            tp.append(f"{self.icon} {self.abv}: ")

        total = base + value
        if persistent_value is not None:
            if base > 0 and value == 0:
                tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))}")
            else:
                if short or value == 0:
                    tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))}")
                else:
                    tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))} "
                              f"(+{value})")
        else:
            if base > 0 and value == 0:
                tp.append(f"{self.represent(self.get_value(total))}")
            else:
                if short or value == 0:
                    tp.append(f"{self.represent(self.get_value(total))}")
                else:
                    tp.append(f"{self.represent(self.get_value(total))} "
                              f"(+{value})")
        return ''.join(tp)


class StatInstanceDecimals(StatInstance):
    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.2f}"


class StatInstancePercent(StatInstance):
    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.0%}"


class StatInstancePercentWeighted(StatInstance):
    def __init__(self, abv: str, name: str, icon: Emoji, weight: int, stat_type: StatType = StatType.MAIN,
                 multiplier: Any = 1,
                 limit_per_item: int = 9999, is_persistent: bool = False):
        super().__init__(abv, name, icon, stat_type, multiplier, limit_per_item, is_persistent)
        self._weight = weight

    def get_value(self, value: int) -> Any:
        return (value/(value + self._weight)) * self.multiplier

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.0%}"


class HP(StatInstance):
    def __init__(self):
        super().__init__('HP', "Health Points", Emoji.HP,
                         multiplier=2, is_persistent=True)


class AP(StatInstance):
    def __init__(self):
        super().__init__('AP', "Action Points", Emoji.AP,
                         is_persistent=True, stat_type=StatType.SECONDARY)


class STR(StatInstance):
    def __init__(self):
        super().__init__('STR', "Attack strength", Emoji.STR)


class DEF(StatInstance):
    def __init__(self):
        super().__init__('DEF', "Damage reduction", Emoji.DEF)


class SPD(StatInstanceDecimals):
    def __init__(self):
        super().__init__('SPD', "Attack speed", Emoji.SPD,
                         multiplier=0.05, stat_type=StatType.SECONDARY)

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value + 1}"


class EVA(StatInstancePercentWeighted):
    def __init__(self):
        super().__init__('EVA', "Chance of ignoring an attack", Emoji.EVA, stat_type=StatType.CHANCE,
                         weight=30)


class CONT(StatInstancePercentWeighted):
    def __init__(self):
        super().__init__('CONT', "Chance of attacking immediately when receiving damage", Emoji.CONT,
                         stat_type=StatType.CHANCE,
                         weight=30)


class CRIT(StatInstancePercentWeighted):
    def __init__(self):
        super().__init__('CRIT', "Chance of attack with double damage", Emoji.CRIT, stat_type=StatType.CHANCE,
                         weight=30)


class VAMP(StatInstancePercentWeighted):
    def __init__(self):
        super().__init__('VAMP', "Chance of stealing health on attack", Emoji.VAMP, stat_type=StatType.CHANCE,
                         weight=30)


class Stat(Enum):
    _ignore_ = ['_INFO']
    HP = HP()
    AP = AP()
    STR = STR()
    DEF = DEF()
    SPD = SPD()
    EVA = EVA()
    CONT = CONT()
    CRIT = CRIT()
    VAMP = VAMP()
    _INFO = {}

    @staticmethod
    def get_by_abv(abv: str) -> 'Stat':
        return Stat._INFO['from_abv'][abv]

    def is_persistent(self) -> bool:
        return self.value.is_persistent

    def get_value(self, value: int) -> Any:
        return self.value.get_value(value)

    def get_abv(self) -> str:
        return self.value.abv

    def get_type(self) -> StatType:
        return self.value.type

    @staticmethod
    def get_type_list(st: StatType) -> List['Stat']:
        return Stat._INFO['of_type'][st]

    def get_limit(self) -> int:
        return self.value.limit

    def print(self, value: int, base: int = 0, short: bool = False, persistent_value: Optional[int] = None) -> str:
        return self.value.print(value, base, short, persistent_value)


stat_dict = {
    'from_abv': {stat.value.abv: stat for stat in Stat},
    'of_type': {st: [stat for stat in Stat if stat.get_type() == st] for st in StatType}
}

Stat._INFO = stat_dict
