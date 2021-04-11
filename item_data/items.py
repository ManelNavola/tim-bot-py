import json

from typing import Any

from item_data.abilities import Ability

from enums.item_type import ItemType

from item_data.item_classes import ItemDescription
from item_data.rarity import Rarity, RarityInstance
from item_data.stats import Stats

ITEM_GENERATION_DATA: dict[str, dict[RarityInstance, Any]] = {
    'stat_number': {
        Rarity.COMMON: (1, 1),
        Rarity.UNCOMMON: (2, 2),
        Rarity.RARE: (2, 3),
        Rarity.EPIC: (3, 4),
        Rarity.LEGENDARY: (3, 5)
    },
    'stat_sum': {
        Rarity.COMMON: (2, 4),
        Rarity.UNCOMMON: (5, 7),
        Rarity.RARE: (8, 10),
        Rarity.EPIC: (11, 13),
        Rarity.LEGENDARY: (14, 16)
    },
    'ability_chance': {
        Rarity.COMMON: 0,
        Rarity.UNCOMMON: 0.05,
        Rarity.RARE: 0.1,
        Rarity.EPIC: 0.2,
        Rarity.LEGENDARY: 0.3
    }
}

ABILITY_TIER_CHANCES = [100, 40, 8]


_ITEMS: list[ItemDescription] = []

with open('game_data/items.json', 'r') as f:
    item_dict: dict[str, Any] = json.load(f)
    for id_k, id_v in item_dict.items():
        if id_v.get('Ability') is None:
            _ITEMS.append(ItemDescription(
                int(id_k), ItemType.get_from_name(id_v['Type']), id_v['Name'], {
                    Stats.get_by_abv(abv): n for abv, n in id_v['Stats'].items()
                },
            ))
        else:
            _ITEMS.append(ItemDescription(
                int(id_k), ItemType.get_from_name(id_v['Type']), id_v['Name'], {
                    Stats.get_by_abv(abv): n for abv, n in id_v['Stats'].items()
                }, Ability.get_by_name(id_v['Ability'])
            ))


INDEX_TO_ITEM: dict[int, ItemDescription] = {item.id: item for item in _ITEMS}

TYPE_TO_ITEMS: dict[ItemType, list[ItemDescription]] = {it: [] for it in ItemType.get_all()}

for item in _ITEMS:
    TYPE_TO_ITEMS[item.type].append(item)
