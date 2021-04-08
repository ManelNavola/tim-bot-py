from typing import Optional, Any

from autoslot import Slots

import utils
from inventory_data.rarity import Rarity, RarityInstance


class StatInstance(Slots):
    def __init__(self, abv: str, name: str, icon: str, cost: int, rarity: RarityInstance, base: int = 0):
        self.name: str = name
        self.abv: str = abv
        self.base: int = base
        self.icon: str = icon
        self.rarity: RarityInstance = rarity
        self.cost: int = cost

    def get_value(self, increment: int) -> Any:
        return self.base + increment

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value}"

    def print(self, value: int, short: bool = False, persistent_value: Optional[int] = None) -> str:
        tp: list[str] = []
        if short:
            tp.append(f"{self.abv}: ")
        else:
            tp.append(f"{self.icon} {self.abv}: ")

        if persistent_value is not None:
            if self.base > 0:
                if value == 0:
                    tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(value))}")
                else:
                    if short:
                        tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(value))}")
                    else:
                        tp.append(f"{self.represent(persistent_value)}/{self.represent(self.get_value(value))} "
                                  f"(+{self.represent(self.get_value(value) - self.base)})")
            else:
                tp.append(f"{self.represent(persistent_value)} +{self.represent(self.get_value(value))}")
        else:
            if self.base > 0:
                if short or value == 0:
                    tp.append(f"{self.represent(self.get_value(value))}")
                else:
                    tp.append(f"{self.represent(self.get_value(value))} "
                              f"(+{self.represent(self.get_value(value) - self.base)})")
            else:
                tp.append(f"{self.represent(self.get_value(value))}")
        return ''.join(tp)


class StatInstanceChance(StatInstance):
    def __init__(self, abv: str, name: str, icon: str, cost: int, rarity: RarityInstance, base: Optional[int] = 0):
        super().__init__(abv, name, icon, cost, rarity, base)

    def get_value(self, increment: int) -> Any:
        x = self.base + increment
        return x / (x + 40)

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.0%}"


class HP(StatInstance):
    def __init__(self):
        super().__init__('HP', "Health Points", utils.Emoji.HP, 10, Rarity.COMMON, 20)


class MP(StatInstance):
    def __init__(self):
        super().__init__('MP', "Mana", utils.Emoji.MP, 10, Rarity.COMMON, 2)


class STR(StatInstance):
    def __init__(self):
        super().__init__('STR', "Attack strength", utils.Emoji.STR, 8, Rarity.COMMON, 2)


class DEF(StatInstance):
    def __init__(self):
        super().__init__('DEF', "Damage reduction", utils.Emoji.DEF, 8, Rarity.COMMON)


class SPD(StatInstance):
    def __init__(self):
        super().__init__('SPD', "Attack speed", utils.Emoji.SPD, 8, Rarity.COMMON, 1)

    def get_value(self, increment: int) -> Any:
        x = increment
        return x / (x + 20) + self.base

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.2f}"


class EVA(StatInstanceChance):
    def __init__(self):
        super().__init__('EVA', "Chance of ignoring an attack", utils.Emoji.EVA, 9, Rarity.COMMON)


class CONT(StatInstanceChance):
    def __init__(self):
        super().__init__('CONT', "Chance of attacking immediately when receiving damage",
                         utils.Emoji.CONT, 20, Rarity.UNCOMMON)


class CRIT(StatInstanceChance):
    def __init__(self):
        super().__init__('CRIT', "Chance of attack with double damage", utils.Emoji.CRIT, 15, Rarity.UNCOMMON)


class STUN(StatInstanceChance):
    def __init__(self):
        super().__init__('STUN', "Chance of stunning on attack", utils.Emoji.STUN, 15, Rarity.UNCOMMON)


class VAMP(StatInstanceChance):
    def __init__(self):
        super().__init__('VAMP', "Chance of stealing health on attack", utils.Emoji.VAMP, 25, Rarity.RARE)


class Stats:
    HP: StatInstance = HP()
    MP: StatInstance = MP()
    STR: StatInstance = STR()
    DEF: StatInstance = DEF()
    SPD: StatInstance = SPD()
    EVA: StatInstance = EVA()
    CONT: StatInstance = CONT()
    CRIT: StatInstance = CRIT()
    STUN: StatInstance = STUN()
    VAMP: StatInstance = VAMP()

    @staticmethod
    def get_by_abv(name: str) -> StatInstance:
        stat_dict: dict = {x.abv: x for x in Stats.get_all()}
        return stat_dict[name]

    @staticmethod
    def get_all() -> list[StatInstance]:
        stat_list: list[StatInstance] = [Stats.HP, Stats.MP, Stats.STR, Stats.DEF, Stats.SPD,
                                         Stats.EVA, Stats.CONT, Stats.CRIT, Stats.STUN,
                                         Stats.VAMP]
        return stat_list
