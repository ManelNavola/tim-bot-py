from typing import Optional

from autoslot import Slots

from inventory_data.stats import StatInstance, Stats


class AbilityTier(Slots):
    def __init__(self, stat: StatInstance, duration: int, multiplier: float = 1, adder: int = 0, other: bool = False):
        self.stat: StatInstance = stat
        self.duration: int = duration
        self.multiplier: float = multiplier
        self.adder: int = adder
        self.other: bool = other


class AbilityDesc(Slots):
    def __init__(self, ability_id: int, name: str, tiers: list[AbilityTier]):
        self.id: int = ability_id
        self._name: str = name
        self._tiers: list[AbilityTier] = tiers

    def get_name(self):
        return self._name

    def get_tier_amount(self) -> int:
        return len(self._tiers)

    def get_tier(self, tier: int) -> AbilityTier:
        return self._tiers[tier]


class AbilityInstance(Slots):
    def __init__(self, desc: Optional[AbilityDesc] = None, tier: Optional[int] = None,
                 decode: Optional[tuple[int, int]] = None):
        if decode is None:
            self.desc = desc
            self.tier = tier
        else:
            self.desc = Ability.get_by_index(decode[0])
            self.tier = decode[1]

    def get(self):
        return self.desc.get_tier(self.tier)

    def encode(self) -> tuple[int, int]:
        return self.desc.id, self.tier


PROTECTION = AbilityDesc(0, "Protection", [
    AbilityTier(Stats.DEF, 3, multiplier=2),
    AbilityTier(Stats.DEF, 4, multiplier=2),
    AbilityTier(Stats.DEF, 5, multiplier=2)
])

BLUNDER = AbilityDesc(1, "Blunder", [
    AbilityTier(Stats.STUN, 3, adder=20),
    AbilityTier(Stats.STUN, 3, adder=40),
    AbilityTier(Stats.STUN, 3, adder=60)
])

FLEE = AbilityDesc(2, "Flee", [
    AbilityTier(Stats.EVA, 3, adder=20),
    AbilityTier(Stats.EVA, 3, adder=40),
    AbilityTier(Stats.EVA, 3, adder=60)
])

CURSE = AbilityDesc(2, "Curse", [
    AbilityTier(Stats.STR, 2, multiplier=0.8, other=True),
    AbilityTier(Stats.STR, 3, multiplier=0.8, other=True),
    AbilityTier(Stats.STR, 3, multiplier=0.6, other=True)
])


class Ability:
    PROTECTION: AbilityDesc = PROTECTION
    BLUNDER: AbilityDesc = BLUNDER
    FLEE: AbilityDesc = FLEE
    _INDEX: list[AbilityDesc] = [PROTECTION, BLUNDER, FLEE, CURSE]
    _ID_INDEX: dict[int, AbilityDesc] = {ai.id: ai for ai in _INDEX}

    @staticmethod
    def get_by_index(index: int) -> AbilityDesc:
        return Ability._ID_INDEX[index]
