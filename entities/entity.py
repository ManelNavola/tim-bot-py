from abc import ABCMeta, abstractmethod
from typing import Optional, Any

from adventure_classes.generic.stat_modifier import StatModifier
from item_data.abilities import AbilityInstance
from enums.item_type import ItemType
from item_data.stat import Stat


class Entity(metaclass=ABCMeta):
    def __init__(self, stat_dict: dict[Stat, int], modifiers: list[StatModifier] = None):
        self._stat_dict: dict[Stat, int] = stat_dict
        self._available_abilities: list[tuple[AbilityInstance, Optional[ItemType]]] = []
        self._persistent_stats: dict[Stat, int] = {}
        if modifiers is None:
            modifiers = []
        self._entity_modifiers: list[StatModifier] = modifiers

    def add_modifier(self, modifier: StatModifier):
        self._entity_modifiers.append(modifier)

    def end_battle(self):
        for i in range(len(self._entity_modifiers) - 1, -1, -1):
            self._entity_modifiers[i].duration -= 1
            if self._entity_modifiers[i].duration == 0:
                del self._entity_modifiers[i]

    def get_modifiers(self):
        return self._entity_modifiers

    def clear_modifiers(self):
        self._entity_modifiers.clear()

    def get_abilities(self) -> list[tuple[AbilityInstance, Optional[ItemType]]]:
        return self._available_abilities

    @abstractmethod
    def get_name(self) -> str:
        pass

    def change_persistent(self, stat: Stat, value: Any) -> None:
        new_value = self.get_persistent(stat) + value
        max_value = stat.get_value(self.get_stat_value(stat))
        if new_value > max_value:
            new_value = max_value
        elif new_value < 0:
            new_value = 0
        self._persistent_stats[stat] = new_value

    def get_persistent(self, stat: Stat) -> Optional[int]:
        return self._persistent_stats.get(stat)

    @abstractmethod
    def get_stat_value(self, stat: Stat) -> int:
        pass

    @abstractmethod
    def print_detailed(self) -> str:
        pass
