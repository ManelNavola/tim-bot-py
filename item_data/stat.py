from enum import Enum
from typing import Optional, Any

from autoslot import Slots

from enums.emoji import Emoji


class StatInstance(Slots):
    def __init__(self, abv: str, name: str, icon: Emoji, cost: int, multiplier: Any = 1,
                 limit_per_item: int = 9999, is_persistent: bool = False):
        self.name: str = name
        self.abv: str = abv
        self.icon: Emoji = icon
        self.cost: int = cost
        self.limit: int = limit_per_item
        self.multiplier: Any = multiplier
        self.is_persistent: bool = is_persistent

    def get_value(self, value: int) -> Any:
        return value * self.multiplier

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value}"

    def print(self, value: int, base: int = 0, short: bool = False, persistent_value: Optional[int] = None) -> str:
        tp: list[str] = []
        if short:
            tp.append(f"{self.abv}: ")
        else:
            tp.append(f"{self.icon} {self.abv}: ")

        total = base + value
        if persistent_value is not None:
            if base > 0:
                if value == 0:
                    tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))}")
                else:
                    if short:
                        tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))}")
                    else:
                        tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))} "
                                  f"(+{value})")
            else:
                if short:
                    tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))}")
                else:
                    tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(total))} (+{value})")
        else:
            if base > 0:
                if short or value == 0:
                    tp.append(f"{self.represent(self.get_value(total))}")
                else:
                    tp.append(f"{self.represent(self.get_value(total))} "
                              f"(+{value})")
            else:
                if short:
                    tp.append(f"{self.represent(self.get_value(value))}")
                else:
                    tp.append(f"{self.represent(self.get_value(value))} (+{value})")
        return ''.join(tp)


class StatInstanceDecimals(StatInstance):
    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.2f}"


class StatInstancePercent(StatInstance):
    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.0%}"


class HP(StatInstance):
    def __init__(self):
        super().__init__('HP', "Health Points", Emoji.HP, 10,
                         multiplier=2, is_persistent=True)


class MP(StatInstance):
    def __init__(self):
        super().__init__('MP', "Mana", Emoji.MP, 10,
                         is_persistent=True)


class STR(StatInstance):
    def __init__(self):
        super().__init__('STR', "Attack strength", Emoji.STR, 8)


class DEF(StatInstance):
    def __init__(self):
        super().__init__('DEF', "Damage reduction", Emoji.DEF, 8)


class SPD(StatInstanceDecimals):
    def __init__(self):
        super().__init__('SPD', "Attack speed", Emoji.SPD, 8,
                         multiplier=0.05)

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value + 1}"


class EVA(StatInstancePercent):
    def __init__(self):
        super().__init__('EVA', "Chance of ignoring an attack", Emoji.EVA, 12,
                         multiplier=0.02, limit_per_item=5)


class CONT(StatInstancePercent):
    def __init__(self):
        super().__init__('CONT', "Chance of attacking immediately when receiving damage", Emoji.CONT, 20,
                         multiplier=0.02, limit_per_item=5)


class CRIT(StatInstancePercent):
    def __init__(self):
        super().__init__('CRIT', "Chance of attack with double damage", Emoji.CRIT, 15,
                         multiplier=0.02, limit_per_item=5)


class VAMP(StatInstancePercent):
    def __init__(self):
        super().__init__('VAMP', "Chance of stealing health on attack", Emoji.VAMP, 25,
                         multiplier=0.02, limit_per_item=5)


class Stat(Enum):
    _ignore_ = ['_INFO']
    HP = HP()
    MP = MP()
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

    def get_limit(self) -> int:
        return self.value.limit

    def print(self, value: int, base: int = 0, short: bool = False, persistent_value: Optional[int] = None) -> str:
        return self.value.print(value, base, short, persistent_value)


stat_dict = {
    'from_abv': {stat.value.abv: stat for stat in Stat}
}

Stat._INFO = stat_dict
