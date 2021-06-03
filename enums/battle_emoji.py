from enum import Enum, unique

from enums.emoji import Emoji


@unique
class BattleEmoji(Enum):
    ATTACK = Emoji.BATTLE
    SPELL_1 = Emoji.BLUE_BOOK
    SPELL_2 = Emoji.RED_BOOK
    SPELL_3 = Emoji.GREEN_BOOK
    SPELL_4 = Emoji.ORANGE_BOOK
    POTION = Emoji.POTION_TUBE
    WAIT = Emoji.CLOCK

    def __str__(self) -> str:
        return str(self.value)

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
