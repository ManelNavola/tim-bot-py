import random
from typing import Optional, Any

from autoslot import Slots

from entities.bot_entity import BotEntity
from entities.entity import Entity
from enums.item_type import ItemType
from item_data.abilities import AbilityInstance
from item_data.stats import Stats, StatInstance


class AbilityEffect(Slots):
    def __init__(self, ability_instance: AbilityInstance):
        self.instance = ability_instance
        self.duration = ability_instance.get().duration


class AttackResult(Slots):
    def __init__(self):
        self.damage: Optional[int] = None
        self.crit: bool = False
        self.eva: bool = False
        self.vamp: bool = False
        self.counter: Optional[int] = None


class BattleEntity:
    def __init__(self, entity: Entity):
        self.entity = entity
        self._available_abilities: list[tuple[AbilityInstance, Optional[ItemType]]] = entity.get_abilities()
        self._effects: list[AbilityEffect] = []
        self._is_user: bool = not isinstance(entity, BotEntity)

    def attack(self, other: 'BattleEntity', ignore_cont: bool = False) -> AttackResult:
        ar: AttackResult = AttackResult()
        # Evasion
        if random.random() < other.get_stat(Stats.EVA):
            ar.eva = True
            return ar
        # Counter
        if (not ignore_cont) and random.random() < other.get_stat(Stats.CONT):
            ar.counter = other.attack(self, True).damage

        # Damage
        dealt: int = self.get_stat(Stats.STR)
        br: float = (dealt / (dealt + other.get_stat(Stats.DEF))) * dealt
        real_amount: int = max(1, round(br))
        # Crit
        if random.random() < self.get_stat(Stats.CRIT):
            real_amount *= 2
            ar.crit = True
        # Vamp
        if random.random() < self.get_stat(Stats.VAMP):
            ar.vamp = True
            self.entity.set_persistent(Stats.HP, min(self.get_stat(Stats.HP), self.entity.get_persistent(Stats.HP)
                                                     + real_amount))
        other.entity.set_persistent(Stats.HP, max(0, other.entity.get_persistent(Stats.HP) - real_amount))
        ar.damage = real_amount
        return ar

    def add_effect(self, ability_instance: AbilityInstance, include: bool = False):
        ae = AbilityEffect(ability_instance)
        if include:
            ae.duration += 1
        self._effects.append(ae)

    def end_turn(self):
        for i in range(len(self._effects) - 1, -1, -1):
            self._effects[i].duration -= 1
            if self._effects[i].duration <= 0:
                del self._effects[i]

    def use_ability(self, ability: Optional[AbilityInstance], item_type: Optional[ItemType]) \
            -> Optional[AbilityInstance]:
        for i in range(len(self._available_abilities)):
            other_ability, other_item_type = self._available_abilities[i]
            if ((ability is None) or (ability == other_ability)) \
                    and ((item_type is None) or (item_type == other_item_type)):
                del self._available_abilities[i]
                return other_ability
        return None

    def get_abilities(self) -> list[tuple[AbilityInstance, Optional[ItemType]]]:
        return self._available_abilities

    def is_user(self) -> bool:
        return self._is_user

    def get_stat(self, stat: StatInstance) -> Any:
        return stat.get_value(self._get_stat_value(stat))

    def _get_stat_value(self, stat: StatInstance) -> int:
        val = self.entity.get_stat_value(stat)
        for effect in self._effects:
            if effect.instance.get().stat == stat:
                val = val * effect.instance.get().multiplier
                val += effect.instance.get().adder
        return round(val)

    def _print_battle_stat(self, stat: StatInstance) -> str:
        stuff: list[str] = []
        for effect in self._effects:
            if effect.instance.get().stat == stat:
                if effect.instance.get().multiplier != 1:
                    stuff.append(f"x{effect.instance.get().multiplier:.2f}")
                if effect.instance.get().adder != 0:
                    stuff.append(f"{effect.instance.get().adder}")
        if stuff:
            return stat.print(self._get_stat_value(stat), short=True,
                              persistent_value=self.entity.get_persistent(stat, None)) + ' (' + ', '.join(stuff) + ')'
        else:
            return stat.print(self._get_stat_value(stat), short=True,
                              persistent_value=self.entity.get_persistent(stat, None))

    def print(self) -> str:
        sc: list[str] = []

        for stat in Stats.get_all():
            if self.get_stat(stat) > 0:
                sc.append(self._print_battle_stat(stat))

        return ', '.join(sc)
