from enum import unique, Enum

from autoslot import Slots

from enums.emoji import Emoji


class EquipmentTypeInstance(Slots):
    def __init__(self, etype_id: int, name: str, icon: Emoji):
        self.id: int = etype_id
        self.icon: Emoji = icon
        self.name: str = name


@unique
class EquipmentType(Enum):
    HELMET = EquipmentTypeInstance(2, 'Helmet', Emoji.HELMET)
    CHEST = EquipmentTypeInstance(1, 'Chest', Emoji.CHEST_PLATE)
    WEAPON = EquipmentTypeInstance(3, 'Weapon', Emoji.WEAPON)
    SECONDARY = EquipmentTypeInstance(4, 'Secondary', Emoji.SHIELD)
    BOOT = EquipmentTypeInstance(0, 'Boot', Emoji.BOOTS)

    def __str__(self) -> str:
        return str(self.value.icon)

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


class ItemTypeInstance(Slots):
    def __init__(self, iid: int):
        self.id: int = iid


@unique
class ItemType(Enum):
    EQUIPMENT = ItemTypeInstance(0)
    POTION = ItemTypeInstance(1)
    MATERIAL = ItemTypeInstance(2)

    def get_id(self) -> int:
        return self.value.id

    @staticmethod
    def from_id(it_id: int) -> 'ItemType':
        return {
            x.value.id: x for x in ItemType
        }[it_id]
