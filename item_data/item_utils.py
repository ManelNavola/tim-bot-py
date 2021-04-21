import json
import random
from typing import Optional, Any

from db.database import PostgreSQL
from enums.item_type import ItemType
from enums.location import Location
from enums.rarity import Rarity
from item_data import stat_utils
from item_data.item_classes import ItemDescription, Item
from item_data.stat import Stat

_ITEMS: dict[Location, dict[int, dict[ItemType, list[ItemDescription]]]] = {
    location: {tier: {itemType: [] for itemType in ItemType} for tier in range(5)} for location in Location
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


def get_stat_bonus(desc: ItemDescription, rarity: Rarity) -> dict[Stat, int]:
    sb: dict[Stat, int] = {}
    if rarity == Rarity.COMMON:  # =
        pass

    elif rarity == Rarity.UNCOMMON:  # +1
        base_stat: Stat = random.choice(list(desc.base_stats.keys()))
        sb[base_stat] = 1

    elif rarity == Rarity.RARE:  # +2
        for i in range(2):
            base_stat: Stat = random.choice(list(desc.base_stats.keys()))
            sb[base_stat] = sb.get(base_stat, 0) + 1

    elif rarity == Rarity.EPIC:  # +3
        for i in range(2):
            base_stat: Stat = random.choice(list(desc.base_stats.keys()))
            sb[base_stat] = sb.get(base_stat, 0) + 1
        random_stat: Stat = random.choice([x for x in Stat])
        sb[random_stat] = sb.get(random_stat, 0) + 1

    elif rarity == Rarity.LEGENDARY:  # +4
        for i in range(2):
            base_stat: Stat = random.choice(list(desc.base_stats.keys()))
            sb[base_stat] = sb.get(base_stat, 0) + 1
        random_stat: Stat = random.choice([x for x in Stat])
        sb[random_stat] = sb.get(random_stat, 0) + 2

    return sb


def get_random_item(tier: int, location: Location, item_type: Optional[ItemType] = None,
                    rarity: Optional[Rarity] = None) -> Item:
    if tier != 0:
        print('only tier 1 for now!')
        tier = 0

    if item_type is None:
        item_type = random.choice([x for x in ItemType if _ITEMS[location][tier][x]])

    if rarity is None:
        rarity = Rarity.get_random()

    desc: ItemDescription = random.choice(_ITEMS[location][tier][item_type])

    return Item(desc, rarity, get_stat_bonus(desc, rarity))


def create_guild_item(db: PostgreSQL, guild_id: int, item: Item) -> Item:
    fetch_data = db.insert_data("items", {
        'data': item.get_row_data()
    }, returns=True, return_columns=['id'])
    item.id = fetch_data['id']
    db.insert_data("guild_items", {
        'guild_id': guild_id,
        'item_id': item.id
    })
    return item


def create_user_item(db: PostgreSQL, user_id: int, item: Item, slot: int) -> Item:
    fetch_data = db.insert_data('items', {
        'data': item.get_row_data()
    }, returns=True, return_columns=['id'])
    item.id = fetch_data['id']
    db.insert_data('user_items', {
        'user_id': user_id,
        'item_id': item.id,
        'slot': slot
    })
    return item


def delete_user_item(db: PostgreSQL, user_id: int, item: Item) -> None:
    db.delete_row("user_items", dict(user_id=user_id, item_id=item.id))
    db.delete_row("items", dict(id=item.id))
    item.id = -1


def transfer_shop(db: PostgreSQL, guild_id: int, user_id: int, slot: int, item: Item) -> None:
    db.delete_row("guild_items", dict(guild_id=guild_id, item_id=item.id))
    db.insert_data("user_items", dict(user_id=user_id, slot=slot, item_id=item.id))


def from_dict(item_dict: dict[str, Any]):
    desc: ItemDescription = _INDEX_TO_ITEM[item_dict['desc_id']]
    rarity: Rarity = Rarity.get_from_id(item_dict['rarity'])
    stat_bonus: dict[Stat, int] = stat_utils.unpack_stat_dict(item_dict['stat_bonus'])
    return Item(desc, rarity, stat_bonus, item_dict['durability'])


# import random
# from typing import Optional, Any
#
# from db.database import PostgreSQL
# from enums.item_type import ItemType
# from item_data.abilities import AbilityInstance
# from item_data.item_classes import ItemData, ItemDescription, Item
# from enums.rarity import Rarity
# from item_data.stat import Stat
#
#
# ITEM_GENERATION_DATA: dict[str, dict[Rarity, Any]] = {
#     'stat_number': {
#         Rarity.COMMON: (1, 1),
#         Rarity.UNCOMMON: (2, 2),
#         Rarity.RARE: (2, 3),
#         Rarity.EPIC: (3, 4),
#         Rarity.LEGENDARY: (3, 5)
#     },
#     'stat_sum': {
#         Rarity.COMMON: (2, 4),
#         Rarity.UNCOMMON: (5, 7),
#         Rarity.RARE: (8, 10),
#         Rarity.EPIC: (11, 13),
#         Rarity.LEGENDARY: (14, 16)
#     },
#     'ability_chance': {
#         Rarity.COMMON: 0,
#         Rarity.UNCOMMON: 0.05,
#         Rarity.RARE: 0.1,
#         Rarity.EPIC: 0.2,
#         Rarity.LEGENDARY: 0.3
#     }
# }
#
#
# def parse_item_data_from_dict(dictionary: dict):
#     price_modifier = dictionary.get('price')
#     durability = dictionary.get('durability')
#     ability: Optional[AbilityInstance] = None
#     ability_d = dictionary.get('ability')
#     if ability_d is not None:
#         ability = AbilityInstance(decode=ability_d)
#     return ItemData(Rarity.get_by_index(dictionary['rarity']), dictionary['desc_id'],
#                     {Stat.get_by_abv(k): v for k, v in dictionary['stats'].items()},
#                     price_modifier=price_modifier, durability=durability, ability=ability)
#
#
# def get_random_shop_item_data(item_type: Optional[ItemType] = None, rarity: Optional[Rarity] = None):
#     if item_type is None:
#         item_type = random.choice([x for x in ItemType])
#
#     if rarity is None:
#         rarity = Rarity.get_random()
#
#     chosen_desc: ItemDescription = random.choice(ItemDescription.TYPE_TO_ITEMS[item_type])
#
#     stat_number: int = random.randint(*ITEM_GENERATION_DATA['stat_number'][rarity])
#     max_rarity: Rarity = Rarity.get_max_stat_rarity(rarity)
#
#     available_stats: list[Stat] = []
#
#     for stat, weight in chosen_desc.stat_weights.items():
#         if stat.get_rarity().get_id() <= max_rarity.get_id():
#             available_stats.append(stat)
#
#     if stat_number >= len(available_stats):
#         chosen_stats: list[Stat] = available_stats
#         chosen_stats_weights: list[int] = [chosen_desc.stat_weights[stat] for stat in chosen_stats]
#     else:
#         chosen_stats: list[Stat] = []
#         chosen_stats_weights: list[int] = []
#         while stat_number > 0:
#             as_index = random.randint(0, len(available_stats) - 1)
#             stat = available_stats[as_index]
#             chosen_stats.append(stat)
#             chosen_stats_weights.append(chosen_desc.stat_weights[stat])
#             del available_stats[as_index]
#             stat_number -= 1
#
#     stat_sum: int = random.randint(*ITEM_GENERATION_DATA['stat_sum'][rarity])
#     stat_dict: dict[Stat, int] = {}
#     stat_limit: dict[Stat, int] = {stat: stat.get_limit() for stat in chosen_stats}
#
#     while stat_sum > 0:
#         stat = random.choices(chosen_stats, weights=chosen_stats_weights, k=1)[0]
#         stat_dict[stat] = stat_dict.get(stat, 0) + 1
#
#         stat_limit[stat] -= 1
#         if stat_limit[stat] == 0:
#             stat_index = chosen_stats.index(stat)
#             del chosen_stats[stat_index]
#             del chosen_stats_weights[stat_index]
#
#         stat_sum -= 1
#
#     ability: Optional[AbilityInstance] = None
#     # if (chosen_desc.ability is not None) and random.random() < ITEM_GENERATION_DATA['ability_chance'][rarity]:
#     #     pop: list[int] = [0, 1, 2][:chosen_desc.ability.get_tier_amount()]
#     #     wei: list[int] = ABILITY_TIER_CHANCES[:chosen_desc.ability.get_tier_amount()]
#     #     chosen_tier: int = random.choices(pop, weights=wei, k=1)[0]
#     #     ability = AbilityInstance(chosen_desc.ability, chosen_tier)
#
#     return ItemData(rarity, chosen_desc.id, stat_dict, ability=ability)
#
#
# def create_guild_item(db: PostgreSQL, guild_id: int, item_data: ItemData) -> Item:
#     item = Item(item_data=item_data)
#     fetch_data = db.insert_data("items", {
#         'data': item.get_row_data()
#     }, returns=True, return_columns=['id'])
#     item.id = fetch_data['id']
#     db.insert_data("guild_items", {
#         'guild_id': guild_id,
#         'item_id': item.id
#     })
#     return item
#
#
# def create_user_item(db: PostgreSQL, user_id: int, item_data: ItemData) -> Item:
#     item = Item(item_data=item_data)
#     fetch_data = db.insert_data('items', {
#         'data': item.get_row_data()
#     }, returns=True, return_columns=['id'])
#     item.id = fetch_data['id']
#     db.insert_data('user_items', {
#         'user_id': user_id,
#         'item_id': item.id
#     })
#     return item
#
#
# def delete_user_item(db: PostgreSQL, user_id: int, item_id: int) -> None:
#     db.delete_row("user_items", dict(user_id=user_id, item_id=item_id))
#     db.delete_row("items", dict(id=item_id))
#
#
# def transfer_shop(db: PostgreSQL, guild_id: int, user_id: int, slot: int, item_id: int) -> None:
#     db.delete_row("guild_items", dict(guild_id=guild_id, item_id=item_id))
#     db.insert_data("user_items", dict(user_id=user_id, slot=slot, item_id=item_id))
