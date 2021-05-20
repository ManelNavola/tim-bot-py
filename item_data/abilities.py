import typing
from abc import ABC, abstractmethod

# from typing import Optional

# from autoslot import Slots

# import utils
from autoslot import Slots

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle_entity_old import BattleEntity


class Ability(ABC):
    def init(self, targets: list['BattleEntity']) -> None:
        pass

    @staticmethod
    def get_duration() -> int:
        return 0

    @staticmethod
    def allow_self() -> bool:
        return False

    @staticmethod
    @abstractmethod
    def get_cost() -> int:
        pass

    def turn(self, targets: list['BattleEntity']):
        pass

    def end(self, targets: list['BattleEntity']):
        pass


class AbilityInstance(Slots):
    def __init__(self, ability: Ability, targets: list[BattleEntity]):
        self.duration_remaining = ability.get_duration()
        self.ability = ability
        self.targets = targets


class Summon(Ability):
    def get_cost(self) -> int:
        return 6

    def init(self, targets: list['BattleEntity']) -> None:
        pass


ABILITIES: dict[int, Ability] = {
    0: Summon()
}


def get_ability(ability_id: int) -> Ability:
    return ABILITIES[ability_id]

# class AbilityTier(Slots):
#     def __init__(self, stat: Stat, duration: int, multiplier: float = 1, adder: int = 0, other: bool = False):
#         self.stat: Stat = stat
#         self.duration: int = duration
#         self.multiplier: float = multiplier
#         self.adder: int = adder
#         self.other: bool = other
#
#     def print(self) -> str:
#         if self.multiplier != 1:
#             return f"x{self.multiplier} {self.stat.abv}/{self.duration} turns"
#         else:
#             return f"+{self.adder} {self.stat.abv}/{self.duration} turns"
#
#
# class AbilityDesc(Slots):
#     def __init__(self, ability_id: int, name: str, tiers: list[AbilityTier]):
#         self.id: int = ability_id
#         self._name: str = name
#         self._tiers: list[AbilityTier] = tiers
#
#     def get_name(self):
#         return self._name
#
#     def get_tier_amount(self) -> int:
#         return len(self._tiers)
#
#     def get_tier(self, tier: int) -> AbilityTier:
#         return self._tiers[tier]
#
#
# class AbilityInstance(Slots):
#     def __init__(self, desc: Optional[AbilityDesc] = None, tier: Optional[int] = None,
#                  decode: Optional[tuple[int, int]] = None):
#         if decode is None:
#             self.desc = desc
#             self.tier = tier
#         else:
#             self.desc = Ability.get_by_index(decode[0])
#             self.tier = decode[1]
#
#     def get_effect(self) -> str:
#         if self.get().multiplier != 1:
#             if self.get().other:
#                 return f"x{self.get().multiplier:.2f} {self.get().stat.abv}
#                 on opponent for {self.get().duration} turns"
#             else:
#                 return f"x{self.get().multiplier:.2f} {self.get().stat.abv} for {self.get().duration} turns"
#         elif self.get().adder != 0:
#             if self.get().other:
#                 return f"+{self.get().adder} {self.get().stat.abv} on opponent for {self.get().duration} turns"
#             else:
#                 return f"+{self.get().adder} {self.get().stat.abv} for {self.get().duration} turns"
#
#     def get_name(self) -> str:
#         return f"{self.desc.get_name()} {utils.NUMERAL_TO_ROMAN[self.tier + 1]}"
#
#     def get(self) -> AbilityTier:
#         return self.desc.get_tier(self.tier)
#
#     def encode(self) -> tuple[int, int]:
#         return self.desc.id, self.tier
#
#
# ABILITY_TIER_CHANCES = [100, 40, 8]
#
#
# PROTECTION = AbilityDesc(0, "Protection", [
#     AbilityTier(Stat.DEF, 3, multiplier=2),
#     AbilityTier(Stat.DEF, 4, multiplier=2),
#     AbilityTier(Stat.DEF, 5, multiplier=2)
# ])
#
# FLEE = AbilityDesc(2, "Flee", [
#     AbilityTier(Stat.EVA, 3, adder=20),
#     AbilityTier(Stat.EVA, 3, adder=40),
#     AbilityTier(Stat.EVA, 3, adder=60)
# ])
#
# CURSE = AbilityDesc(3, "Curse", [
#     AbilityTier(Stat.STR, 2, multiplier=0.8, other=True),
#     AbilityTier(Stat.STR, 3, multiplier=0.8, other=True),
#     AbilityTier(Stat.STR, 3, multiplier=0.6, other=True)
# ])
#
#
# class Ability:
#     PROTECTION: AbilityDesc = PROTECTION
#     FLEE: AbilityDesc = FLEE
#     CURSE: AbilityDesc = CURSE
#
#     @staticmethod
#     def get_all() -> list[AbilityDesc]:
#         al: list[AbilityDesc] = [PROTECTION, FLEE, CURSE]
#         return al
#
#     @staticmethod
#     def get_by_name(name: str) -> AbilityDesc:
#         d: dict[str, AbilityDesc] = {ai.get_name(): ai for ai in Ability.get_all()}
#         return d.get(name)
#
#     @staticmethod
#     def get_by_index(index: int) -> AbilityDesc:
#         d: dict[int, AbilityDesc] = {ai.id: ai for ai in Ability.get_all()}
#         return d[index]
