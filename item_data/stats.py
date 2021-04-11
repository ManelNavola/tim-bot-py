from typing import Optional, Any

from autoslot import Slots

from enums.emoji import Emoji
from item_data.rarity import Rarity, RarityInstance


class StatInstance(Slots):
    def __init__(self, abv: str, name: str, icon: Emoji, cost: int, rarity: RarityInstance):
        self.name: str = name
        self.abv: str = abv
        self.icon: Emoji = icon
        self.rarity: RarityInstance = rarity
        self.cost: int = cost

    def get_value(self, value: int) -> Any:
        return value

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value}"

    def print(self, value: int, short: bool = False, base: int = 0, persistent_value: Optional[int] = None) -> str:
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
                    tp.append(f"{self.represent(persistent_value)}")
                else:
                    tp.append(f"{self.represent(persistent_value)} (+{value})")
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


class StatInstanceChance(StatInstance):
    def __init__(self, abv: str, name: str, icon: Emoji, cost: int, rarity: RarityInstance):
        super().__init__(abv, name, icon, cost, rarity)

    def get_value(self, value: int) -> Any:
        if value < 0:
            return 0
        return value / (value + 40)

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.0%}"


class HP(StatInstance):
    def __init__(self):
        super().__init__('HP', "Health Points", Emoji.HP, 10, Rarity.COMMON)


class MP(StatInstance):
    def __init__(self):
        super().__init__('MP', "Mana", Emoji.MP, 10, Rarity.COMMON)


class STR(StatInstance):
    def __init__(self):
        super().__init__('STR', "Attack strength", Emoji.STR, 8, Rarity.COMMON)


class DEF(StatInstance):
    def __init__(self):
        super().__init__('DEF', "Damage reduction", Emoji.DEF, 8, Rarity.COMMON)


class SPD(StatInstance):
    def __init__(self):
        super().__init__('SPD', "Attack speed", Emoji.SPD, 8, Rarity.COMMON)

    def get_value(self, value: int) -> Any:
        if value < 0:
            return 0
        return value / (value + 30)

    @staticmethod
    def represent(value: Any) -> str:
        return f"{value:.2f}"


class EVA(StatInstanceChance):
    def __init__(self):
        super().__init__('EVA', "Chance of ignoring an attack", Emoji.EVA, 9, Rarity.COMMON)


class CONT(StatInstanceChance):
    def __init__(self):
        super().__init__('CONT', "Chance of attacking immediately when receiving damage",
                         Emoji.CONT, 20, Rarity.UNCOMMON)


class CRIT(StatInstanceChance):
    def __init__(self):
        super().__init__('CRIT', "Chance of attack with double damage", Emoji.CRIT, 15, Rarity.UNCOMMON)


class STUN(StatInstanceChance):
    def __init__(self):
        super().__init__('STUN', "Chance of stunning on attack", Emoji.STUN, 15, Rarity.UNCOMMON)


class VAMP(StatInstanceChance):
    def __init__(self):
        super().__init__('VAMP', "Chance of stealing health on attack", Emoji.VAMP, 25, Rarity.RARE)


class Stats:
    HP = HP()
    MP = MP()
    STR = STR()
    DEF = DEF()
    SPD = SPD()
    EVA = EVA()
    CONT = CONT()
    CRIT = CRIT()
    STUN = STUN()
    VAMP = VAMP()
    _STAT_INFO = {}

    @staticmethod
    def get_all() -> list[StatInstance]:
        return [Stats.HP, Stats.MP,
                Stats.STR, Stats.DEF, Stats.SPD,
                Stats.EVA, Stats.CONT, Stats.CRIT, Stats.STUN,
                Stats.VAMP]

    @staticmethod
    def get_by_abv(abv: str) -> StatInstance:
        return Stats._STAT_INFO['from_abv'][abv]


stat_dict = {
    'from_abv': {x.abv: x for x in Stats.get_all()}
}

Stats._STAT_INFO = stat_dict
