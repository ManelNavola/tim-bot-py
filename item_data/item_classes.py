from typing import Optional

from autoslot import Slots

from enums.item_type import ItemType
from item_data.abilities import AbilityDesc
from item_data.stats import StatInstance


class ItemDescription(Slots):
    def __init__(self, item_id: int, item_type: ItemType, name: str, stat_weights: dict[StatInstance, int],
                 ability: Optional[AbilityDesc] = None):
        self.id = item_id
        self.type: ItemType = item_type
        self.name: str = name
        self.stat_weights: dict[StatInstance, int] = stat_weights
        self.ability: Optional[AbilityDesc] = ability
