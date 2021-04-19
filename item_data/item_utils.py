import random
from typing import Optional, Any

from db.database import PostgreSQL
from enums.item_type import ItemType
from item_data.abilities import AbilityInstance
from item_data.item_classes import ItemData, ItemDescription, Item
from item_data.rarity import Rarity, RarityInstance
from item_data.stat import Stat


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


def parse_item_data_from_dict(dictionary: dict):
    price_modifier = dictionary.get('price')
    durability = dictionary.get('durability')
    ability: Optional[AbilityInstance] = None
    ability_d = dictionary.get('ability')
    if ability_d is not None:
        ability = AbilityInstance(decode=ability_d)
    return ItemData(Rarity.get_by_index(dictionary['rarity']), dictionary['desc_id'],
                    {Stat.get_by_abv(k): v for k, v in dictionary['stats'].items()},
                    price_modifier=price_modifier, durability=durability, ability=ability)


def get_random_shop_item_data(item_type: Optional[ItemType] = None, rarity: Optional[RarityInstance] = None):
    if item_type is None:
        item_type = random.choice(ItemType.get_all())

    if rarity is None:
        rarity = Rarity.get_random()

    chosen_desc: ItemDescription = random.choice(ItemDescription.TYPE_TO_ITEMS[item_type])

    stat_number: int = random.randint(*ITEM_GENERATION_DATA['stat_number'][rarity])
    max_rarity: RarityInstance = Rarity.get_max_stat_rarity(rarity)

    available_stats: list[Stat] = []

    for stat, weight in chosen_desc.stat_weights.items():
        if stat.rarity.id <= max_rarity.id:
            available_stats.append(stat)

    if stat_number >= len(available_stats):
        chosen_stats: list[Stat] = available_stats
        chosen_stats_weights: list[int] = [chosen_desc.stat_weights[stat] for stat in chosen_stats]
    else:
        chosen_stats: list[Stat] = []
        chosen_stats_weights: list[int] = []
        while stat_number > 0:
            as_index = random.randint(0, len(available_stats) - 1)
            stat = available_stats[as_index]
            chosen_stats.append(stat)
            chosen_stats_weights.append(chosen_desc.stat_weights[stat])
            del available_stats[as_index]
            stat_number -= 1

    stat_sum: int = random.randint(*ITEM_GENERATION_DATA['stat_sum'][rarity])
    stat_dict: dict[Stat, int] = {}
    stat_limit: dict[Stat, int] = {stat: stat.limit for stat in chosen_stats}

    while stat_sum > 0:
        stat = random.choices(chosen_stats, weights=chosen_stats_weights, k=1)[0]
        stat_dict[stat] = stat_dict.get(stat, 0) + 1

        stat_limit[stat] -= 1
        if stat_limit[stat] == 0:
            stat_index = chosen_stats.index(stat)
            del chosen_stats[stat_index]
            del chosen_stats_weights[stat_index]

        stat_sum -= 1

    ability: Optional[AbilityInstance] = None
    # if (chosen_desc.ability is not None) and random.random() < ITEM_GENERATION_DATA['ability_chance'][rarity]:
    #     pop: list[int] = [0, 1, 2][:chosen_desc.ability.get_tier_amount()]
    #     wei: list[int] = ABILITY_TIER_CHANCES[:chosen_desc.ability.get_tier_amount()]
    #     chosen_tier: int = random.choices(pop, weights=wei, k=1)[0]
    #     ability = AbilityInstance(chosen_desc.ability, chosen_tier)

    return ItemData(rarity, chosen_desc.id, stat_dict, ability=ability)


def create_guild_item(db: PostgreSQL, guild_id: int, item_data: ItemData) -> Item:
    item = Item(item_data=item_data)
    fetch_data = db.insert_data("items", {
        'data': item.get_row_data()
    }, returns=True, return_columns=['id'])
    item.id = fetch_data['id']
    db.insert_data("guild_items", {
        'guild_id': guild_id,
        'item_id': item.id
    })
    return item


def create_user_item(db: PostgreSQL, user_id: int, item_data: ItemData) -> Item:
    item = Item(item_data=item_data)
    fetch_data = db.insert_data('items', {
        'data': item.get_row_data()
    }, returns=True, return_columns=['id'])
    item.id = fetch_data['id']
    db.insert_data('user_items', {
        'user_id': user_id,
        'item_id': item.id
    })
    return item


def delete_user_item(db: PostgreSQL, user_id: int, item_id: int) -> None:
    db.delete_row("user_items", dict(user_id=user_id, item_id=item_id))
    db.delete_row("items", dict(id=item_id))


def transfer_shop(db: PostgreSQL, guild_id: int, user_id: int, slot: int, item_id: int) -> None:
    db.delete_row("guild_items", dict(guild_id=guild_id, item_id=item_id))
    db.insert_data("user_items", dict(user_id=user_id, slot=slot, item_id=item_id))
