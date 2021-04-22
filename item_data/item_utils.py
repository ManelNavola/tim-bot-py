import json
import random
from typing import Optional, Any

from db.database import PostgreSQL
from enums.item_type import ItemType
from enums.location import Location
from enums.item_rarity import ItemRarity
from item_data import stat_utils
from item_data.item_classes import ItemDescription, Item
from item_data.stat import Stat

_ITEMS: dict[Location, dict[int, dict[ItemType, list[ItemDescription]]]] = {
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
            _ITEMS[location][tier][item_type].append(desc)
            _INDEX_TO_ITEM[int(id_k)] = desc
            item_count += 1
    print(f"Loaded {item_count} items")


def get_stat_bonus(desc: ItemDescription, rarity: ItemRarity) -> dict[Stat, int]:
    sb: dict[Stat, int] = {}
    if rarity == ItemRarity.COMMON:  # =
        pass

    elif rarity == ItemRarity.UNCOMMON:  # +1
        base_stat: Stat = random.choice(list(desc.base_stats.keys()))
        sb[base_stat] = 1

    elif rarity == ItemRarity.RARE:  # +2
        for i in range(2):
            base_stat: Stat = random.choice(list(desc.base_stats.keys()))
            sb[base_stat] = sb.get(base_stat, 0) + 1

    elif rarity == ItemRarity.EPIC:  # +3
        for i in range(2):
            base_stat: Stat = random.choice(list(desc.base_stats.keys()))
            sb[base_stat] = sb.get(base_stat, 0) + 1
        random_stat: Stat = random.choice([x for x in Stat])
        sb[random_stat] = sb.get(random_stat, 0) + 1

    elif rarity == ItemRarity.LEGENDARY:  # +4
        for i in range(2):
            base_stat: Stat = random.choice(list(desc.base_stats.keys()))
            sb[base_stat] = sb.get(base_stat, 0) + 1
        random_stat: Stat = random.choice([x for x in Stat])
        sb[random_stat] = sb.get(random_stat, 0) + 2

    return sb


class RandomItemBuilder:
    def __init__(self, tier: int):
        self.tier: int = tier
        self.item_type: Optional[ItemType] = None
        self.item_rarity: Optional[ItemRarity] = None
        self.location: Optional[Location] = None

    def set_location(self, location: Location) -> 'RandomItemBuilder':
        self.location = location
        return self

    def set_type(self, item_type: ItemType) -> 'RandomItemBuilder':
        self.item_type = item_type
        return self

    def choose_type(self, item_types: list[ItemType], weights: Optional[list[float]] = None)\
            -> 'RandomItemBuilder':
        if weights:
            self.item_type = random.choices(item_types, weights=weights, k=1)[0]
        else:
            self.item_type = random.choice(item_types)
        return self

    def set_rarity(self, rarity: ItemRarity):
        self.item_rarity = rarity
        return self

    def choose_rarity(self, item_types: list[ItemRarity], weights: Optional[list[float]] = None)\
            -> 'RandomItemBuilder':
        if weights:
            self.item_rarity = random.choices(item_types, weights=weights, k=1)[0]
        else:
            self.item_rarity = random.choice(item_types)
        return self

    def build(self):
        if self.location is None:
            self.location = Location.ANYWHERE
        if self.item_type is None:
            self.item_type = random.choice([x for x in ItemType])
        if self.item_rarity is None:
            self.item_rarity = ItemRarity.get_random()
        desc: ItemDescription = random.choice(_ITEMS[self.location][self.tier][self.item_type])
        return Item(desc, self.item_rarity, get_stat_bonus(desc, self.item_rarity))


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
