import json
import random
from typing import Optional, Any

from db.database import PostgreSQL
from enums.item_type import ItemType
from enums.location import Location
from enums.item_rarity import ItemRarity
from item_data import stat_utils
from item_data.item_classes import ItemDescription, Item
from item_data.stat import Stat, StatType

_ITEMS: dict[int, dict[Location, dict[ItemType, list[ItemDescription]]]] = {
    tier: {location: {itemType: [] for itemType in ItemType} for location in Location} for tier in range(5)
}

_INDEX_TO_ITEM: dict[int, ItemDescription] = {}


def load():
    item_count: int = 0
    with open('game_data/items.json', 'r') as f:
        item_dict: dict[str, Any] = json.load(f)
        for id_k, id_v in item_dict.items():
            tier: int = id_v['Tier']
            location: Location = Location.get_from_name(id_v['Location'])
            item_type: ItemType = ItemType.get_from_name(id_v['Type'])
            desc: ItemDescription = ItemDescription(int(id_k), id_v)
            _ITEMS[tier][location][item_type].append(desc)
            _INDEX_TO_ITEM[int(id_k)] = desc
            item_count += 1
    print(f"Loaded {item_count} items")


def get_stat_bonus(desc: ItemDescription, rarity: ItemRarity) -> dict[Stat, int]:
    base_main: list[Stat] = [x for x in desc.base_stats.keys() if x.get_type() == StatType.MAIN]
    chance_main: list[Stat] = [x for x in desc.base_stats.keys() if x.get_type() == StatType.CHANCE]

    sb: dict[Stat, int] = {}
    if rarity == ItemRarity.COMMON:  # =
        pass

    elif rarity == ItemRarity.UNCOMMON:  # +1
        if chance_main:
            sb[random.choice(chance_main)] = 1
        else:
            sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 1

    elif rarity == ItemRarity.RARE:  # +2
        if chance_main:
            sb[random.choice(chance_main)] = 1
        else:
            sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 1
        if base_main:
            sb[random.choice(base_main)] = 1
        else:
            if chance_main:
                rc = random.choice(chance_main)
                sb[rc] = sb.get(rc, 0) + 1
            else:
                rc = random.choice(Stat.get_type_list(StatType.CHANCE))
                sb[rc] = sb.get(rc, 0) + 1

    elif rarity == ItemRarity.EPIC:  # +3
        first_one = random.randint(1, 2)
        if base_main:
            sb[random.choice(base_main)] = first_one
        else:
            sb[random.choice(Stat.get_type_list(StatType.MAIN))] = first_one
        if chance_main:
            sb[random.choice(chance_main)] = 3 - first_one
        else:
            sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 3 - first_one

    elif rarity == ItemRarity.LEGENDARY:  # +4
        if base_main:
            sb[random.choice(base_main)] = 2
        else:
            sb[random.choice(Stat.get_type_list(StatType.MAIN))] = 2
        if chance_main:
            sb[random.choice(chance_main)] = 2
        else:
            sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 2

    return sb


class RandomItemBuilder:
    def __init__(self, tier: int):
        self.tier: int = tier
        self.location: Location = Location.ANYWHERE
        self.item_type: list[ItemType] = [x for x in ItemType]
        self.item_type_weights: list[int] = [1 for _ in ItemType]
        self.item_rarity: list[ItemRarity] = [x for x in ItemRarity]
        self.item_rarity_weights: list[int] = [1 for _ in ItemRarity]

    def set_location(self, location: Location) -> 'RandomItemBuilder':
        self.location = location
        return self

    def set_type(self, item_type: ItemType) -> 'RandomItemBuilder':
        self.item_type = [item_type]
        self.item_type_weights = [1]
        return self

    def choose_type(self, item_types: list[ItemType], weights: Optional[list[int]]) -> 'RandomItemBuilder':
        self.item_type = item_types
        if weights:
            assert len(weights) == len(item_types)
            self.item_type_weights = weights
        else:
            self.item_type_weights = [1] * len(item_types)
        return self

    def set_rarity(self, rarity: ItemRarity):
        self.item_rarity = [rarity]
        self.item_rarity_weights = [1]
        return self

    def choose_rarity(self, item_rarities: list[ItemRarity], weights: Optional[list[float]] = None)\
            -> 'RandomItemBuilder':
        self.item_rarity = item_rarities
        if weights:
            assert len(weights) == len(item_rarities)
            self.item_rarity_weights = weights
        else:
            self.item_rarity_weights = [1] * len(item_rarities)
        return self

    def build(self):
        item_type: ItemType = random.choices(self.item_type, weights=self.item_type_weights, k=1)[0]
        item_rarity: ItemRarity = random.choices(self.item_rarity, weights=self.item_rarity_weights, k=1)[0]
        desc: ItemDescription = random.choice(_ITEMS[self.tier][self.location][item_type])
        return Item(desc, item_rarity, get_stat_bonus(desc, item_rarity))


def create_guild_item(db: PostgreSQL, guild_id: int, item: Item) -> None:
    fetch_data = db.insert_data("items", {
        'data': item.get_row_data()
    }, returns=True, return_columns=['id'])
    item.id = fetch_data['id']
    db.insert_data("guild_items", {
        'guild_id': guild_id,
        'item_id': item.id
    })


def create_user_item(db: PostgreSQL, user_id: int, item: Item, slot: int) -> None:
    fetch_data = db.insert_data('items', {
        'data': item.get_row_data()
    }, returns=True, return_columns=['id'])
    item.id = fetch_data['id']
    db.insert_data('user_items', {
        'user_id': user_id,
        'item_id': item.id,
        'slot': slot
    })


def delete_user_item(db: PostgreSQL, user_id: int, item: Item) -> None:
    db.delete_row("user_items", dict(user_id=user_id, item_id=item.id))
    db.delete_row("items", dict(id=item.id))
    item.id = -1


def transfer_shop(db: PostgreSQL, guild_id: int, user_id: int, slot: int, item: Item) -> None:
    db.delete_row("guild_items", dict(guild_id=guild_id, item_id=item.id))
    db.insert_data("user_items", dict(user_id=user_id, slot=slot, item_id=item.id))


def from_dict(item_dict: dict[str, Any]):
    desc: ItemDescription = _INDEX_TO_ITEM[item_dict['desc_id']]
    rarity: ItemRarity = ItemRarity.get_from_id(item_dict['rarity'])
    stat_bonus: dict[Stat, int] = stat_utils.unpack_stat_dict(item_dict['stat_bonus'])
    return Item(desc, rarity, stat_bonus, item_dict['durability'])
