from typing import Optional

from entities.ai.base_ai import BotAI, BaseBotAI
from entities.entity import Entity
# from item_data.abilities import AbilityInstance
from enums.item_type import ItemType
from item_data.abilities import Ability
from item_data.stat import Stat


class BotEntityBuilder:
    def __init__(self, name: str, stat_dict: dict[Stat, int], enemy_id: Optional[int] = None):
        # abilities: Optional[list[AbilityInstance]] = None, ):
        # if not abilities:
        #    abilities = []
        # self.abilities: list[AbilityInstance] = abilities
        self.stat_dict: dict[Stat, int] = stat_dict
        self.name = name
        self.enemy_id: Optional[int] = enemy_id

    def instance(self):
        return BotEntity(self.name, self.stat_dict.copy())
        # [ab for ab in self.abilities])


class BotEntity(Entity):
    def __init__(self, name: str, stat_dict: dict[Stat, int], abilities: list[Ability] = None, ai: BotAI = BaseBotAI()):
        super().__init__(stat_dict)
        if abilities:
            self._available_abilities = abilities
        self._name: str = name
        self._ai: BotAI = ai
        self._persistent_stats = {stat: stat.get_value(stat_dict[stat])
                                  for stat in Stat
                                  if stat.is_persistent() and stat in stat_dict}

    def get_name(self) -> str:
        return self._name

    def get_stat_value(self, stat: Stat) -> int:
        return self._stat_dict.get(stat, 0)

    def print_detailed(self) -> str:
        dc: list[str] = []
        for stat in Stat.get_all():
            if stat in self._stat_dict:
                dc.append(stat.print(self._stat_dict.get(stat, 0)))
        return '\n'.join(dc)
