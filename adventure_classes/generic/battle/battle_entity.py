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


class AttackResult(Slots):
    def __init__(self):
        self.damage: Optional[int] = None
        self.crit: bool = False
        self.eva: bool = False
        self.vamp: bool = False
        self.counter: Optional[int] = None


class BattleEntity:
    def __init__(self, entity: Entity):
        self._entity: Entity = entity
        self._turn_modifiers: list[StatModifier] = []
        self._ability_instances: list[AbilityInstance] = []
        self._last_target: Optional['BattleEntity'] = None
        # Apply global stat modifiers
        for modifier in entity.get_battle_modifiers():
            self._turn_modifiers.append(modifier.clone(-1))

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

    def get_persistent_value(self, stat: Stat) -> int:
        return self._entity.get_persistent_value(stat)

    def change_persistent_value(self, stat: Stat, value: int) -> None:
        self._entity.change_persistent_value(stat, value)

    def set_persistent_value(self, stat: Stat, value: int) -> None:
        self._entity.set_persistent_value(stat, value)

    def get_stat_value(self, stat: Stat) -> typing.Any:
        return stat.get_value(self.get_stat(stat))

    def get_stat(self, stat: Stat) -> int:
        number: float = self._entity.get_stat(stat)
        for modifier in self._turn_modifiers:
            if modifier.stat == stat:
                number = modifier.apply(number)
        return round(number)

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
        return bot_entity.get_ai().decide(data)

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
        # Counter
        if (not ignore_cont) and random.random() < target.get_stat_value(Stat.CONT):
            ar.counter = target.attack(BattleActionData(data.lang, data.damage_multiplier, self), True).damage

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
            self.change_persistent_value(Stat.HP, min(self.get_stat_value(Stat.HP), int_dealt))
        target.change_persistent_value(Stat.HP, -int_dealt)
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
                    msg.append(f"> {battle_emoji} {temp}")
                else:
                    if ar.vamp:
                        if ar.crit:
                            temp = tr(data.lang, 'BATTLE_ATTACK.CRITICAL_VAMP', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {battle_emoji} {temp}")
                        else:
                            temp = tr(data.lang, 'BATTLE_ATTACK.VAMP', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {battle_emoji} {temp}")
                    else:
                        if ar.crit:
                            temp = tr(data.lang, 'BATTLE_ATTACK.CRIT', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {battle_emoji} {temp}")
                        else:
                            temp = tr(data.lang, 'BATTLE_ATTACK.ATTACK', source=self.get_name(),
                                      target=target_entity.get_name(), damage=ar.damage)
                            msg.append(f"> {battle_emoji} {temp}")
                return '\n'.join(msg)
        if battle_emoji == BattleEmoji.WAIT:
            return f"> {battle_emoji} {self.get_name()} waits..."
        spell_index: int = battle_emoji.get_spell_index()
        if 0 <= spell_index < len(self.get_abilities()):
            ability_holder: AbilityContainer = self.get_abilities()[spell_index]
            if (target_entity is None) and ability_holder.ability.allow_self():
                target_entity = self
            if target_entity is None:
                return None
            if ability_holder.get_cost() > self.get_persistent_value(Stat.AP):
                return None
            self.change_persistent_value(Stat.AP, -ability_holder.get_cost())
            ret: str = f"> {battle_emoji} {ability_holder.use(self, target_entity)}"
            target_entity.add_ability_instance(AbilityInstance(ability_holder))
            start: str = ability_holder.start(target_entity)
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
