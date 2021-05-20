import asyncio
import math
import typing

from typing import Optional
from enum import unique, Enum

from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.chapter import Chapter
from adventure_classes.generic.stat_modifier import StatModifier
from entities.entity import Entity
from entities.user_entity import UserEntity
from enums.emoji import Emoji
from helpers.timer import DelayTask
from helpers.translate import tr
from item_data.abilities import AbilityInstance
from item_data.stat import Stat

if typing.TYPE_CHECKING:
    from user_data.user import User


@unique
class BattleEmoji(Enum):
    ATTACK = Emoji.BATTLE
    SPELL_1 = Emoji.BLUE_BOOK
    SPELL_2 = Emoji.RED_BOOK
    SPELL_3 = Emoji.GREEN_BOOK
    SPELL_4 = Emoji.ORANGE_BOOK

    def __str__(self) -> str:
        return self.value

    def get_spell_index(self) -> int:
        return {
            BattleEmoji.SPELL_1: 0,
            BattleEmoji.SPELL_2: 1,
            BattleEmoji.SPELL_3: 2,
            BattleEmoji.SPELL_4: 3,
        }.get(self, -1)

    @staticmethod
    def get_spells(many: int):
        return [BattleEmoji.SPELL_1, BattleEmoji.SPELL_2, BattleEmoji.SPELL_3, BattleEmoji.SPELL_4][:many]


class BattleEntity:
    def __init__(self, entity: Entity):
        self._entity: Entity = entity
        self._turn_modifiers: list[StatModifier] = []
        self._ability_instances: list[AbilityInstance] = []
        self._last_target: Optional['BattleEntity'] = None
        # Apply global stat modifiers
        for modifier in entity.get_battle_modifiers():
            self._turn_modifiers.append(modifier.clone(-1))

    def get_last_target(self) -> Optional['BattleEntity']:
        return self._last_target

    def set_last_target(self, battle_entity: Optional['BattleEntity']) -> None:
        self._last_target = battle_entity

    def get_ability_instances(self) -> list[AbilityInstance]:
        return self._ability_instances

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

    def is_user(self) -> bool:
        return isinstance(self._entity, UserEntity)

    def print(self) -> str:
        prefixes: list[str] = []
        sc: list[str] = []

        if self.is_dead():
            return f"{Emoji.DEAD} {self.get_name()}"
        else:
            for ability_instance in self._ability_instances:
                prefixes.append(str(ability_instance.ability.icon))

        for stat in Stat:
            if self._has_stat(stat):
                sc.append(self._print_battle_stat(stat))

        return ''.join(prefixes) + f"{self.get_name()}:" + ', '.join(sc)


class BattleGroup:
    def __init__(self, entities: list['Entity'] = None):
        if entities is None:
            entities = []
        self._battle_entities: list[BattleEntity] = [BattleEntity(entity) for entity in entities]
        self._speed: float = 0

    def get_battle_entities(self):
        return self._battle_entities

    def get_alive_count(self) -> int:
        return sum(1 for battle_entity in self._battle_entities if not battle_entity.is_dead())

    def has_multiple_users(self) -> int:
        return sum(1 for battle_entity in self._battle_entities if battle_entity.is_user()) > 1

    def has_users(self) -> bool:
        return any(battle_entity
                   for battle_entity in self._battle_entities
                   if isinstance(battle_entity.is_user(), UserEntity))

    def get_speed(self) -> float:
        return self._speed

    def load(self, adventure: Adventure) -> None:
        # Fix entity health
        for battle_entity in self._battle_entities:
            min_health: int = int(math.ceil(Stat.HP.get_value(battle_entity.get_stat(Stat.HP)) * 0.1))
            if battle_entity.get_persistent_value(Stat.HP) < min_health:
                battle_entity.set_persistent_value(Stat.HP, min_health)

    def add_entity(self, entity: Entity) -> None:
        self._battle_entities.append(BattleEntity(entity))
        self._recalculate()

    def remove_entity(self, battle_entity: BattleEntity) -> None:
        self._battle_entities.remove(battle_entity)
        self._recalculate()

    def _recalculate(self) -> None:
        fl: list[float] = [Stat.SPD.get_value(battle_entity.get_stat(Stat.SPD)) for battle_entity in self._battle_entities]
        self._speed = sum(fl) / float(len(fl))


class BattleGroupUsers(BattleGroup):
    def __init__(self, users: list['User'] = None):
        super().__init__([])
        if users is None:
            users = []
        self._users_to_load: list['User'] = users

    def load(self, adventure: Adventure) -> None:
        for user in adventure.get_users():
            if user in adventure.get_users():
                self.add_entity(user.user_entity)
        super().load(adventure)


class BattleChapter(Chapter):
    INCREASE_EVERY: typing.Final[int] = 8

    def __init__(self, group_a: BattleGroup, group_b: BattleGroup):
        super().__init__(Emoji.BATTLE)
        self._group_a: BattleGroup = group_a
        self._group_b: BattleGroup = group_b
        self._turn_a: bool = True
        self._battle_log: list[str] = []
        self._round: int = 0
        self._available_targets: list[BattleEntity] = []
        self._chosen_targets: dict[BattleEntity, BattleEntity] = {}
        self._pass_turn: Optional[DelayTask] = None

    def _print_round(self) -> str:
        mult: int = (self._round // self.INCREASE_EVERY) + 1
        if mult == 1:
            return tr(self.get_lang(), 'BATTLE.ROUND', EMOJI_BATTLE=Emoji.BATTLE, round=self._round)
        return tr(self.get_lang(), 'BATTLE.ROUND_DMG', EMOJI_BATTLE=Emoji.BATTLE, round=self._round, multiplier=mult)

    def get_current_team(self) -> BattleGroup:
        return self._group_a if self._turn_a else self._group_b

    def get_opposing_team(self) -> BattleGroup:
        return self._group_b if self._turn_a else self._group_a

    async def update(self):
        current_team: BattleGroup = self.get_current_team()
        other_team: BattleGroup = self.get_opposing_team()
        self.clear_log()
        self.start_log()
        if self._round < 2:
            self.add_log(f"{tr(self.get_lang(), 'BATTLE.START')}")
        self.add_log(self._print_round())
        for battle_entity in current_team.get_battle_entities():
            self.add_log(battle_entity.print())

        if len(self._available_targets) == 1:
            battle_entity: BattleEntity = other_team.get_battle_entities()[0]
            self.add_log(f"{battle_entity.print()}")
        else:
            td: dict[BattleEntity, list[str]] = {}
            for be1, be2 in self._chosen_targets.items():
                if be2 is not None:
                    td[be2] = td.get(be2, []) + [be1.get_name()]
            for i in range(len(self._available_targets)):
                battle_entity: BattleEntity = self._available_targets[i]
                sl: list[str] = td.get(battle_entity, [])
                if sl and (not battle_entity.is_dead()):
                    self.add_log(f"{i + 1} | {battle_entity.print()} <- {', '.join(sl)}")
                else:
                    self.add_log(f"{i + 1} | {battle_entity.print()}")

        self.add_log('\n'.join(self._battle_log))

        await self.send_log()

    async def execute_turn(self) -> bool:
        current_team: BattleGroup = self.get_current_team()

        # Turn happenings
        for battle_entity in current_team.get_battle_entities():
            instances: list[AbilityInstance] = []
            for ability_instance in battle_entity.get_ability_instances():
                ability_instance.duration_remaining -= 1
                if ability_instance.duration_remaining > 0:
                    self._battle_log.append(ability_instance.ability.turn(battle_entity, ability_instance.tier))
                    instances.append(ability_instance)
                battle_entity.set_ability_instances(instances)

        if current_team.get_alive_count() == 0:
            return True

        other_team: BattleGroup = self.get_opposing_team()

        self._available_targets: list[BattleEntity] = [battle_entity
                                                       for battle_entity in other_team.get_battle_entities()
                                                       if not battle_entity.is_dead()]

        if not self._available_targets:
            return True  # Won

        if not current_team.has_users():
            return await self.execute_turn_bot()

        for battle_entity in current_team.get_battle_entities():
            target: BattleEntity = battle_entity.get_last_target()
            if (target is not None) and (target in self._available_targets):
                self._chosen_targets[battle_entity] = target
            else:
                battle_entity.set_last_target(None)

        await self.update()

        if len(self._available_targets) == 1:
            for battle_entity in current_team.get_battle_entities():
                battle_entity.set_last_target(self._available_targets[0])

        if current_team.has_multiple_users():
            self._pass_turn = DelayTask(30, self.next_turn)
        else:
            self._pass_turn = DelayTask(120, self.next_turn)

    async def execute_turn_bot(self) -> bool:
        return False

    async def init(self) -> None:
        self._round = 1
        self._group_a.load(self.get_adventure())
        self._group_b.load(self.get_adventure())
        self._turn_a = (self._group_a.get_speed() >= self._group_b.get_speed())
        # Loop
        while True:
            if self._battle_log and (not self._group_a.has_users()) and (not self._group_b.has_users()):
                await self.update()
                await asyncio.sleep(3)
                self._battle_log.clear()
            if await self.execute_turn():
                break
            self._battle_log.clear()
            self._turn_a = not self._turn_a

    async def next_turn(self) -> None:

