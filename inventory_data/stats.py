from typing import Optional, Any

from autoslot import Slots

import utils
from inventory_data.rarity import Rarity, RarityInstance


class StatInstance(Slots):
    def __init__(self, abv: str, name: str, icon: str, cost: int, rarity: RarityInstance, base: Optional[int] = 0):
        self.name: str = name
        self.abv: str = abv
        self.base: int = base
        self.icon: str = icon
        self.rarity: RarityInstance = rarity
        self.cost: int = cost

    def get_value(self, value: int) -> Any:
        return self.base + value

    def print(self, value: int) -> str:
        if self.base > 0:
            if value == 0:
                return f"{self.icon} {self.abv}: {self.base}"
            else:
                return f"{self.icon} {self.abv}: {self.base} (+{self.get_value(value) - self.base})"
        else:
            return f"{self.icon} {self.abv}: +{self.get_value(value)}"


class HP(StatInstance):
    def __init__(self):
        super().__init__('HP', "Health Points", utils.Emoji.HP, 10, Rarity.COMMON, 50)


class STR(StatInstance):
    def __init__(self):
        super().__init__('STR', "Attack strength", utils.Emoji.STR, 8, Rarity.COMMON, 10)


class DEF(StatInstance):
    def __init__(self):
        super().__init__('DEF', "Damage reduction", utils.Emoji.DEF, 8, Rarity.COMMON)


class SPD(StatInstance):
    def __init__(self):
        super().__init__('SPD', "Attack speed", utils.Emoji.SPD, 8, Rarity.COMMON)


class EVA(StatInstance):
    def __init__(self):
        super().__init__('EVA', "Chance of ignoring an attack", utils.Emoji.EVA, 9, Rarity.COMMON)


class CONT(StatInstance):
    def __init__(self):
        super().__init__('CONT', "Chance of attacking immediately when receiving damage",
                         utils.Emoji.CONT, 20, Rarity.UNCOMMON)


class CRIT(StatInstance):
    def __init__(self):
        super().__init__('CRIT', "Chance of attack with double damage", utils.Emoji.CRIT, 15, Rarity.UNCOMMON)

    def print(self, value: int) -> str:
        return f"{self.get_value(value):.0%}"


class STUN(StatInstance):
    def __init__(self):
        super().__init__('STUN', "Chance of stunning on attack", utils.Emoji.STUN, 15, Rarity.UNCOMMON)


class VAMP(StatInstance):
    def __init__(self):
        super().__init__('CRIT', "Chance of stealing health on attack", utils.Emoji.VAMP, 25, Rarity.RARE)


class Stats:
    HP: StatInstance = HP()
    STR: StatInstance = STR()
    DEF: StatInstance = DEF()
    SPD: StatInstance = SPD()
    EVA: StatInstance = EVA()
    CONT: StatInstance = CONT()
    CRIT: StatInstance = CRIT()
    STUN: StatInstance = STUN()
    VAMP: StatInstance = VAMP()
    _INDEX: dict[str, StatInstance] = {x.name: x for x in [HP, STR, DEF, SPD, EVA, CONT, CRIT, STUN, VAMP]}

    @staticmethod
    def get_by_name(name: str) -> StatInstance:
        return Stats._INDEX[name]

    @staticmethod
    def get_all() -> dict[str, StatInstance]:
        return Stats._INDEX
