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

    def get_value(self, increment: int) -> Any:
        return self.base + increment

    def print(self, value: int, short: bool = False, persistent_value: Optional[int] = None) -> str:
        tp: list[str] = []
        if short:
            tp.append(f"{self.abv}: ")
        else:
            tp.append(f"{self.icon} {self.abv}: ")

        if persistent_value:
            if self.base > 0:
                value -= self.base
                if value == 0:
                    tp.append(f"{persistent_value}/{self.get_value(value)}")
                else:
                    if short:
                        tp.append(f"{persistent_value}/{self.get_value(value)}")
                    else:
                        tp.append(f"{persistent_value}/{self.get_value(value)} (+{self.get_value(value) - self.base})")
            else:
                tp.append(f"{persistent_value} +{self.get_value(value)}")
        else:
            if self.base > 0:
                value -= self.base
                if value == 0:
                    tp.append(f"{self.base}")
                else:
                    if short:
                        tp.append(f"{self.get_value(value)})")
                    else:
                        tp.append(f"{self.base} (+{self.get_value(value) - self.base})")
            else:
                tp.append(f"+{self.get_value(value)}")
        return ''.join(tp)


class StatInstanceChance(StatInstance):
    def __init__(self, abv: str, name: str, icon: str, cost: int, rarity: RarityInstance, base: Optional[int] = 0):
        super().__init__(abv, name, icon, cost, rarity, base)

    def get_value(self, increment: int) -> Any:
        x = self.base + increment
        return x / (x + 40)

    def print(self, value: int, short: bool = False, persistent_value: Optional[int] = None) -> str:
        tp: list[str] = []
        if short:
            tp.append(f"{self.abv}: ")
        else:
            tp.append(f"{self.icon} {self.abv}: ")

        if persistent_value:
            if self.base > 0:
                if value == 0:
                    tp.append(f"{persistent_value:.0%}/{self.base:.0%}")
                else:
                    tp.append(f"{persistent_value:.0%}/{self.base:.0%} (+{(self.get_value(value) - self.base):.0%})")
            else:
                tp.append(f"{persistent_value:.0%} +{self.get_value(value):.0%}")
        else:
            if self.base > 0:
                if value == 0:
                    tp.append(f"{self.base:.0%}")
                else:
                    tp.append(f"{self.base:.0%} (+{(self.get_value(value) - self.base):.0%})")
            else:
                tp.append(f"+{self.get_value(value):.0%}")
        return ''.join(tp)


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
        super().__init__('SPD', "Attack speed", utils.Emoji.SPD, 8, Rarity.COMMON)


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
        super().__init__('CRIT', "Chance of stealing health on attack", utils.Emoji.VAMP, 25, Rarity.RARE)


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
    _LIST_INDEX: list[StatInstance] = [HP, MP, STR, DEF, SPD, EVA, CONT, CRIT, STUN, VAMP]
    _INDEX: dict[str, StatInstance] = {x.name: x for x in _LIST_INDEX}

    @staticmethod
    def get_by_name(name: str) -> StatInstance:
        return Stats._INDEX[name]

    @staticmethod
    def get_all() -> list[StatInstance]:
        return Stats._LIST_INDEX
