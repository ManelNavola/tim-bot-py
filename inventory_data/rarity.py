import random

from autoslot import Slots


class RarityInstance(Slots):
    def __init__(self, rarity_id: int, name: str, chance: int):
        self.id: int = rarity_id
        self.name: str = name
        self.chance: int = chance


class Rarity:
    COMMON: RarityInstance = RarityInstance(0, "I", 100)
    UNCOMMON: RarityInstance = RarityInstance(1, "II", 60)
    RARE: RarityInstance = RarityInstance(2, "III", 25)
    EPIC: RarityInstance = RarityInstance(3, "IV", 5)
    LEGENDARY: RarityInstance = RarityInstance(4, "V", 1)
    _INDEX: dict[int, RarityInstance] = {x.id: x for x in [COMMON, UNCOMMON, RARE, EPIC, LEGENDARY]}
    _MAX_STAT_RARITY: dict[RarityInstance, RarityInstance] = {
        COMMON: COMMON,
        UNCOMMON: COMMON,
        RARE: UNCOMMON,
        EPIC: UNCOMMON,
        LEGENDARY: RARE
    }

    @staticmethod
    def get_by_index(index: int) -> RarityInstance:
        return Rarity._INDEX[index]

    @staticmethod
    def get_random() -> RarityInstance:
        return random.choices(list(Rarity._INDEX.values()), weights=[x.chance for x in Rarity._INDEX.values()])[0]

    @staticmethod
    def get_max_stat_rarity(rarity_instance: RarityInstance) -> RarityInstance:
        return Rarity._MAX_STAT_RARITY[rarity_instance]
