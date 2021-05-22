from entities.ai.base_ai import BotAI
# from item_data.abilities import AbilityInstance
from entities.entity import Entity
from item_data.abilities import AbilityEnum
from item_data.stat import Stat


class BotEntity(Entity):
    def __init__(self, name: str, stat_dict: dict[Stat, int], ai: BotAI, abilities: list[AbilityEnum] = None):
        super().__init__(stat_dict)
        self._name: str = name
        if abilities:
            self._available_abilities = abilities
        self._ai: BotAI = ai
        self._persistent_stats = {stat: stat.get_value(stat_dict[stat])
                                  for stat in Stat
                                  if stat.is_persistent() and stat in stat_dict}

    def get_ai(self) -> BotAI:
        return self._ai

    def get_name(self) -> str:
        return self._name

    def print_detailed(self) -> str:
        dc: list[str] = []
        for stat in Stat.get_all():
            if stat in self._stat_dict:
                dc.append(stat.print(self._stat_dict.get(stat, 0)))
        return '\n'.join(dc)
