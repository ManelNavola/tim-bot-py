from abc import abstractmethod, ABC
from typing import Optional, Dict, List

from item_data.stat_modifier import StatModifier
from item_data.abilities import AbilityContainer
from item_data.stat import Stat


class Entity(ABC):
    def __init__(self, stat_dict: Dict[Stat, int], modifiers: List[StatModifier] = None):
        self._stat_dict: Dict[Stat, int] = stat_dict
        self._abilities: List[AbilityContainer] = []
        self._persistent_stats: Dict[Stat, int] = {}
        if modifiers is None:
            modifiers = []
        self._stat_modifiers: List[StatModifier] = modifiers

    def add_modifier(self, modifier: StatModifier) -> None:
        if modifier.persistent:
            self.set_persistent_value(modifier.stat, round(modifier.apply(self.get_persistent_value(modifier.stat))))
        else:
            self._stat_modifiers.append(modifier)

    def get_modifiers(self) -> List[StatModifier]:
        return self._stat_modifiers

    def step_turn_modifiers(self):
        for i in range(len(self._stat_modifiers) - 1, -1, -1):
            if self._stat_modifiers[i].per_battle:
                continue
            self._stat_modifiers[i].duration -= 1
            if self._stat_modifiers[i].duration == 0:
                del self._stat_modifiers[i]

    def step_battle_modifiers(self):
        for i in range(len(self._stat_modifiers) - 1, -1, -1):
            if self._stat_modifiers[i].per_battle:
                self._stat_modifiers[i].duration -= 1
                if self._stat_modifiers[i].duration == 0:
                    del self._stat_modifiers[i]

    def clear_stat_modifiers(self) -> None:
        self._stat_modifiers.clear()

    def get_stat(self, stat: Stat, default: Optional[int] = 0) -> Optional[int]:
        return self._stat_dict.get(stat, default)

    def reset(self) -> None:
        self.clear_stat_modifiers()
        self._persistent_stats.clear()
        for stat in Stat:
            if stat.is_persistent():
                sv = self.get_stat(stat)
                self._persistent_stats[stat] = stat.get_value(sv)

    def get_abilities(self) -> List[AbilityContainer]:
        return self._abilities

    def set_abilities(self, abilities: List[AbilityContainer]) -> None:
        self._abilities = abilities

    @abstractmethod
    def get_name(self) -> str:
        pass

    def get_stat_dict(self) -> Dict[Stat, int]:
        return self._stat_dict

    def set_persistent_value(self, stat: Stat, new_value: int) -> None:
        max_value = stat.get_value(self.get_stat(stat))
        if new_value > max_value:
            new_value = max_value
        elif new_value < 0:
            new_value = 0
        self._persistent_stats[stat] = new_value

    def change_persistent_value(self, stat: Stat, value: int) -> None:
        self.set_persistent_value(stat, self.get_persistent_value(stat) + value)

    def get_persistent_value(self, stat: Stat) -> Optional[int]:
        return self._persistent_stats.get(stat)

    @abstractmethod
    def print_detailed(self) -> str:
        pass
