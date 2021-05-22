import math
import typing

from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle.battle_entity import BattleEntity
from entities.entity import Entity
from item_data.stat import Stat

if typing.TYPE_CHECKING:
    from user_data.user import User


class BattleGroup:
    def __init__(self, entities: list[Entity] = None):
        if entities is None:
            entities = []
        self._battle_entities: list[BattleEntity] = [BattleEntity(entity, self) for entity in entities]
        self._speed: float = 0
        self._recalculate()

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

    def load(self, adventure: Adventure) -> None:
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

    def remove_entity(self, battle_entity: BattleEntity) -> None:
        self._battle_entities.remove(battle_entity)
        self._recalculate()

    def _recalculate(self) -> None:
        fl: list[float] = [battle_entity.get_stat_value(Stat.SPD)
                           for battle_entity in self._battle_entities]
        if not fl:
            self._speed = 1
        else:
            self._speed = sum(fl) / float(len(fl))


class BattleGroupUsers(BattleGroup):
    def __init__(self, users: list['User'] = None, entities: list[Entity] = None):
        if entities is None:
            entities = []
        super().__init__(entities)
        if users is None:
            users = []
        self._users_to_load: list['User'] = users

    def load(self, adventure: Adventure) -> None:
        for user in adventure.get_users():
            if user in adventure.get_users():
                self.add_entity(user.user_entity)
        super().load(adventure)
