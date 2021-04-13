from enum import unique
from typing import Optional

from autoslot import Slots

from enums.emoji import Emoji
from enums.enum_plus import EnumPlus


class ItemTypeInfo(Slots):
    def __init__(self, name: str, icon: Emoji):
        self.icon: Emoji = icon
        self.name: str = name


@unique
class ItemType(EnumPlus):
    _ignore_ = ['_ITEM_TYPE_INFO']
    BOOT = 0
    CHEST = 1
    HELMET = 2
    WEAPON = 3
    SECONDARY = 4
    _ITEM_TYPE_INFO = {}

    @classmethod
    def get_all(cls) -> list['ItemType']:
        return list(cls)

    def __str__(self) -> str:
        return self.get_icon_str()

    @staticmethod
    def get_from_icon(other: str) -> Optional['ItemType']:
        for it, iti in ItemType._ITEM_TYPE_INFO['items']:
            if iti.icon.compare(other):
                return it
        return None

    @staticmethod
    def get_from_name(name: str) -> Optional['ItemType']:
        return ItemType._ITEM_TYPE_INFO['from_name'].get(name)

    def get_name(self) -> str:
        return ItemType._ITEM_TYPE_INFO['items'][self].name

    def get_icon_str(self) -> str:
        return str(ItemType._ITEM_TYPE_INFO['items'][self].icon)


iti_dict = {
    'items': {
        ItemType.BOOT: ItemTypeInfo('Boot', Emoji.BOOTS),
        ItemType.CHEST: ItemTypeInfo('Chest', Emoji.CHEST_PLATE),
        ItemType.HELMET: ItemTypeInfo('Helmet', Emoji.HELMET),
        ItemType.WEAPON: ItemTypeInfo('Weapon', Emoji.WEAPON),
        ItemType.SECONDARY: ItemTypeInfo('Secondary', Emoji.SHIELD),
    }
}

iti_dict['from_name'] = {iti.name: it for it, iti in iti_dict['items'].items()}

ItemType._ITEM_TYPE_INFO = iti_dict
