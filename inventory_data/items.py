from enum import Enum, unique
import random
from typing import Optional

from autoslot import Slots

import utils
from inventory_data.rarity import Rarity, RarityInstance
from db import database
from inventory_data.stats import Stats, StatInstance

ITEM_GENERATION_DATA: dict[str, dict[RarityInstance, tuple[int, int]]] = {
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
    }
}


@unique
class ItemType(Enum):
    BOOT = 0
    CHEST = 1
    HELMET = 2
    WEAPON = 3
    SECONDARY = 4

    TYPE_ICONS = {
        BOOT: utils.Emoji.BOOTS,
        CHEST: utils.Emoji.CHEST_PLATE,
        HELMET: utils.Emoji.HELMET,
        WEAPON: utils.Emoji.WEAPON,
        SECONDARY: utils.Emoji.SHIELD
    }

    def get_type_icon(self):
        return self.TYPE_ICONS.value[self.value]

    @staticmethod
    def get_length() -> int:
        return 5


class ItemDescription(Slots):
    def __init__(self, item_id: int, item_type: ItemType, name: str, stat_weights: dict[StatInstance, int]):
        self.id = item_id
        self.type: ItemType = item_type
        self.name: str = name
        self.stat_weights: dict[StatInstance, int] = stat_weights


_ITEMS: list[ItemDescription] = [
    ItemDescription(0, ItemType.BOOT, "Leather Boots", {Stats.SPD: 2, Stats.EVA: 1}),
    ItemDescription(1, ItemType.CHEST, "Breastplate", {Stats.HP: 1, Stats.DEF: 2}),
    ItemDescription(2, ItemType.HELMET, "Metal Helmet", {Stats.HP: 1, Stats.DEF: 1, Stats.EVA: 1}),
    ItemDescription(3, ItemType.WEAPON, "Iron Sword", {Stats.STR: 1, Stats.VAMP: 1}),
    ItemDescription(4, ItemType.SECONDARY, "Wooden Shield", {Stats.DEF: 1, Stats.CONT: 1})
]

INDEX_TO_ITEM: dict[int, ItemDescription] = {item.id: item for item in _ITEMS}

TYPE_TO_ITEMS: dict[ItemType, list[ItemDescription]] = {ItemType(i): [] for i in range(ItemType.get_length())}

for item in _ITEMS:
    TYPE_TO_ITEMS[item.type].append(item)


class ItemData(Slots):
    def __init__(self, rarity: RarityInstance, desc_id: int, stats: dict[StatInstance, int], price_modifier: float = 1,
                 durability: int = 100):
        self.rarity: RarityInstance = rarity
        self.stats: dict[StatInstance, int] = stats
        self.desc_id: int = desc_id
        self.price_modifier: float = price_modifier
        self.durability: int = durability

    def get_description(self) -> ItemDescription:
        return INDEX_TO_ITEM[self.desc_id]


def parse_item_data_from_dict(dictionary: dict):
    price_modifier = dictionary.get('price')
    durability = dictionary.get('durability')
    return ItemData(Rarity.get_by_index(dictionary['rarity']), dictionary['desc_id'],
                    {Stats.get_by_name(k): v for k, v in dictionary['stats'].items()}, price_modifier, durability)


class Item(Slots):
    def __init__(self, item_data: ItemData = None, item_id: int = -1):
        assert (item_data is not None) or (item_id is not None), "You can't create an Item with empty arguments"
        self.id: int = item_id
        self.data: ItemData = item_data
        self._price: Optional[int] = None
        self.durability: int = 100

    def get_row_data(self):
        row_data = {
            'desc_id': self.data.desc_id,
            'stats': {k.name: v for k, v in self.data.stats.items()},
            'rarity': self.data.rarity.id,
            'price': self.data.price_modifier,
            'durability': self.data.durability
        }
        return row_data

    def get_price(self) -> int:
        if not self._price:
            self._calculate_price()
        return self._price

    def _calculate_price(self) -> None:
        stat_sum = sum([v * (k.cost + 1) for k, v in self.data.stats.items()])
        rarity = self.data.rarity.id + 1
        before_round = (pow(stat_sum, 0.9) * pow(rarity, 1.1) * 10) * self.data.price_modifier
        self._price = round(before_round / 10) * 10

    def print(self) -> str:
        stats = ', '.join([f"+{v} {k.abv}" for k, v in self.data.stats.items()])
        item_desc: ItemDescription = self.data.get_description()
        return f"{item_desc.type.get_type_icon()}{item_desc.name} {self.data.rarity.name} [{stats}]"


def get_random_item(item_type: Optional[ItemType] = None, rarity: Optional[RarityInstance] = None):
    if item_type is None:
        item_type = ItemType(random.randrange(0, ItemType.get_length()))

    if rarity is None:
        rarity = Rarity.get_random()

    chosen_desc: ItemDescription = random.choice(TYPE_TO_ITEMS[item_type])

    stat_number: int = random.randint(*ITEM_GENERATION_DATA['stat_number'][rarity])
    stat_sum: int = random.randint(*ITEM_GENERATION_DATA['stat_sum'][rarity])
    max_rarity: RarityInstance = Rarity.get_max_stat_rarity(rarity)

    available_stats: list = []
    chosen_stats: list = []
    chosen_stats_amounts: dict = {}

    for stat, chance in chosen_desc.stat_weights.items():
        if stat.rarity.id <= max_rarity.id:
            available_stats += [stat] * chance

    while stat_number > 0:
        index = random.randrange(0, len(available_stats))
        stat = available_stats[index]
        chosen_stats.append(stat)
        chosen_stats_amounts[stat] = 0
        stat_number -= 1

    while stat_sum > 0:
        stat = random.choice(chosen_stats)
        chosen_stats_amounts[stat] = chosen_stats_amounts.get(stat, 0) + 1
        stat_sum -= 1

    return ItemData(rarity, chosen_desc.id, chosen_stats_amounts)


def create_guild_item(guild_id: int, item_data: ItemData) -> Item:
    item = Item(item_data=item_data)
    fetch_data = database.INSTANCE.insert_data("items", {
        'data': item.get_row_data()
    }, must_return=['id'])
    item.id = fetch_data['id']
    database.INSTANCE.insert_data("guild_items", {
        'guild_id': guild_id,
        'item_id': item.id
    })
    return item


def delete_user_item(user_id: int, item_id: int) -> None:
    database.INSTANCE.delete_row("user_items", dict(user_id=user_id, item_id=item_id))
    database.INSTANCE.delete_row("items", dict(id=item_id))


def transfer(guild_id: int, user_id: int, item_id: int) -> None:
    database.INSTANCE.delete_row("guild_items", dict(guild_id=guild_id, item_id=item_id))
    database.INSTANCE.insert_data("user_items", dict(user_id=user_id, item_id=item_id))
