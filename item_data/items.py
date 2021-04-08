import json
import random
from typing import Optional, Any

from autoslot import Slots

import utils
from item_data.abilities import AbilityInstance, Ability
from item_data.item_classes import ItemDescription, ItemType
from item_data.rarity import Rarity, RarityInstance
from db import database
from item_data.stats import Stats, StatInstance

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
        Rarity.COMMON: 0 + 1,
        Rarity.UNCOMMON: 0.05 + 1,
        Rarity.RARE: 0.1 + 1,
        Rarity.EPIC: 0.2 + 1,
        Rarity.LEGENDARY: 0.3 + 1
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


class ItemData(Slots):
    def __init__(self, rarity: RarityInstance, desc_id: int, stats: dict[StatInstance, int],
                 price_modifier: Optional[float] = None, durability: Optional[int] = None,
                 ability: Optional[AbilityInstance] = None):
        self.rarity: RarityInstance = rarity
        self.stats: dict[StatInstance, int] = stats
        self.desc_id: int = desc_id
        self.price_modifier: Optional[float] = price_modifier
        self.durability: Optional[int] = durability
        self.ability: Optional[AbilityInstance] = ability

    def get_description(self) -> ItemDescription:
        return INDEX_TO_ITEM[self.desc_id]


def parse_item_data_from_dict(dictionary: dict):
    price_modifier = dictionary.get('price')
    durability = dictionary.get('durability')
    ability: Optional[AbilityInstance] = None
    ability_d = dictionary.get('ability')
    if ability_d is not None:
        ability = AbilityInstance(decode=ability_d)
    return ItemData(Rarity.get_by_index(dictionary['rarity']), dictionary['desc_id'],
                    {Stats.get_by_abv(k): v for k, v in dictionary['stats'].items()},
                    price_modifier=price_modifier, durability=durability, ability=ability)


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
            'stats': {k.abv: v for k, v in self.data.stats.items()},
            'rarity': self.data.rarity.id,
        }
        if self.data.durability is not None:
            row_data['durability'] = self.data.durability
        if self.data.price_modifier is not None:
            row_data['price'] = self.data.price_modifier
        if self.data.ability is not None:
            row_data['ability'] = self.data.ability.encode()
        return row_data

    def get_price(self, ignore_modifier: bool = False) -> int:
        if ignore_modifier:
            return self._calculate_price(ignore_modifier=True)
        if not self._price:
            self._price = self._calculate_price()
        return self._price

    def _calculate_price(self, ignore_modifier: bool = False):
        stat_sum = sum([v * (k.cost + 1) for k, v in self.data.stats.items()])
        rarity = self.data.rarity.id + 1
        price_mod = 1
        if (self.data.price_modifier is not None) and (not ignore_modifier):
            price_mod = self.data.price_modifier

        ab_mod = 1
        if self.data.ability is not None:
            ab_mod = 1.5

        before_round = (pow(stat_sum, 0.9) * pow(rarity, 1.1) * 10) * price_mod * ab_mod
        return round(before_round / 10) * 10

    def print(self) -> str:
        stats = ', '.join([f"+{v} {k.abv}" for k, v in self.data.stats.items()])
        item_desc: ItemDescription = self.data.get_description()
        if self.data.ability is None:
            return f"{item_desc.type.get_type_icon()}{item_desc.name} {self.data.rarity.name} [{stats}]"
        else:
            return f"{item_desc.type.get_type_icon()}{item_desc.name} {self.data.rarity.name} [{stats}]" \
                   f" | Ability: {self.data.ability.desc.get_name()} " \
                   f"{utils.NUMERAL_TO_ROMAN[self.data.ability.tier + 1]}"


def get_random_shop_item_data(item_type: Optional[ItemType] = None, rarity: Optional[RarityInstance] = None):
    if item_type is None:
        item_type = random.choice(ItemType.get_all())

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

    ability: Optional[AbilityInstance] = None
    if (chosen_desc.ability is not None) and random.random() < ITEM_GENERATION_DATA['ability_chance'][rarity]:
        pop: list[int] = [0, 1, 2][:chosen_desc.ability.get_tier_amount()]
        wei: list[int] = ABILITY_TIER_CHANCES[:chosen_desc.ability.get_tier_amount()]
        chosen_tier: int = random.choices(pop, weights=wei, k=1)[0]
        ability = AbilityInstance(chosen_desc.ability, chosen_tier)

    return ItemData(rarity, chosen_desc.id, chosen_stats_amounts, ability=ability)


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


def transfer_shop(guild_id: int, user_id: int, item_id: int) -> None:
    database.INSTANCE.delete_row("guild_items", dict(guild_id=guild_id, item_id=item_id))
    database.INSTANCE.insert_data("user_items", dict(user_id=user_id, item_id=item_id))
