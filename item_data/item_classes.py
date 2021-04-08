from enum import Enum, unique
from typing import Optional

from autoslot import Slots

import utils
from item_data.abilities import AbilityDesc
from item_data.stats import StatInstance


@unique
class ItemType(Enum):
    _ignore_ = ['_type_icons']
    BOOT = 0
    CHEST = 1
    HELMET = 2
    WEAPON = 3
    SECONDARY = 4
    _type_icons = {}

    @staticmethod
    def get_type_icons_dict() -> dict['ItemType', str]:
        return {
            ItemType.BOOT: utils.Emoji.BOOTS,
            ItemType.CHEST: utils.Emoji.CHEST_PLATE,
            ItemType.HELMET: utils.Emoji.HELMET,
            ItemType.WEAPON: utils.Emoji.WEAPON,
            ItemType.SECONDARY: utils.Emoji.SHIELD
        }

    @staticmethod
    def get_from_type_icon(icon: str) -> Optional['ItemType']:
        for k, v in ItemType.get_type_icons_dict().items():
            if v.startswith(icon):
                return k
        return None

    @staticmethod
    def get_from_name(name: str) -> Optional['ItemType']:
        d: dict[str, ItemType] = {
            "Boot": ItemType.BOOT,
            "Chest": ItemType.CHEST,
            "Helmet": ItemType.HELMET,
            "Weapon": ItemType.WEAPON,
            "Secondary": ItemType.SECONDARY
        }
        return d[name]

    def get_name(self) -> str:
        d: dict[ItemType, str] = {
            ItemType.BOOT: "Boot",
            ItemType.CHEST: "Chest",
            ItemType.HELMET: "Helmet",
            ItemType.WEAPON: "Weapon",
            ItemType.SECONDARY: "Secondary"
        }
        return d[self]

    @staticmethod
    def get_all() -> list['ItemType']:
        return list(ItemType.get_type_icons_dict().keys())

    def get_type_icon(self) -> str:
        return ItemType.get_type_icons_dict()[self]


class ItemDescription(Slots):
    def __init__(self, item_id: int, item_type: ItemType, name: str, stat_weights: dict[StatInstance, int],
                 ability: Optional[AbilityDesc] = None):
        self.id = item_id
        self.type: ItemType = item_type
        self.name: str = name
        self.stat_weights: dict[StatInstance, int] = stat_weights
        self.ability: Optional[AbilityDesc] = ability
