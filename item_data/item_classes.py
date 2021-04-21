from typing import Any, Optional

from autoslot import Slots

from enums.item_type import ItemType
from item_data import stat_utils
from enums.rarity import Rarity
from item_data.stat import Stat


class ItemDescription(Slots):
    def __init__(self, key: int, data: dict[str, Any]):
        self.id: int = key
        self.name: str = data['Name']
        self.type: ItemType = ItemType.get_from_name(data['Type'])
        self.tier: int = data['Tier']
        self.base_stats: dict[Stat, int] = stat_utils.unpack_stat_dict(data['Stats'])


class Item:
    def __init__(self, description: ItemDescription, rarity: Rarity, stat_bonus: dict[Stat, int] = None,
                 durability: int = 100):
        self.id: int = -1
        self.price_modifier: Optional[int] = None
        self.durability: int = durability
        self._description: ItemDescription = description
        self._rarity: Rarity = rarity
        if stat_bonus is None:
            stat_bonus = {}
        self._stat_bonus: dict[Stat, int] = stat_bonus

    def get_description(self) -> ItemDescription:
        return self._description

    def get_stats(self):
        stats: dict[Stat, int] = self._description.base_stats.copy()
        for stat, value in self._stat_bonus.items():
            stats[stat] = stats.get(stat, 0) + value
        return stats

    def get_row_data(self):
        tr = {
            'desc_id': self._description.id,
            'stat_bonus': stat_utils.pack_stat_dict(self._stat_bonus),
            'rarity': self._rarity.get_id(),
            'durability': self.durability,
        }
        if self.price_modifier is not None:
            tr['price_modifier'] = self.price_modifier
        return tr

    def get_price(self, ignore_modifier: bool = False):
        stat_dict: dict[Stat, int] = self.get_stats()
        stat_sum = sum([v * (k.value.cost + 1) for k, v in stat_dict.items()])
        rarity = self._rarity.get_id() + 1
        price_mod = 1
        if (self.price_modifier is not None) and (not ignore_modifier):
            price_mod = self.price_modifier

        before_round = (stat_sum * pow(rarity, 0.5) * 10) * price_mod
        return round(before_round / 10) * 10

    def print(self) -> str:
        stat_dict: dict[Stat, int] = self.get_stats()
        stats = ', '.join([f"+{v} {k.get_abv()}" for k, v in stat_dict.items()])
        return f"{self._description.type} _{self._rarity.get_name()}_ {self._description.name} [{stats}]"


# class ItemDescription(Slots):
#     ITEMS: list['ItemDescription'] = []
#     INDEX_TO_ITEM: dict[int, 'ItemDescription'] = {}
#     TYPE_TO_ITEMS: dict[ItemType, list['ItemDescription']] = {}
#
#     def __init__(self, item_id: int, item_type: ItemType, name: str, stat_weights: dict[Stat, int],
#                  ability: Optional[AbilityDesc] = None):
#         self.id = item_id
#         self.type: ItemType = item_type
#         self.name: str = name
#         self.stat_weights: dict[Stat, int] = stat_weights
#         self.ability: Optional[AbilityDesc] = ability
#
#     @staticmethod
#     def load():
#         with open('game_data/items.json', 'r') as f:
#             item_dict: dict[str, Any] = json.load(f)
#             for id_k, id_v in item_dict.items():
#                 if id_v.get('Ability') is None:
#                     ItemDescription.ITEMS.append(ItemDescription(
#                         int(id_k), ItemType.get_from_name(id_v['Type']), id_v['Name'], {
#                             Stat.get_by_abv(abv): n for abv, n in id_v['Stats'].items()
#                         },
#                     ))
#                 else:
#                     ItemDescription.ITEMS.append(ItemDescription(
#                         int(id_k), ItemType.get_from_name(id_v['Type']), id_v['Name'], {
#                             Stat.get_by_abv(abv): n for abv, n in id_v['Stats'].items()
#                         }, Ability.get_by_name(id_v['Ability'])
#                     ))
#             ItemDescription.INDEX_TO_ITEM = {item.id: item for item in ItemDescription.ITEMS}
#             ItemDescription.TYPE_TO_ITEMS = {it: [] for it in ItemType}
#
#             for item in ItemDescription.ITEMS:
#                 ItemDescription.TYPE_TO_ITEMS[item.type].append(item)
#
#
# class ItemData(Slots):
#     def __init__(self, rarity: Rarity, desc_id: int, stats: dict[Stat, int],
#                  price_modifier: Optional[float] = None, durability: Optional[int] = None,
#                  ability: Optional[AbilityInstance] = None):
#         self.rarity: Rarity = rarity
#         self.stats: dict[Stat, int] = stats
#         self.desc_id: int = desc_id
#         self.price_modifier: Optional[float] = price_modifier
#         self.durability: Optional[int] = durability
#         self.ability: Optional[AbilityInstance] = ability
#
#     def get_description(self) -> ItemDescription:
#         return ItemDescription.INDEX_TO_ITEM[self.desc_id]
#
#     def calculate_price(self, ignore_modifier: bool = False):
#         stat_sum = sum([v * (k.value.cost + 1) for k, v in self.stats.items()])
#         rarity = self.rarity.get_id() + 1
#         price_mod = 1
#         if (self.price_modifier is not None) and (not ignore_modifier):
#             price_mod = self.price_modifier
#
#         ab_mod = 1
#         if self.ability is not None:
#             ab_mod = 1.5
#
#         before_round = (pow(stat_sum, 0.9) * pow(rarity, 1.1) * 10) * price_mod * ab_mod
#         return round(before_round / 10) * 10
#
#     def print(self) -> str:
#         stats = ', '.join([f"+{v} {k.get_abv()}" for k, v in self.stats.items()])
#         item_desc: ItemDescription = self.get_description()
#         if self.ability is None:
#             return f"{item_desc.type}{item_desc.name} {self.rarity.get_name()} [{stats}]"
#         else:
#             return f"{item_desc.type}{item_desc.name} {self.rarity.get_name()} [{stats}]" \
#                    f" | Ability: {self.ability.desc.get_name()} " \
#                    f"{utils.NUMERAL_TO_ROMAN[self.ability.tier + 1]}"
#
#
# class Item(Slots):
#     def __init__(self, item_data: ItemData = None, item_id: int = -1):
#         assert (item_data is not None) or (item_id is not None), "You can't create an Item with empty arguments"
#         self.id: int = item_id
#         self.data: ItemData = item_data
#         self._price: Optional[int] = None
#         self.durability: int = 100
#
#     def get_price(self, ignore_modifier: bool = False) -> int:
#         if ignore_modifier:
#             return self.data.calculate_price(ignore_modifier=True)
#         if not self._price:
#             self._price = self.data.calculate_price()
#         return self._price
#
#     def get_row_data(self):
#         row_data = {
#             'desc_id': self.data.desc_id,
#             'stats': {k.get_abv(): v for k, v in self.data.stats.items()},
#             'rarity': self.data.rarity.get_id(),
#         }
#         if self.data.durability is not None:
#             row_data['durability'] = self.data.durability
#         if self.data.price_modifier is not None:
#             row_data['price'] = self.data.price_modifier
#         if self.data.ability is not None:
#             row_data['ability'] = self.data.ability.encode()
#         return row_data
#
#     def print(self) -> str:
#         return self.data.print()
