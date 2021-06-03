import typing
from abc import ABC, abstractmethod
from enum import Enum, unique

from typing import Optional
from autoslot import Slots

from enemy_data import enemy_utils
from enums.emoji import Emoji
from helpers.translate import tr
from item_data.stat import Stat
from item_data.stat_modifier import StatModifier, StatModifierOperation

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle.battle import BattleEntity
    from entities.bot_entity import BotEntity


class Ability(ABC):
    def __init__(self, icon: Emoji):
        self.icon = icon

    @staticmethod
    @abstractmethod
    def use(lang: str, source: 'BattleEntity', target_entity: 'BattleEntity', tier: int) -> str:  # noqa
        pass

    @staticmethod
    def start(lang: str, target: 'BattleEntity', tier: int) -> Optional[str]:  # noqa
        return None

    @staticmethod
    def turn(lang: str, target: 'BattleEntity', tier: int) -> Optional[str]:  # noqa
        return None

    @staticmethod
    def end(lang: str, target: 'BattleEntity', tier: int) -> Optional[str]:  # noqa
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
    def use(lang: str, source: 'BattleEntity', target_entity: 'BattleEntity', tier: int) -> str:
        return f"{source.get_name()} used Burn on {target_entity.get_name()}!"

    @staticmethod
    def get_duration(tier: int) -> int:
        return 4

    @staticmethod
    def get_cost(tier: int) -> int:
        return 6

    @staticmethod
    def turn(lang: str, target: 'BattleEntity', tier: int) -> Optional[str]:
        damage: int = (tier + 1) * 3
        target.damage(damage)
        return f"{target.get_name()} was burnt for {damage} damage!"


class Claw(Ability):
    def __init__(self):
        super().__init__(Emoji.LOBSTER)

    @staticmethod
    def use(lang: str, source: 'BattleEntity', target_entity: 'BattleEntity', tier: int) -> str:
        target_entity.add_temp_modifier(StatModifier(Stat.DEF, -3, StatModifierOperation.ADD, 3))
        target_entity.add_temp_modifier(StatModifier(Stat.STR, -4, StatModifierOperation.ADD, 3))
        return tr(lang, 'ABILITIES.CLAW_USE', source=source.get_name(), target=target_entity.get_name())

    @staticmethod
    def get_duration(tier: int) -> int:
        return 3

    @staticmethod
    def get_cost(tier: int) -> int:
        return 4


SUMMON_TYPES_TIER: dict[int, tuple[int, int]] = {
    100: (22, 5)  # Entling
}


class Summon(Ability):
    def __init__(self):
        super().__init__(Emoji.SPARKLE)

    @staticmethod
    def use(lang: str, source: 'BattleEntity', target_entity: 'BattleEntity', tier: int) -> str:
        bot_entity: 'BotEntity' = enemy_utils.get_enemy(SUMMON_TYPES_TIER[tier][0]).instance()
        source.get_group().add_entity(bot_entity)
        return tr(lang, 'ABILITIES.SUMMON', source=source.get_name(), summon=bot_entity.get_name())

    @staticmethod
    def get_duration(tier: int) -> int:
        return 0

    @staticmethod
    def get_cost(tier: int) -> int:
        return SUMMON_TYPES_TIER[tier][1]


@unique
class AbilityEnum(Enum):
    BURN = Burn()
    SUMMON = Summon()
    CLAW = Claw()

    def get(self) -> Ability:
        return self.value

    def allow_self(self) -> bool:
        return self.get().allow_self()


class AbilityContainer(Slots):
    def __init__(self, ability: AbilityEnum, tier: int):
        self.ability: AbilityEnum = ability
        self.tier: int = tier

    def get_duration(self) -> int:
        return self.ability.get().get_duration(self.tier)

    def use(self, lang: str, source: 'BattleEntity', target_entity: 'BattleEntity') -> str:
        return self.ability.get().use(lang, source, target_entity, self.tier)

    def start(self, lang: str, target_entity: 'BattleEntity') -> str:
        return self.ability.get().start(lang, target_entity, self.tier)

    def turn(self, lang: str, target_entity: 'BattleEntity') -> str:
        return self.ability.get().turn(lang, target_entity, self.tier)

    def end(self, lang: str, target_entity: 'BattleEntity') -> str:
        return self.ability.get().end(lang, target_entity, self.tier)

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
