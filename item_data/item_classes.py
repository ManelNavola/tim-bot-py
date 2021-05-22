from typing import Any, Optional

from autoslot import Slots

from enums.item_type import ItemType
from item_data import stat_utils
from enums.item_rarity import ItemRarity
from item_data.stat import Stat


class ItemDescription(Slots):
    def __init__(self, key: int, data: dict[str, Any]):
        self.id: int = key
        self.name: str = data['Name']
        self.type: ItemType = ItemType.get_from_name(data['Type'])
        self.tier: int = data['Tier']
        self.base_stats: dict[Stat, int] = stat_utils.unpack_stat_dict(data['Stats'])


class Item:
    def __init__(self, description: ItemDescription, rarity: ItemRarity, stat_bonus: dict[Stat, int] = None):
        self.id: int = -1
        self.price_modifier: Optional[int] = None
        self._description: ItemDescription = description
        self._rarity: ItemRarity = rarity
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
            'rarity': self._rarity.get_id()
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
