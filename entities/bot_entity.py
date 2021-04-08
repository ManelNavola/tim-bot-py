from typing import Optional

from entities.entity import Entity
from item_data.abilities import AbilityInstance
from item_data.stats import StatInstance, Stats


class BotEntityBuilder:
    def __init__(self, name: str, stat_dict: dict[StatInstance, int],
                 abilities: Optional[list[AbilityInstance]] = None):
        if not abilities:
            abilities = []
        self.abilities: list[AbilityInstance] = abilities
        self.stat_dict: dict[StatInstance, int] = stat_dict
        self.name = name

    def instance(self):
        return BotEntity(self.name, self.stat_dict.copy(), [ab for ab in self.abilities])


class BotEntity(Entity):
    def __init__(self, name: str, stat_dict: dict[StatInstance, int],
                 abilities: Optional[list[AbilityInstance]] = None):
        super().__init__(stat_dict)
        self._name: str = name
        self._current_hp: int = Stats.HP.get_value(stat_dict.get(Stats.HP, 0))
        self._current_mp: int = Stats.MP.get_value(stat_dict.get(Stats.MP, 0))
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
