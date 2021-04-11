import random
from typing import Optional

from db import database
from enums.item_type import ItemType
from item_data.abilities import AbilityInstance
from item_data.item_classes import ItemData, ItemDescription, Item
from item_data.items import TYPE_TO_ITEMS, ITEM_GENERATION_DATA, ABILITY_TIER_CHANCES
from item_data.rarity import Rarity, RarityInstance
from item_data.stats import Stats


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
