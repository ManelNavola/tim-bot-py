from enum import unique, Enum
from typing import Optional

from autoslot import Slots

from enums.emoji import Emoji


class ItemTypeInstance(Slots):
    def __init__(self, name: str, icon: Emoji):
        self.icon: Emoji = icon
        self.name: str = name


@unique
class ItemType(Enum):
    _ignore_ = ['_INFO']
    BOOT = ItemTypeInstance('Boot', Emoji.BOOTS)
    CHEST = ItemTypeInstance('Chest', Emoji.CHEST_PLATE)
    HELMET = ItemTypeInstance('Helmet', Emoji.HELMET)
    WEAPON = ItemTypeInstance('Weapon', Emoji.WEAPON)
    SECONDARY = ItemTypeInstance('Secondary', Emoji.SHIELD)
    _INFO = {}

    def __str__(self) -> str:
        return str(self.value.icon)

    @staticmethod
    def get_from_name(name: str) -> Optional['ItemType']:
        return ItemType._INFO['from_name'].get(name)

    def get_name(self) -> str:
        return self.value.name

    def get_icon_str(self) -> str:
        return str(self.value.icon)


it_dict = {
    'from_name': {x.value.name: x for x in ItemType}
}

ItemType._INFO = it_dict
