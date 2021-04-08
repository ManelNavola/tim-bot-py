from typing import Optional

from item_data import items
from item_data.abilities import AbilityInstance
from utils import DictRef
from item_data.items import Item, ItemType
from item_data.stats import StatInstance, Stats
from abc import ABCMeta, abstractmethod


class Entity(metaclass=ABCMeta):
    def __init__(self, stat_dict: dict[StatInstance, int]):
        self._stat_dict: dict[StatInstance, int] = stat_dict
        self._available_abilities: list[tuple[AbilityInstance, Optional[ItemType]]] = []

    def get_abilities(self) -> list[tuple[AbilityInstance, Optional[ItemType]]]:
        return self._available_abilities

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

    def get_stat_dict(self) -> dict[StatInstance, int]:
        return self._stat_dict

    def get_stat(self, stat: StatInstance):
        return self._stat_dict.get(stat, 0)

    def print_detailed(self):
        dc: list[str] = [Stats.HP.print(self.get_stat(Stats.HP), persistent_value=self.get_current_hp()),
                         Stats.MP.print(self.get_stat(Stats.MP), persistent_value=self.get_current_mp())]

        for stat in Stats.get_all():
            if (stat in self._stat_dict) or (stat.base > 0):
                if stat not in [Stats.HP, Stats.MP]:
                    dc.append(stat.print(self.get_stat(stat)))

        return '\n'.join(dc)


class BotEntityBuilder:
    def __init__(self, name: str, max_hp: int, max_mp: int, stat_dict: dict[StatInstance, int],
                 abilities: Optional[list[AbilityInstance]] = None):
        if not abilities:
            abilities = []
        self.abilities: list[AbilityInstance] = abilities
        self.stat_dict: dict[StatInstance, int] = stat_dict
        self.max_mp: int = max_mp
        self.max_hp: int = max_hp
        self.name = name

    def instance(self):
        return BotEntity(self.name, self.max_hp, self.max_mp, self.stat_dict.copy(), [ab for ab in self.abilities])


class BotEntity(Entity):
    def __init__(self, name: str, max_hp: int, max_mp: int, stat_dict: dict[StatInstance, int],
                 abilities: Optional[list[AbilityInstance]] = None):
        stat_dict.update({
            Stats.HP: max_hp - Stats.HP.base,
            Stats.MP: max_mp - Stats.MP.base,
        })
        super().__init__(stat_dict)
        self._name: str = name
        self._current_hp: int = max_hp
        self._current_mp: int = max_mp
        if abilities is not None:
            self._available_abilities = abilities

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
        self._power: int = 0

    def get_power(self) -> int:
        return self._power

    def get_name(self) -> str:
        return self._name_ref.get()

    def get_current_hp(self) -> int:
        return self._hp_ref.get()

    def get_current_mp(self) -> int:
        return self._mp_ref.get()

    def set_current_health(self, amount: int) -> None:
        self._hp_ref.set(amount)

    def update_equipment(self, item_list: list[Item]):
        calc_power: float = 0
        self._stat_dict.clear()
        self._available_abilities.clear()
        for item in item_list:
            for stat, value in item.data.stats.items():
                self._stat_dict[stat] = self._stat_dict.get(stat, 0) + value
            if item.data.ability is not None:
                self._available_abilities.append((item.data.ability, items.INDEX_TO_ITEM[item.data.desc_id].type))
            calc_power += item.get_price()
        self._power = calc_power // 100
