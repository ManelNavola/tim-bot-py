import typing
from typing import Optional, Dict

from autoslot import Slots

from item_data.abilities import AbilityContainer

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle.battle_entity import BattleEntity


class BattleActionData(Slots):
    def __init__(self,
                 lang: str,
                 damage_multiplier: int,
                 target_entity: Optional['BattleEntity'] = None,
                 targeted_entities: Optional[Dict['BattleEntity', int]] = None):
        self.lang: str = lang
        self.damage_multiplier: int = damage_multiplier
        self.target_entity: Optional['BattleEntity'] = target_entity
        self.targeted_entities: Optional[Dict['BattleEntity', int]] = targeted_entities
        self.override_ability: Optional[AbilityContainer] = None
