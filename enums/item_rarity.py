from enum import Enum, unique

from autoslot import Slots


class RarityInstance(Slots):
    def __init__(self, rarity_id: int, name: str, chance: int):
        self.id: int = rarity_id
        self.name: str = name
        self.chance: int = chance


@unique
class ItemRarity(Enum):
    _ignore_ = ['_INFO']
    COMMON = RarityInstance(0, "Common", 100)
    UNCOMMON = RarityInstance(1, "Uncommon", 60)
    RARE = RarityInstance(2, "Rare", 25)
    EPIC = RarityInstance(3, "Epic", 5)
    LEGENDARY = RarityInstance(4, "Legendary", 1)
    _INFO = {}

    @staticmethod
    def get_from_id(rarity_id: int) -> 'ItemRarity':
        return ItemRarity._INFO['from_id'][rarity_id]

    def get_id(self) -> int:
        return self.value.id

    @staticmethod
    def get_from_name(name: str) -> 'ItemRarity':
        return ItemRarity._INFO['from_name'][name]

    def get_name(self) -> str:
        return self.value.name

    def get_chance(self) -> float:
        return self.value.chance

    @staticmethod
    def get_max_stat_rarity(rarity: 'ItemRarity') -> 'ItemRarity':
        return ItemRarity._INFO['max_stat_rarity'][rarity]


ri = {
    'from_id': {x.get_id(): x for x in ItemRarity},
    'from_name': {x.get_name(): x for x in ItemRarity},
    'max_stat_rarity': {
        ItemRarity.COMMON: ItemRarity.COMMON,
        ItemRarity.UNCOMMON: ItemRarity.COMMON,
        ItemRarity.RARE: ItemRarity.UNCOMMON,
        ItemRarity.EPIC: ItemRarity.UNCOMMON,
        ItemRarity.LEGENDARY: ItemRarity.RARE
    }
}

ItemRarity._INFO = ri
