from abc import ABCMeta, abstractmethod
from typing import Optional

from item_data.abilities import AbilityInstance
from item_data.item_classes import ItemType
from item_data.stats import Stats, StatInstance


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
