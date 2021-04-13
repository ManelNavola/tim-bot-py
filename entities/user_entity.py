from typing import Any

from entities.entity import Entity
from helpers.dictref import DictRef
from item_data.item_classes import Item, ItemDescription
from item_data.stats import StatInstance, Stats


class UserEntity(Entity):
    def __init__(self, name_ref: DictRef[str], persistent_ref: dict[StatInstance, DictRef[int]],
                 base_stats: dict[StatInstance, int]):
        super().__init__({})
        self._base_dict = base_stats
        self._persistent_ref: dict[StatInstance, DictRef[int]] = persistent_ref
        self._name_ref: DictRef[str] = name_ref
        self._power: int = 0

    def get_power(self) -> int:
        return self._power

    def get_name(self) -> str:
        return self._name_ref.get()

    def set_persistent(self, stat: StatInstance, value: Any) -> None:
        if stat not in self._persistent_ref:
            print('Tried setting non existant persistent stat')
            return
        self._persistent_ref[stat].set(value)

    def get_persistent(self, stat: StatInstance, default=0) -> Any:
        got = self._persistent_ref.get(stat, None)
        if got is None:
            return default
        return got.get()

    def get_stat_value(self, stat: StatInstance) -> int:
        return self._stat_dict.get(stat, 0) + self._base_dict.get(stat, 0)

    def update_equipment(self, item_list: list[Item]):
        calc_power: float = 0
        self._stat_dict.clear()
        self._available_abilities.clear()
        for item in item_list:
            for stat, value in item.data.stats.items():
                self._stat_dict[stat] = self._stat_dict.get(stat, 0) + value
            if item.data.ability is not None:
                self._available_abilities.append((item.data.ability,
                                                  ItemDescription.INDEX_TO_ITEM[item.data.desc_id].type))
            calc_power += item.get_price()
        self._power = calc_power // 100

    def print_detailed(self):
        dc: list[str] = []

        for stat in Stats.get_all():
            if (stat in self._stat_dict) or (stat in self._base_dict):
                dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0)))
        return '\n'.join(dc)
