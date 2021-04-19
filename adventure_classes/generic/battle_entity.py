import random
from typing import Optional, Any

from autoslot import Slots

from adventure_classes.generic.stat_modifier import StatModifier
from entities.bot_entity import BotEntity
from entities.entity import Entity
from enums.item_type import ItemType
from item_data.abilities import AbilityInstance
from item_data.stat import Stat


class AttackResult(Slots):
    def __init__(self):
        self.damage: Optional[int] = None
        self.crit: bool = False
        self.eva: bool = False
        self.vamp: bool = False
        self.counter: Optional[int] = None


class BattleEntity:
    def __init__(self, entity: Entity, battle_modifiers: list[StatModifier] = None):
        self.entity = entity
        self._available_abilities: list[tuple[AbilityInstance, Optional[ItemType]]] = entity.get_abilities()
        self._turn_modifiers: list[StatModifier] = []
        if battle_modifiers:
            for modifier in battle_modifiers:
                self._turn_modifiers.append(modifier.clone(-1))
        self._is_user: bool = not isinstance(entity, BotEntity)

    def attack(self, other: 'BattleEntity', ignore_cont: bool = False) -> AttackResult:
        ar: AttackResult = AttackResult()
        # Evasion
        if random.random() < other.get_stat(Stat.EVA):
            ar.eva = True
            return ar
        # Counter
        if (not ignore_cont) and random.random() < other.get_stat(Stat.CONT):
            ar.counter = other.attack(self, True).damage

        # Damage
        dealt: int = self.get_stat(Stat.STR)
        br: float = (dealt / (dealt + other.get_stat(Stat.DEF))) * dealt
        real_amount: int = max(1, round(br))
        # Crit
        if random.random() < self.get_stat(Stat.CRIT):
            real_amount *= 2
            ar.crit = True
        # Vamp
        if random.random() < self.get_stat(Stat.VAMP):
            ar.vamp = True
            self.entity.change_persistent(Stat.HP, min(self.get_stat(Stat.HP), real_amount))
        other.entity.change_persistent(Stat.HP, -real_amount)
        ar.damage = real_amount
        return ar

    def add_effect(self, modifier: StatModifier, include: bool = False):
        c_modifier: StatModifier
        if include:
            c_modifier = modifier.clone(modifier.duration + 1)
        else:
            c_modifier = modifier.clone()
        self._turn_modifiers.append(c_modifier)

    def end_turn(self):
        for i in range(len(self._turn_modifiers) - 1, -1, -1):
            self._turn_modifiers[i].duration -= 1
            if self._turn_modifiers[i].duration == 0:
                del self._turn_modifiers[i]

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

    def get_stat(self, stat: Stat) -> Any:
        return stat.get_value(self._get_stat_value(stat))

    def _get_stat_value(self, stat: Stat) -> int:
        value = self.entity.get_stat_value(stat)
        for modifier in self._turn_modifiers:
            if modifier.stat == stat:
                value = modifier.apply(value)
        return round(value)

    def _print_battle_stat(self, stat: Stat) -> str:
        stuff: list[str] = []
        for modifier in self._turn_modifiers:
            if modifier.stat == stat:
                stuff.append(modifier.print())
        if stuff:
            return stat.print(self._get_stat_value(stat), short=True,
                              persistent_value=self.entity.get_persistent(stat)) + ' (' + ', '.join(stuff) + ')'
        else:
            return stat.print(self._get_stat_value(stat), short=True,
                              persistent_value=self.entity.get_persistent(stat))

    def print(self) -> str:
        sc: list[str] = []

        for stat in Stat:
            if self.get_stat(stat) > 0:
                sc.append(self._print_battle_stat(stat))

        return ', '.join(sc)
