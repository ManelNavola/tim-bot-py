from typing import Optional

from utils import DictRef
from inventory_data.items import Item
from inventory_data.stats import StatInstance, Stats
from abc import ABCMeta, abstractmethod


class Entity(metaclass=ABCMeta):
    def __init__(self, stat_dict: dict[StatInstance, int]):
        self._stat_dict: dict[StatInstance, int] = stat_dict
        self._simple_cached: Optional[str] = None
        self._detailed_cached: Optional[str] = None

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_current_hp(self) -> int:
        pass

    @abstractmethod
    def get_current_mp(self) -> int:
        pass

    @abstractmethod
    def set_current_health(self, amount: int) -> None:
        pass

    def _refill_print(self) -> None:
        sc = []
        dc = []

        if self._stat_dict.get(Stats.HP) is None:
            sc.append(f"{Stats.HP.abv}: {self.get_current_hp()}/{self.get_stat(Stats.HP)}")
            dc.append(f"{Stats.HP.icon} {Stats.HP.abv}: {self.get_current_hp()}/{self.get_stat(Stats.HP)}")

        else:
            sc.append(f"{Stats.HP.abv}: {self.get_current_hp()}/{self.get_stat(Stats.HP)}")
            dc.append(f"{Stats.HP.icon} {Stats.HP.abv}: {self.get_current_hp()}/{self.get_stat(Stats.HP)}"
                      f"+{self._stat_dict.get(Stats.HP, 0)}")

        if self._stat_dict.get(Stats.MP) is None:
            sc.append(f"{Stats.MP.abv}: {self.get_current_mp()}/{self.get_stat(Stats.MP)}")
            dc.append(f"{Stats.MP.icon} {Stats.MP.abv}: {self.get_current_mp()}/{self.get_stat(Stats.MP)}")
        else:
            sc.append(f"{Stats.MP.abv}: {self.get_current_mp()}/{self.get_stat(Stats.MP)}")
            dc.append(f"{Stats.MP.icon} {Stats.MP.abv}: {self.get_current_mp()}/{self.get_stat(Stats.MP)}"
                      f"+{self._stat_dict.get(Stats.MP, 0)}")

        for stat in Stats.get_all():
            if stat in self._stat_dict:
                if stat not in [Stats.HP, Stats.MP]:
                    sc.append(f"{stat.abv}: {self.get_stat(stat)}")
                    dc.append(f"{stat.icon} {stat.abv}: +{self.get_stat(stat)}")

        self._simple_cached = ', '.join(sc)
        self._detailed_cached = '\n'.join(dc)

    def get_stat(self, stat: StatInstance) -> int:
        return stat.get_value(self._stat_dict.get(stat, 0))

    def print_simple(self):
        if not self._simple_cached:
            self._refill_print()
        return self._simple_cached

    def print_detailed(self):
        if not self._detailed_cached:
            self._refill_print()
        return self._detailed_cached

    def damage(self, other: 'Entity') -> int:
        dealt = other.get_stat(Stats.STR)
        if dealt <= 0:
            return 0
        br: float = (dealt / (dealt + self.get_stat(Stats.DEF))) * dealt
        real_amount = max(1, int(round(br)))
        self.set_current_health(max(0, self.get_current_hp() - real_amount))
        self._simple_cached = None
        return real_amount


class BotEntity(Entity):
    def __init__(self, name: str, max_hp: int, max_mp: int, stat_dict: dict[StatInstance, int]):
        stat_dict.update({
            Stats.HP: max_hp - Stats.HP.base,
            Stats.MP: max_mp - Stats.MP.base
        })
        super().__init__(stat_dict)
        self._name: str = name
        self._current_hp: int = max_hp
        self._current_mp: int = max_mp

    def get_name(self) -> str:
        return self._name

    def get_current_hp(self) -> int:
        return self._current_hp

    def get_current_mp(self) -> int:
        return self._current_mp

    def set_current_health(self, amount: int) -> None:
        self._current_hp = amount


class UserEntity(Entity):
    def __init__(self, name_ref: DictRef, hp_ref: DictRef, mp_ref: DictRef):
        super().__init__({})
        self._stat_dict: dict[StatInstance, int] = {}
        self._mp_ref: DictRef = mp_ref
        self._hp_ref: DictRef = hp_ref
        self._name_ref: DictRef = name_ref
        self._stat_sum: int = 0

    def get_stat_sum(self) -> int:
        return self._stat_sum

    def get_name(self) -> str:
        return self._name_ref.get()

    def get_current_hp(self) -> int:
        return self._hp_ref.get()

    def get_current_mp(self) -> int:
        return self._mp_ref.get()

    def set_current_health(self, amount: int) -> None:
        self._hp_ref.set(amount)

    def update_items(self, item_list: list[Item]):
        self._stat_sum = 0
        self._stat_dict.clear()
        for item in item_list:
            for stat, value in item.data.stats.items():
                self._stat_dict[stat] = self._stat_dict.get(stat, 0) + value
                self._stat_sum += value
