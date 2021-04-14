from typing import Any

import utils
from entities.entity import Entity
from helpers.dictref import DictRef
from item_data.item_classes import Item, ItemDescription
from item_data.stats import StatInstance, Stats


class UserEntity(Entity):
    def __init__(self, name_ref: DictRef[str], persistent_ref: DictRef[dict[str, int]],
                 base_stats: dict[StatInstance, int]):
        super().__init__({})
        self._base_dict = base_stats
        self._persistent_ref: DictRef[dict[str, int]] = persistent_ref
        self._name_ref: DictRef[str] = name_ref
        self._power: int = 0

    def get_power(self) -> int:
        return self._power

    def get_name(self) -> str:
        return self._name_ref.get()

    def set_persistent(self, stat: StatInstance, value: Any) -> None:
        if stat.abv not in self._persistent_ref.get():
            print('Tried setting non existent persistent stat')
            return
        self._persistent_ref.get_update()[stat.abv] = value

    def get_persistent(self, stat: StatInstance, default=0) -> int:
        got = self._persistent_ref.get().get(stat.abv)
        if got is None:
            return default
        return got

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
                dr = self._persistent_ref.get().get(stat.abv)
                if dr is None:
                    dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0)))
                else:
                    dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0),
                                         persistent_value=dr))
        return '\n'.join(dc)

    def print_detailed_refill(self, persistent_refill: dict[StatInstance, int]):
        dc: list[str] = []

        for stat in Stats.get_all():
            if (stat in self._stat_dict) or (stat in self._base_dict):
                dr = self._persistent_ref.get().get(stat.abv)
                if dr is None:
                    dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0)))
                else:
                    pr = persistent_refill.get(stat, 0)
                    if pr == 0:
                        dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0),
                                             persistent_value=dr) + " (Full)")
                    else:
                        dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0),
                                             persistent_value=dr) + f" (Full in {utils.print_time(pr)})")
        return '\n'.join(dc)
