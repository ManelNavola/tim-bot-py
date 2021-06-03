from typing import Any, Type

from enums.item_type import ItemType, EquipmentType
from enums.location import Location
from item_data.stat import Stat
from item_data.stat_modifier import StatModifier


class ItemDescription:
    def __init__(self, desc_id: int, data_dict: dict[str, Any]):
        self.name: str = data_dict['Name']
        self.id: int = desc_id
        self.type: ItemType = ItemType.from_id(data_dict['Type'])


class EquipmentDescription(ItemDescription):
    def __init__(self, desc_id: int, data_dict: dict[str, Any]):
        super().__init__(desc_id, data_dict)
        self.subtype: EquipmentType = EquipmentType.from_id(data_dict['Subtype'])
        self.tier: int = data_dict['Tier']
        self.location: Location = Location.from_id(data_dict['Location'])
        self.base_stats: dict[Stat, int] = EquipmentDescription.unpack_stat_dict(data_dict['Stats'])

    @staticmethod
    def pack_stat_dict(stats: dict[Stat, int]):
        return {
            stat.get_abv(): value for stat, value in stats.items()
        }

    @staticmethod
    def unpack_stat_dict(stats: dict[str, int]):
        return {
            Stat.get_by_abv(abv): value for abv, value in stats.items()
        }


class PotionDescription(ItemDescription):
    def __init__(self, desc_id: int, data_dict: dict[str, Any]):
        super().__init__(desc_id, data_dict)
        self.stat_modifiers: list[StatModifier] = [StatModifier.from_dict(md) for md in data_dict['Modifiers']]


def item_type_to_desc_class(item_type: ItemType) -> Type[ItemDescription]:
    return {
        ItemType.EQUIPMENT: EquipmentDescription,
        ItemType.POTION: PotionDescription
    }[item_type]
