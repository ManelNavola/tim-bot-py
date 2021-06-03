# Dictionary
from typing import Callable, Any, Optional

from autoslot import Slots

from enums.emoji import Emoji
from helpers.dictref import DictRef


class Upgrade(Slots):
    def __init__(self, name: str, icon: Emoji, upgrades: dict[int, tuple[Any, int]], locked: bool = False):
        self._name: str = name
        self._icon: Emoji = icon
        self._upgrades: dict[int, tuple[Any, int]] = upgrades
        self._locked = locked

    def get_name(self) -> str:
        return self._name

    def get_icon(self) -> str:
        return self._icon.value

    def get_value(self, level: int) -> object:
        return self._upgrades[level][0]

    def get_cost(self, level: int) -> int:
        return self._upgrades[level + 1][1]

    def is_locked(self) -> bool:
        return self._locked

    def is_max_level(self, level: int) -> bool:
        return (level + 1) not in self._upgrades


class UpgradeLink(Slots):
    def __init__(self, upgrade: Upgrade, lvl_ref: DictRef[int], before: Callable = None, after: Callable = None):
        self._upgrade: Upgrade = upgrade
        self._lvl_ref: DictRef[int] = lvl_ref
        self._before: Optional[Callable] = before
        self._after: Optional[Callable] = after

    def get_name(self):
        return self._upgrade.get_name()

    def get_icon(self):
        return self._upgrade.get_icon()

    def get_value(self, override=None):
        if override is None:
            override = self.get_level()
        return self._upgrade.get_value(override)

    def get_cost(self):
        return self._upgrade.get_cost(self.get_level())

    def get_level(self):
        return self._lvl_ref.get()

    def set_level(self, lvl: int):
        if self._before:
            self._before()
        self._lvl_ref.set(lvl)
        if self._after:
            self._after()

    def level_up(self):
        self.set_level(self.get_level() + 1)

    def is_max_level(self):
        return self._upgrade.is_max_level(self.get_level())


MONEY_LIMIT = Upgrade('Money Limit', Emoji.MONEY, {
    1:  (1000,    0),
    2:  (5000,  800),
    3: (10000, 4000),
})

BANK_LIMIT = Upgrade('Bank Limit', Emoji.BANK, {
    1: (100, 0),
    2: (200, 800),
    3: (400, 1600),
    4: (800, 4800),
    5: (1600, 10000),
})

GARDEN_PROD = Upgrade('Garden Production', Emoji.GARDEN, {
    1: (5, 0),
    2: (12, 1500),
    3: (20, 3300),
    4: (30, 7260),
    5: (40, 15972),
})

INVENTORY_LIMIT = Upgrade('Inventory Limit', Emoji.BAG, {
    1: (4,       0),
    2: (5,    5000),
    3: (6,  50000),
    4: (7, 100000),
    5: (8, 200000),
})
