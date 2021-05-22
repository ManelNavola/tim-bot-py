from abc import abstractmethod, ABC
from typing import Optional

from adventure_classes.generic.stat_modifier import StatModifier
from item_data.abilities import AbilityContainer
from item_data.stat import Stat


class Entity(ABC):
    def __init__(self, stat_dict: dict[Stat, int], modifiers: list[StatModifier] = None):
        self._stat_dict: dict[Stat, int] = stat_dict
        self._abilities: list[AbilityContainer] = []
        self._persistent_stats: dict[Stat, int] = {}
        if modifiers is None:
            modifiers = []
        self._battle_modifiers: list[StatModifier] = modifiers

    def add_battle_modifier(self, modifier: StatModifier) -> None:
        self._battle_modifiers.append(modifier)

    def get_battle_modifiers(self) -> list[StatModifier]:
        return self._battle_modifiers

    def step_battle_modifiers(self):
        for i in range(len(self._battle_modifiers) - 1, -1, -1):
            self._battle_modifiers[i].duration -= 1
            if self._battle_modifiers[i].duration == 0:
                del self._battle_modifiers[i]

    def clear_battle_modifiers(self) -> None:
        self._battle_modifiers.clear()

    def get_stat(self, stat: Stat, default: Optional[int] = 0) -> Optional[int]:
        return self._stat_dict.get(stat, default)

    def reset(self) -> None:
        self.clear_battle_modifiers()
        self._persistent_stats.clear()
        for stat in Stat:
            if stat.is_persistent():
                sv = self.get_stat(stat)
                self._persistent_stats[stat] = stat.get_value(sv)

    def get_abilities(self) -> list[AbilityContainer]:
        return self._abilities

    def set_abilities(self, abilities: list[AbilityContainer]) -> None:
        self._abilities = abilities

    @abstractmethod
    def get_name(self) -> str:
        pass

    def get_stat_dict(self) -> dict[Stat, int]:
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
