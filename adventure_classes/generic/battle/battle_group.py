import math
import typing

from typing import List

from adventure_classes.generic.battle.battle_entity import BattleEntity
from entities.entity import Entity
from item_data.stat import Stat

if typing.TYPE_CHECKING:
    from user_data.user import User
    from adventure_classes.generic.adventure import Adventure


class BattleGroup:
    def __init__(self, entities: List[Entity] = None, users: List['User'] = None):
        if entities is None:
            entities = []
        if users is None:
            users = []
        self._users: List['User'] = users
        self._battle_entities: List[BattleEntity] = [BattleEntity(entity, self) for entity in entities]
        self._speed: float = 0

    def get_name(self) -> str:
        return ', '.join(battle_entity.get_name() for battle_entity in self.get_battle_entities())

    def find_user(self, user: 'User') -> typing.Optional[BattleEntity]:
        for battle_entity in self._battle_entities:
            if battle_entity.is_user(user):
                return battle_entity
        return None

    def get_battle_entities(self):
        return self._battle_entities

    def get_alive_count(self) -> int:
        return sum(1 for battle_entity in self._battle_entities if not battle_entity.is_dead())

    def get_alive_user_count(self) -> int:
        return sum(1 for battle_entity in self._battle_entities
                   if battle_entity.is_user() and (not battle_entity.is_dead()))

    def has_multiple_users(self) -> bool:
        return sum(1 for battle_entity in self._battle_entities if battle_entity.is_user()) > 1

    def has_users(self) -> bool:
        return any(battle_entity.is_user()
                   for battle_entity in self._battle_entities)

    def get_speed(self) -> float:
        return self._speed

    def load(self, _: 'Adventure') -> None:
        # Load users if any
        for user in self._users:
            self._battle_entities.append(BattleEntity(user.user_entity, self, user))
        self._recalculate()
        # Battle effects step
        for battle_entity in self._battle_entities:
            battle_entity.step_battle_modifiers()
        # Fix entity health
        for battle_entity in self._battle_entities:
            min_health: int = int(math.ceil(battle_entity.get_max_hp() * 0.1))
            if not battle_entity.has_hp(min_health):
                battle_entity.set_hp(min_health)

    def add_entity(self, entity: Entity) -> None:
        self._battle_entities.append(BattleEntity(entity, self))
        self._recalculate()

    def add_user(self, user: 'User') -> None:
        self._battle_entities.append(BattleEntity(user.user_entity, self, user))
        self._recalculate()

    def remove_entity(self, battle_entity: BattleEntity) -> None:
        self._battle_entities.remove(battle_entity)
        self._recalculate()

    def _recalculate(self) -> None:
        fl: List[float] = [battle_entity.get_stat_value(Stat.SPD)
                           for battle_entity in self._battle_entities]
        if not fl:
            self._speed = 1
        else:
            self._speed = sum(fl) / float(len(fl))


class BattleGroupUserDelayed(BattleGroup):
    def __init__(self):
        super().__init__()

    def load(self, adventure: 'Adventure') -> None:
        self._users = adventure.get_users()
        super().load(adventure)
