from abc import ABC, abstractmethod
import typing

from enums.battle_emoji import BattleEmoji

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle.battle import BattleActionData
    from adventure_classes.generic.battle.battle import BattleEntity


class BotAI(ABC):
    @abstractmethod
    def decide(self, battle_entity: 'BattleEntity', data: 'BattleActionData') -> BattleEmoji:
        pass


class BaseBotAI(BotAI):
    def decide(self, battle_entity: 'BattleEntity', data: 'BattleActionData') -> BattleEmoji:
        best: int = -1
        first_most_attacked: 'BattleEntity' = next(iter(data.targeted_entities.keys()))
        for battle_entity, count in data.targeted_entities.items():
            if count > best:
                first_most_attacked = battle_entity
        data.target_entity = first_most_attacked
        return BattleEmoji.ATTACK
