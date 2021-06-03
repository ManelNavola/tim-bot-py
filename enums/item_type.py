from enum import unique, Enum

from autoslot import Slots

from enums.emoji import Emoji


class EquipmentTypeInstance(Slots):
    def __init__(self, etype_id: int, name: str, icon: Emoji):
        self.id: int = etype_id
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

    def get_id(self) -> int:
        return self.value.id

    def get_icon_str(self) -> str:
        return str(self.value.icon)

    @staticmethod
    def from_name(name: str) -> 'EquipmentType':
        return {
            x.value.name: x for x in EquipmentType
        }[name]

    @staticmethod
    def from_id(eid: int) -> 'EquipmentType':
        return {
            x.value.id: x for x in EquipmentType
        }[eid]

it_dict = {
    'from_name': {x.value.name: x for x in ItemType}
}

ItemType._INFO = it_dict
