import random
import typing

from autoslot import Slots

from entities.ai.base_ai import BotAI
from enums.battle_emoji import BattleEmoji
from item_data.abilities import AbilityContainer

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle.battle import BattleActionData
    from adventure_classes.generic.battle.battle import BattleEntity


class AbilityDecision(Slots):
    def __init__(self, min_hp: float, max_hp: float, ability: AbilityContainer, max_uses: int = 999):
        self.min_hp: float = min_hp
        self.max_hp: float = max_hp
        self.ability: AbilityContainer = ability
        self.uses: int = max_uses

    def get_cost(self) -> int:
        return self.ability.get_cost()


class AbilityAI(BotAI):
    def __init__(self, ability_decision_list: list[AbilityDecision] = None):
        if ability_decision_list is None:
            ability_decision_list = []
        self._ability_decisions = ability_decision_list
        self._min_ap: int = 99999999
        if self._ability_decisions:
            self._min_ap = min(x.get_cost() for x in self._ability_decisions)

    def decide(self, battle_entity: 'BattleEntity', data: 'BattleActionData') -> BattleEmoji:
        best: int = -1
        first_most_attacked: 'BattleEntity' = next(iter(data.targeted_entities.keys()))
        for other_battle_entity, count in data.targeted_entities.items():
            if count > best:
                first_most_attacked = other_battle_entity

        data.target_entity = first_most_attacked

        if battle_entity.has_ap(self._min_ap):
            current_hp_pct: float = float(battle_entity.get_hp()) / battle_entity.get_max_hp()
            potential_abilities: list[AbilityDecision] = []
            for ability_decision in self._ability_decisions:
                if ability_decision.min_hp <= current_hp_pct <= ability_decision.max_hp and battle_entity.has_ap(
                        ability_decision.get_cost()) and ability_decision.uses > 0:
                    potential_abilities.append(ability_decision)
            if potential_abilities:
                ability_decision: AbilityDecision = random.choice(potential_abilities)
                ability_decision.uses -= 1
                data.override_ability = ability_decision.ability
                return BattleEmoji.SPELL_1

        return BattleEmoji.ATTACK
