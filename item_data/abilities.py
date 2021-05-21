import typing
from abc import ABC, abstractmethod
from enum import Enum, unique

from typing import Optional
from autoslot import Slots
from enums.emoji import Emoji
from item_data.stat import Stat

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle.battle import BattleEntity


class Ability(ABC):
    def __init__(self, icon: Emoji):
        self.icon = icon

    @staticmethod
    @abstractmethod
    def use(source: 'BattleEntity', target_entity: 'BattleEntity', tier: int) -> str:  # noqa
        pass

    @staticmethod
    def start(target: 'BattleEntity', tier: int) -> Optional[str]:  # noqa
        return None

    @staticmethod
    def turn(target: 'BattleEntity', tier: int) -> Optional[str]:  # noqa
        return None

    @staticmethod
    def end(target: 'BattleEntity', tier: int) -> Optional[str]:  # noqa
        return None

    @staticmethod
    def get_duration(tier: int) -> int:
        return 0

    @staticmethod
    def allow_self() -> bool:
        return False

    @staticmethod
    @abstractmethod
    def get_cost(tier: int) -> int:
        pass


class Burn(Ability):
    def __init__(self):
        super().__init__(Emoji.BURN)

    @staticmethod
    def use(source: 'BattleEntity', target_entity: 'BattleEntity', tier: int) -> str:
        return f"{source.get_name()} used Burn on {target_entity.get_name()}!"

    @staticmethod
    def get_duration(tier: int) -> int:
        return 4

    @staticmethod
    def get_cost(tier: int) -> int:
        return 6

    @staticmethod
    def turn(target: 'BattleEntity', tier: int) -> Optional[str]:
        damage: int = (tier + 1) * 3
        target.change_persistent_value(Stat.HP, -damage)
        return f"{target.get_name()} was burnt for {damage} damage!"


@unique
class AbilityEnum(Enum):
    BURN = Burn()

    def get(self) -> Ability:
        return self.value


class AbilityContainer(Slots):
    def __init__(self, ability: AbilityEnum, tier: int):
        self.ability: AbilityEnum = ability
        self.tier: int = tier

    def get_duration(self) -> int:
        return self.ability.get().get_duration(self.tier)

    def use(self, source: 'BattleEntity', target_entity: 'BattleEntity') -> str:
        return self.ability.get().use(source, target_entity, self.tier)

    def start(self, target_entity: 'BattleEntity') -> str:
        return self.ability.get().start(target_entity, self.tier)

    def turn(self, target_entity: 'BattleEntity') -> str:
        return self.ability.get().turn(target_entity, self.tier)

    def end(self, target_entity: 'BattleEntity') -> str:
        return self.ability.get().end(target_entity, self.tier)

    def get_cost(self) -> int:
        return self.ability.get().get_cost(self.tier)

    def get_icon(self) -> Emoji:
        return self.ability.get().icon


class AbilityInstance(Slots):
    def __init__(self, holder: AbilityContainer):
        self.duration_remaining = holder.get_duration()
        self.ability_holder = holder

    def get_icon(self) -> Emoji:
        return self.ability_holder.get_icon()
