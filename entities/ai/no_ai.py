import typing

from entities.ai.base_ai import BotAI
from enums.battle_emoji import BattleEmoji

if typing.TYPE_CHECKING:
    from adventure_classes.generic.battle.battle import BattleActionData
    from adventure_classes.generic.battle.battle import BattleEntity


class NoAI(BotAI):
    def decide(self, battle_entity: 'BattleEntity', data: 'BattleActionData') -> BattleEmoji:
        return BattleEmoji.WAIT
