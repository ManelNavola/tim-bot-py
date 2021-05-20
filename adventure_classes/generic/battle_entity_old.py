import random
import typing
from typing import Optional, Any

from autoslot import Slots

from adventure_classes.generic.stat_modifier import StatModifier
from entities.bot_entity import BotEntity
from entities.entity import Entity
from enums.emoji import Emoji
from helpers.translate import tr
from item_data.abilities import Ability
from item_data.stat import Stat

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle_old import BattleChapter, BattleEmoji


class AttackResult(Slots):
    def __init__(self):
        self.damage: Optional[int] = None
        self.crit: bool = False
        self.eva: bool = False
        self.vamp: bool = False
        self.counter: Optional[int] = None


class BattleEntity:
    def __init__(self, entity: Entity, lang: str):
        self.entity = entity
        self._lang: str = lang
        self._turn_modifiers: list[StatModifier] = []
        for modifier in entity.get_modifiers():
            self._turn_modifiers.append(modifier.clone(-1))
        self._is_user: bool = not isinstance(entity, BotEntity)
        self._actions: set[BattleEmoji] = {BattleEmoji.ATTACK} | set(BattleEmoji.get_spells(len(self.entity.get_abilities())))
        self._battle_chapter: Optional['BattleChapter'] = None

    def set_battle_instance(self, battle_chapter: 'BattleChapter'):
        self._battle_chapter = battle_chapter

    def is_dead(self):
        return self.entity.get_persistent(Stat.HP) == 0

    def get_actions(self) -> set[BattleEmoji]:
        return self._actions

    def try_action(self, action: BattleEmoji, targets: list['BattleEntity']) -> Optional[str]:
        if action not in self._actions:
            return None

        if action == BattleEmoji.ATTACK:
            if targets:
                temp: str
                ar: AttackResult = self.attack(targets[0])
                # Return message
                msg = []
                if ar.eva:
                    temp = tr(self._lang, 'BATTLE_ATTACK.EVADE', source=self.entity.get_name(),
                              target=targets[0].entity.get_name())
                    msg.append(f"> {temp}")
                else:
                    if ar.vamp:
                        if ar.crit:
                            temp = tr(self._lang, 'BATTLE_ATTACK.CRITICAL_VAMP', source=self.entity.get_name(),
                                      target=targets.entity.get_name(), damage=ar.damage)
                            msg.append(f"> {temp}")
                        else:
                            temp = tr(self._lang, 'BATTLE_ATTACK.VAMP', source=self.entity.get_name(),
                                      target=targets.entity.get_name(), damage=ar.damage)
                            msg.append(f"> {temp}")
                    else:
                        if ar.crit:
                            temp = tr(self._lang, 'BATTLE_ATTACK.CRIT', source=self.entity.get_name(),
                                      target=targets.entity.get_name(), damage=ar.damage)
                            msg.append(f"> {temp}")
                        else:
                            temp = tr(self._lang, 'BATTLE_ATTACK.ATTACK', source=self.entity.get_name(),
                                      target=targets.entity.get_name(), damage=ar.damage)
                            msg.append(f"> {temp}")
                return '\n'.join(msg)
        else:
            spell_index = action.get_spell_index()
            if -1 < spell_index < len(self.entity.get_abilities()):
                ability: Ability = self.entity.get_abilities()[spell_index]
                if ability.get_cost() <= self.entity.get_persistent(Stat.AP):
                    if (targets is not None) or ability.allow_self():
                        self.entity.change_persistent(Stat.AP, -ability.get_cost())
                        targets.

        return None


    @staticmethod
    def calculate_damage(atk: int, defense: int):
        return (float(atk) * 4.0 + 8.0) / (float(defense) * 1.5 + 6.0)

    def attack(self, target: 'BattleEntity', ignore_cont: bool = False) -> AttackResult:
        ar: AttackResult = AttackResult()
        # Evasion
        if random.random() < target.get_stat(Stat.EVA):
            ar.eva = True
            return ar
        # Counter
        if (not ignore_cont) and random.random() < target.get_stat(Stat.CONT):
            ar.counter = target.attack(self, True).damage

        # Damage
        dealt: float = self.calculate_damage(self.get_stat(Stat.STR), target.get_stat(Stat.DEF))
        # Crit
        if random.random() < self.get_stat(Stat.CRIT):
            dealt *= 2
            ar.crit = True
        int_dealt: int = max(round(dealt), 1)
        if self._battle_chapter:
            int_dealt *= (self._battle_chapter.get_round() // self._battle_chapter.INCREASE_EVERY + 1)
        # Vamp
        if random.random() < self.get_stat(Stat.VAMP):
            ar.vamp = True
            self.entity.change_persistent(Stat.HP, min(self.get_stat(Stat.HP), int_dealt))
        target.entity.change_persistent(Stat.HP, -int_dealt)
        ar.damage = int_dealt

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

    # def use_ability(self, ability: Optional[AbilityInstance], item_type: Optional[ItemType]) \
    #         -> Optional[AbilityInstance]:
    #     for i in range(len(self._available_abilities)):
    #         other_ability, other_item_type = self._available_abilities[i]
    #         if ((ability is None) or (ability == other_ability)) \
    #                 and ((item_type is None) or (item_type == other_item_type)):
    #             del self._available_abilities[i]
    #             return other_ability
    #     return None

    # def get_abilities(self) -> list[tuple[AbilityInstance, Optional[ItemType]]]:
    #     return self._available_abilities

    def is_user(self) -> bool:
        return self._is_user

    def _has_stat(self, stat: Stat) -> bool:
        if stat.get_value(self._get_stat_value(stat)) > 0:
            return True
        if self.entity.get_stat_value(stat) > 0:
            return True
        return False

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
            if self._has_stat(stat):
                sc.append(self._print_battle_stat(stat))

        return ', '.join(sc)
