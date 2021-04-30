from entities.entity import Entity
from helpers.dictref import DictRef
from item_data.item_classes import Item
from item_data.stat import Stat
from enums.user_class import UserClass


class UserEntity(Entity):
    def __init__(self, name_ref: DictRef[str]):
        super().__init__({})
        self._base_dict: dict[Stat, int] = {}
        self._name_ref: DictRef[str] = name_ref
        self._power: int = 0

    def set_class(self, user_class: UserClass):
        self._base_dict = user_class.get_stats()
        self.reset()

    def reset(self):
        self.clear_modifiers()
        self._persistent_stats.clear()
        for stat in Stat:
            if stat.is_persistent():
                sv = self._stat_dict.get(stat, 0) + self._base_dict.get(stat, 0)
                if sv > 0:
                    self._persistent_stats[stat] = stat.get_value(sv)

    def get_power(self) -> int:
        return self._power

    def get_name(self) -> str:
        return self._name_ref.get()

    def get_stat_value(self, stat: Stat) -> int:
        return self._stat_dict.get(stat, 0) + self._base_dict.get(stat, 0)

    def update_equipment(self, item_list: list[Item]):
        calc_power: float = 0
        self._stat_dict.clear()
        # self._available_abilities.clear()
        for item in item_list:
            for stat, value in item.get_stats().items():
                self._stat_dict[stat] = self._stat_dict.get(stat, 0) + value
            # if item.data.ability is not None:
            #     self._available_abilities.append((item.data.ability,
            #                                       ItemDescription.INDEX_TO_ITEM[item.data.desc_id].type))
            calc_power += item.get_price()
        self._power = calc_power // 100
        self.reset()

    def print_detailed(self):
        dc: list[str] = []

        for stat in Stat:
            if (stat in self._stat_dict) or (stat in self._base_dict) or (stat.is_persistent()):
                dr = self._persistent_stats.get(stat)
                if dr is None:
                    dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0)))
                else:
                    dc.append(stat.print(self._stat_dict.get(stat, 0), self._base_dict.get(stat, 0),
                                         persistent_value=dr))
        return '\n'.join(dc)
