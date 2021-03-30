# Dictionary
from dataclasses import dataclass
from autoslot import Slots
from utils import DictRef


# Base class
class Upgrade(Slots):
    def __init__(self, name: str, icon: str, level_ref: DictRef, upgrades: dict, hook=None):
        self.name = name
        self.icon = icon
        self._level_ref = level_ref
        self._upgrades = upgrades
        self._hook = hook

    def get_value(self, override_level: int = None):
        if not override_level:
            override_level = self.get_level()
        return self._upgrades[override_level][0]

    def get_next_value(self):
        if self._level_ref.get() + 1 in self._upgrades:
            return self._upgrades[self._level_ref.get() + 1][0]
        else:
            return None

    def get_cost(self):
        if self.get_level() + 1 in self._upgrades:
            return self._upgrades[self.get_level() + 1][1]
        else:
            return None

    def get_level(self):
        return self._level_ref.get()

    def level_up(self):
        self._level_ref.set(self.get_level() + 1)
        if self._hook:
            self._hook()

    def is_max_level(self):
        return (self.get_level() + 1) not in self._upgrades


@dataclass
class MoneyLimit(Upgrade):
    UPGRADES = {
        0: (5000, 0),
        1: (20000, 4000),
        2: (35000, 16000),
        3: (95000, 28000),
        4: (200000, 76000),
        5: (485000, 160000),
        6: (1085000, 388000),
        7: (2540000, 868000)
    }

    def __init__(self, level_ref: DictRef, hook=None):
        super().__init__('Money Limit', 'money', level_ref, MoneyLimit.UPGRADES, hook)


@dataclass
class Garden(Upgrade):
    UPGRADES = {
        0: (50, 0),
        1: (80, 2000),
        2: (125, 4000),
        3: (150, 8000),
        4: (200, 16000),
        5: (300, 32000),
        6: (425, 64000),
        7: (575, 128000),
        8: (750, 256000),
        9: (950, 512000),
        10: (1175, 1024000)
    }

    def __init__(self, level_ref: DictRef, hook=None):
        super().__init__('Garden Production', 'garden', level_ref, Garden.UPGRADES, hook)


class Bank(Upgrade):
    UPGRADES = {
        0: (500, 0),
        1: (1000, 3000),
        2: (3500, 7500),
        3: (7000, 12500),
        4: (12000, 25000),
        5: (25000, 125000),
        6: (50000, 250000),
        7: (100000, 500000)
    }

    def __init__(self, level_ref: DictRef, hook=None):
        super().__init__('Bank Limit', 'bank', level_ref, Bank.UPGRADES, hook)
