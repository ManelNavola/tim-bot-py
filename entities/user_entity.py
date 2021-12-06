from typing import Optional, List, Dict

from entities.entity import Entity
from enums.item_type import EquipmentType
from helpers.dictref import DictRef
from item_data.item_classes import Equipment
from item_data.stat import Stat
from enums.user_class import UserClass


class UserEntity(Entity):
    def __init__(self, name_ref: DictRef[str]):
        super().__init__({})
        self._base_dict: Dict[Stat, int] = {}
        self._name_ref: DictRef[str] = name_ref
        self._power: int = 0

    def get_name(self) -> str:
        return self._name_ref.get()

    def set_class(self, user_class: UserClass) -> None:
        self._base_dict = user_class.get_stats()
        self.reset()

    def get_power(self) -> int:
        return self._power

    def get_stat(self, stat: Stat, default: Optional[int] = 0) -> Optional[int]:
        if default is None:
            fs: Optional[int] = self._stat_dict.get(stat, default)
            if fs is None:
                return None
            else:
                ss: Optional[int] = self._base_dict.get(stat, default)
                if ss is None:
                    return None
                else:
                    return fs + ss
        else:
            return self._stat_dict.get(stat, default) + self._base_dict.get(stat, default)

    def update_equipment(self, item_list: Dict[EquipmentType, Equipment]):
        self._stat_dict.clear()
        # self._available_abilities.clear()
        for equipment in item_list.values():
            for stat, value in equipment.get_stats().items():
                self._stat_dict[stat] = self._stat_dict.get(stat, 0) + value
            # if item.data.ability is not None:
            #     self._available_abilities.append((item.data.ability,
            #                                       ItemDescription.INDEX_TO_ITEM[item.data.desc_id].type))
        self._power = round(sum(stat.get_type().get_weighted_value() * count
                                for stat, count in self._stat_dict.items()))
        self.reset()

    def print_detailed(self):
        dc: List[str] = []

        for stat in Stat:
            if (stat in self._stat_dict) or (stat in self._base_dict) or (stat.is_persistent()):
                dr = self._persistent_stats.get(stat)
                if dr is None:
                    dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0)))
                else:
                    dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0),
                                         persistent_value=dr))
        return '\n'.join(dc)
