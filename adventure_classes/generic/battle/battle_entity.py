import random
import typing
from typing import Optional

from autoslot import Slots

from adventure_classes.generic.battle import battle_utils
from adventure_classes.generic.battle.battle import BattleActionData
from adventure_classes.generic.stat_modifier import StatModifier
from entities.bot_entity import BotEntity
from entities.entity import Entity
from entities.user_entity import UserEntity
from enums.battle_emoji import BattleEmoji
from enums.emoji import Emoji
from helpers.translate import tr
from item_data.abilities import AbilityInstance, AbilityContainer
from item_data.stat import Stat
from user_data.user import User

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle.battle import BattleGroup


class AttackResult(Slots):
    def __init__(self):
        self.damage: Optional[int] = None
        self.crit: bool = False
        self.eva: bool = False
        self.vamp: bool = False
        self.counter: Optional[int] = None


class BattleEntity:
    def __init__(self, entity: Entity, group: 'BattleGroup'):
        self._entity: Entity = entity
        self._group: 'BattleGroup' = group
        self._turn_modifiers: list[StatModifier] = []
        self._ability_instances: list[AbilityInstance] = []
        self._last_target: Optional['BattleEntity'] = None
        # Apply global stat modifiers
        for modifier in entity.get_battle_modifiers():
            self._turn_modifiers.append(modifier.clone(-1))

    def get_group(self) -> 'BattleGroup':
        return self._group

    def add_turn_modifier(self, modifier: StatModifier) -> None:
        self._turn_modifiers.append(modifier)

    def step_turn_modifiers(self) -> None:
        modifiers: list[StatModifier] = []
        for modifier in self._turn_modifiers:
            if modifier.duration == -1:
                modifiers.append(modifier)
            else:
                modifier.duration -= 1
                if modifier.duration > 0:
                    modifiers.append(modifier)
        self._turn_modifiers = modifiers

    def step_battle_modifiers(self) -> None:
        self._entity.step_battle_modifiers()

    def get_last_target(self) -> Optional['BattleEntity']:
        return self._last_target

    def set_last_target(self, battle_entity: Optional['BattleEntity']) -> None:
        self._last_target = battle_entity

    def get_ability_instances(self) -> list[AbilityInstance]:
        return self._ability_instances

    def add_ability_instance(self, ability_instance: AbilityInstance) -> None:
        self._ability_instances.append(ability_instance)

    def set_ability_instances(self, ability_instances: list[AbilityInstance]) -> None:
        self._ability_instances = ability_instances

    def get_name(self) -> str:
        return self._entity.get_name()

    def _has_stat(self, stat: Stat) -> bool:
        if stat.get_value(self.get_stat(stat)) > 0:
            return True
        if self._entity.get_stat(stat) > 0:
            return True
        return False

    def get_abilities(self) -> list[AbilityContainer]:
        return self._entity.get_abilities()

    def _get_persistent_value(self, stat: Stat) -> int:
        return self._entity.get_persistent_value(stat)

    def _change_persistent_value(self, stat: Stat, value: int) -> None:
        self._entity.change_persistent_value(stat, value)

    def _set_persistent_value(self, stat: Stat, value: int) -> None:
        self._entity.set_persistent_value(stat, value)

    def get_stat_value(self, stat: Stat) -> typing.Any:
        return stat.get_value(self.get_stat(stat))

    def get_hp(self) -> int:
        return self._get_persistent_value(Stat.HP)

    def has_hp(self, value: int) -> int:
        return self.get_hp() >= value

    def get_max_hp(self) -> int:
        return self.get_stat_value(Stat.HP)

    def set_hp(self, value: int) -> None:
        self._set_persistent_value(Stat.HP, value)

    def damage(self, value: int) -> None:
        self._change_persistent_value(Stat.HP, -value)

    def heal(self, value: int) -> None:
        self._change_persistent_value(Stat.HP, value)

    def get_ap(self) -> int:
        return self._get_persistent_value(Stat.AP)

    def regen_ap(self) -> None:
        if self._has_stat(Stat.AP):
            self._change_persistent_value(Stat.AP, 1)

    def has_ap(self, value: int) -> bool:
        return self.get_ap() >= value

    def use_ap(self, value: int) -> bool:
        if self.get_ap() >= value:
            self._change_persistent_value(Stat.AP, -value)
            return True
        return False

    def set_ap(self, value: int) -> None:
        self._set_persistent_value(Stat.AP, value)

    def change_ap(self, value: int) -> None:
        self._change_persistent_value(Stat.AP, value)

    def get_money_value(self) -> int:
        stat_dict: dict[Stat, int] = self._entity.get_stat_dict()
        money: int = round(sum(stat.get_cost() * count for stat, count in stat_dict.items()) * 0.035)
        return money

    def get_stat(self, stat: Stat) -> int:
        number: float = self._entity.get_stat(stat)
        for modifier in self._turn_modifiers:
            if modifier.stat == stat:
                number = modifier.apply(number)
        return max(0, round(number))

    def _print_battle_stat(self, stat: Stat) -> str:
        stuff: list[str] = []
        for modifier in self._turn_modifiers:
            if modifier.stat == stat:
                stuff.append(modifier.print())
        if stuff:
            return stat.print(self.get_stat(stat), short=True,
                              persistent_value=self._entity.get_persistent_value(stat)) + ' (' + ', '.join(stuff) + ')'
        else:
            return stat.print(self.get_stat(stat), short=True,
                              persistent_value=self._entity.get_persistent_value(stat))

    def is_dead(self) -> bool:
        return self._entity.get_persistent_value(Stat.HP) == 0

    def bot_decide(self, data: BattleActionData) -> BattleEmoji:
        assert isinstance(self._entity, BotEntity), 'Cannot bot decide on a non-Bot entity'
        bot_entity: BotEntity = self._entity
        return bot_entity.get_ai().decide(self, data)

    def is_bot(self) -> bool:
        return isinstance(self._entity, BotEntity)

    def is_user(self, user: Optional[User] = None) -> bool:
        if user is None:
            return isinstance(self._entity, UserEntity)
        else:
            return self._entity == user.user_entity

    def attack(self, data: BattleActionData, ignore_cont: bool = False) -> AttackResult:
        target: BattleEntity = data.target_entity
        ar: AttackResult = AttackResult()
        # Evasion
        if random.random() < target.get_stat_value(Stat.EVA):
            ar.eva = True
            return ar
        # Damage
        dealt: float = battle_utils.calculate_damage(self.get_stat_value(Stat.STR), target.get_stat_value(Stat.DEF))
        # Crit
        if random.random() < self.get_stat_value(Stat.CRIT):
            dealt *= 2
            ar.crit = True
        int_dealt: int = max(round(dealt), 1)
        int_dealt *= data.damage_multiplier
        # Vamp
        if random.random() < self.get_stat_value(Stat.VAMP):
            ar.vamp = True
            self.heal(min(self.get_stat_value(Stat.HP), int_dealt))
        target.damage(int_dealt)
        if not target.is_dead():
            # Counter
            if (not ignore_cont) and random.random() < target.get_stat_value(Stat.CONT):
                ar.counter = target.attack(BattleActionData(data.lang, data.damage_multiplier, self), True).damage
        ar.damage = int_dealt

        return ar

    def try_perform_action(self, battle_emoji: BattleEmoji, data: BattleActionData) -> Optional[str]:
        target_entity: Optional[BattleEntity] = data.target_entity
        if battle_emoji == BattleEmoji.ATTACK:
            if target_entity is not None:
                temp: str
                ar: AttackResult = self.attack(data)
                # Return message
                msg = []
                if ar.eva:
                    temp = tr(data.lang, 'BATTLE_ATTACK.EVADE', source=self.get_name(),
                              target=target_entity.get_name())
                    msg.append(f"> {Emoji.EVA} {temp}")
                else:
                    if ar.vamp:
                        if ar.crit:
                            temp = tr(data.lang, 'BATTLE_ATTACK.CRITICAL_VAMP', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {Emoji.CRIT}{Emoji.VAMP} {temp}")
                        else:
                            temp = tr(data.lang, 'BATTLE_ATTACK.VAMP', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {Emoji.VAMP} {temp}")
                    else:
                        if ar.crit:
                            temp = tr(data.lang, 'BATTLE_ATTACK.CRIT', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {Emoji.CRIT} {temp}")
                        else:
                            temp = tr(data.lang, 'BATTLE_ATTACK.ATTACK', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {Emoji.BATTLE} {temp}")
                if ar.counter is not None:
                    temp = tr(data.lang, 'BATTLE_ATTACK.COUNTER', target=target_entity.get_name(), damage=ar.damage)
                    msg.append(f"> {Emoji.CONT} {temp}")
                return '\n'.join(msg)
        if battle_emoji == BattleEmoji.WAIT:
            return f"> {battle_emoji} {tr(data.lang, 'BATTLE_ATTACK.WAIT', source=self.get_name())}"
        spell_index: int = battle_emoji.get_spell_index()
        if 0 <= spell_index < len(self.get_abilities()) or (data.override_ability is not None):
            ability_holder: AbilityContainer
            if data.override_ability is None:
                ability_holder = self.get_abilities()[spell_index]
            else:
                ability_holder = data.override_ability
            if (target_entity is None) and ability_holder.ability.allow_self():
                target_entity = self
            if target_entity is None:
                return None
            if not self.use_ap(ability_holder.get_cost()):
                return None
            ret: str = f"> {battle_emoji} {ability_holder.use(data.lang, self, target_entity)}"
            if ability_holder.get_duration() > 0:
                target_entity.add_ability_instance(AbilityInstance(ability_holder))
            start: str = ability_holder.start(data.lang, target_entity)
            if start:
                ret += f"\n> {ability_holder.get_icon()} {start}"
            return ret

        return None

    def print(self) -> str:
        prefixes: list[str] = []
        sc: list[str] = []

        if self.is_dead():
            return f"{Emoji.DEAD} {self.get_name()}"
        else:
            for ability_instance in self._ability_instances:
                prefixes.append(f"{ability_instance.get_icon()} ")

        for stat in Stat:
            if self._has_stat(stat):
                sc.append(self._print_battle_stat(stat))

        return ''.join(prefixes) + f"{self.get_name()}: " + ', '.join(sc)
