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
    1: (2500, 0),
    2: (10000, 2000),
    3: (50000, 8000),
    4: (100000, 40000),
    5: (500000, 80000),
    6: (1000000, 400000)
})

BANK_LIMIT = Upgrade('Bank Limit', Emoji.BANK, {
    1: (200, 0),
    2: (400, 500),
    3: (800, 1200),
    4: (1600, 3200),
    5: (3200, 6400),
    6: (6400, 12800),
    7: (12800, 25600),
    8: (25600, 51200),
    9: (51200, 102400),
    10: (102400, 204800),
    11: (204800, 409600),
    12: (409600, 819200)
})

GARDEN_PROD = Upgrade('Garden Production', Emoji.GARDEN, {
    1: (25, 0),
    2: (35, 1500),
    3: (50, 3300),
    4: (75, 7260),
    5: (100, 15972),
    6: (125, 35138),
    7: (150, 77304),
    8: (175, 170070),
    9: (200, 374154),
    10: (225, 823138)
})

INVENTORY_LIMIT = Upgrade('Inventory Limit', Emoji.BAG, {
    1: (4, 0),
    2: (5, 1000),
    3: (6, 2000),
    4: (7, 5000),
    5: (8, 10000),
    6: (9, 50000),
    7: (10, 100000),
    8: (11, 200000),
    9: (12, 500000),
    10: (13, 1000000)
})
