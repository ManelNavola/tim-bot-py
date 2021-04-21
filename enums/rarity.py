import random
from enum import Enum, unique

from autoslot import Slots


class RarityInstance(Slots):
    def __init__(self, rarity_id: int, name: str, chance_weight: float):
        self.id: int = rarity_id
        self.name: str = name
        self.chance_weight: float = chance_weight


@unique
class Rarity(Enum):
    _ignore_ = ['_INFO']
    COMMON = RarityInstance(0, "Common", 52.35)
    UNCOMMON = RarityInstance(1, "Uncommon", 31.41)
    RARE = RarityInstance(2, "Rare", 13.08)
    EPIC = RarityInstance(3, "Epic", 2.61)
    LEGENDARY = RarityInstance(4, "Legendary", 0.52)
    _INFO = {}

    @staticmethod
    def get_from_id(rarity_id: int) -> 'Rarity':
        return Rarity._INFO['from_id'][rarity_id]

    def get_id(self):
        return self.value.id

    def get_name(self):
        return self.value.name

    @staticmethod
    def get_random() -> 'Rarity':
        return random.choices([x for x in Rarity], weights=[x.value.chance_weight for x in Rarity])[0]

    @staticmethod
    def get_max_stat_rarity(rarity: 'Rarity') -> 'Rarity':
        return Rarity._INFO['max_stat_rarity'][rarity]


ri = {
    'from_id': {x.get_id(): x for x in Rarity},
    'max_stat_rarity': {
        Rarity.COMMON: Rarity.COMMON,
        Rarity.UNCOMMON: Rarity.COMMON,
        Rarity.RARE: Rarity.UNCOMMON,
        Rarity.EPIC: Rarity.UNCOMMON,
        Rarity.LEGENDARY: Rarity.RARE
    }
}

Rarity._INFO = ri
