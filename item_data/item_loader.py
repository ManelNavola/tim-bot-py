import json
from typing import Any, List, Dict

from enums.item_type import EquipmentType, ItemType
from enums.location import Location
from item_data import item_descriptions
from item_data.item_descriptions import ItemDescription, EquipmentDescription, PotionDescription

_EQUIPMENT_DICT: Dict[int, Dict[Location, Dict[EquipmentType, List[EquipmentDescription]]]] = {
    tier: {location: {} for location in Location} for tier in range(5)
}

_POTION_LIST: List[PotionDescription] = []

_INDEX_TO_DESC: Dict[int, ItemDescription] = {}


def load():
    with open('game_data/items.json', 'r') as f:
        item_dict: Dict[str, Dict[str, Any]] = json.load(f)
        equipment_count: int = 0
        for id_k, id_v in item_dict.items():
            item_type: ItemType = ItemType.from_id(id_v['Type'])
            desc_id: int = int(id_k)
            desc: ItemDescription = item_descriptions.item_type_to_desc_class(item_type)(desc_id, id_v)
            _INDEX_TO_DESC[desc_id] = desc
            if item_type == ItemType.EQUIPMENT:
                assert isinstance(desc, EquipmentDescription)
                subtype_list = _EQUIPMENT_DICT[desc.tier][desc.location].get(desc.subtype, [])
                _EQUIPMENT_DICT[desc.tier][desc.location][desc.subtype] = subtype_list + [desc]
                equipment_count += 1
            elif item_type == ItemType.POTION:
                assert isinstance(desc, PotionDescription)
                _POTION_LIST.append(desc)
        print(f"Loaded {equipment_count} equipment")
        print(f"Loaded {len(_POTION_LIST)} potions")


def get_description(desc_id: int) -> ItemDescription:
    return _INDEX_TO_DESC[desc_id]


def get_equipment_dict() -> Dict[int, Dict[Location, Dict[EquipmentType, List[EquipmentDescription]]]]:
    return _EQUIPMENT_DICT


def get_potion_list() -> List[PotionDescription]:
    return _POTION_LIST
