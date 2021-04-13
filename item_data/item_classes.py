import json
from typing import Optional, Any

from autoslot import Slots

import utils
from enums.item_type import ItemType
from item_data.abilities import AbilityDesc, AbilityInstance, Ability
from item_data.rarity import RarityInstance
from item_data.stats import StatInstance, Stats


class ItemDescription(Slots):
    ITEMS: list['ItemDescription'] = []
    INDEX_TO_ITEM: dict[int, 'ItemDescription'] = {}
    TYPE_TO_ITEMS: dict[ItemType, list['ItemDescription']] = {}

    def __init__(self, item_id: int, item_type: ItemType, name: str, stat_weights: dict[StatInstance, int],
                 ability: Optional[AbilityDesc] = None):
        self.id = item_id
        self.type: ItemType = item_type
        self.name: str = name
        self.stat_weights: dict[StatInstance, int] = stat_weights
        self.ability: Optional[AbilityDesc] = ability

    @staticmethod
    def load():
        with open('game_data/items.json', 'r') as f:
            item_dict: dict[str, Any] = json.load(f)
            for id_k, id_v in item_dict.items():
                if id_v.get('Ability') is None:
                    ItemDescription.ITEMS.append(ItemDescription(
                        int(id_k), ItemType.get_from_name(id_v['Type']), id_v['Name'], {
                            Stats.get_by_abv(abv): n for abv, n in id_v['Stats'].items()
                        },
                    ))
                else:
                    ItemDescription.ITEMS.append(ItemDescription(
                        int(id_k), ItemType.get_from_name(id_v['Type']), id_v['Name'], {
                            Stats.get_by_abv(abv): n for abv, n in id_v['Stats'].items()
                        }, Ability.get_by_name(id_v['Ability'])
                    ))
            ItemDescription.INDEX_TO_ITEM = {item.id: item for item in ItemDescription.ITEMS}
            ItemDescription.TYPE_TO_ITEMS = {it: [] for it in ItemType.get_all()}

            for item in ItemDescription.ITEMS:
                ItemDescription.TYPE_TO_ITEMS[item.type].append(item)


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
        return ItemDescription.INDEX_TO_ITEM[self.desc_id]


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
            return f"{item_desc.type}{item_desc.name} {self.data.rarity.name} [{stats}]"
        else:
            return f"{item_desc.type}{item_desc.name} {self.data.rarity.name} [{stats}]" \
                   f" | Ability: {self.data.ability.desc.get_name()} " \
                   f"{utils.NUMERAL_TO_ROMAN[self.data.ability.tier + 1]}"
