from typing import Optional, List, Dict

from autoslot import Slots

from entities.ai.base_ai import BotAI, BaseBotAI
from entities.bot_entity import BotEntity
from item_data.abilities import AbilityEnum
from item_data.stat import Stat


class BotEntityBuilder(Slots):
    def __init__(self, name: str, stat_dict: Dict[Stat, int], enemy_id: Optional[int] = None, ai: BotAI = BaseBotAI()):
        # abilities: Optional[list[AbilityInstance]] = None, ):
        # if not abilities:
        #    abilities = []
        # self.abilities: list[AbilityInstance] = abilities
        self.stat_dict: Dict[Stat, int] = stat_dict
        self.name: str = name
        self.enemy_id: Optional[int] = enemy_id
        self.ai: BotAI = ai
        self.abilities: List[AbilityEnum] = []

    def instance(self, bot_ai: Optional[BotAI] = None):
        if bot_ai is not None:
            return BotEntity(self.name, self.stat_dict.copy(), bot_ai, self.abilities)
        else:
            return BotEntity(self.name, self.stat_dict.copy(), self.ai, self.abilities)
