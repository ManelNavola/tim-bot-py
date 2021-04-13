from abc import ABCMeta, abstractmethod
from typing import Optional, Any

from item_data.abilities import AbilityInstance
from enums.item_type import ItemType
from item_data.stats import StatInstance


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
    def set_persistent(self, stat: StatInstance, value: Any) -> None:
        pass

    @abstractmethod
    def get_persistent(self, stat: StatInstance, default=None) -> Any:
        pass

    @abstractmethod
    def get_stat_value(self, stat: StatInstance) -> int:
        pass

    @abstractmethod
    def print_detailed(self) -> str:
        pass
