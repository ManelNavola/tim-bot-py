from enum import Enum

from typing import Dict

from enums.emoji import Emoji
from helpers.translate import tr
from item_data.stat import Stat


class UserClassInstance:
    def __init__(self, class_id: int, name: str, emoji: Emoji, stats: Dict[Stat, int]):
        self.id = class_id
        self.name = name
        self.stats = stats
        self.emoji = emoji


# UserClass total should be 10
class UserClass(Enum):
    _ignore_ = ['_INFO']
    WARRIOR = UserClassInstance(0, 'WARRIOR', Emoji.WARRIOR, {
        Stat.HP: 4,
        Stat.AP: 5,

        Stat.STR: 3,
        Stat.DEF: 3
    })
    ROGUE = UserClassInstance(1, 'ROGUE', Emoji.ROGUE, {
        Stat.HP: 4,
        Stat.AP: 5,

        Stat.STR: 4,

        Stat.SPD: 3,
    })
    BARBARIAN = UserClassInstance(2, 'BARBARIAN', Emoji.BARBARIAN, {
        Stat.HP: 4,
        Stat.AP: 4,

        Stat.STR: 5,
        Stat.DEF: 1,

        Stat.CONT: 2,
    })
    # MAGE = UserClassInstance(3, 'MAGE', Emoji.MAGE, {
    #     Stat.HP: 5,
    #     Stat.AP: 8,
    #
    #     Stat.STR: 3,
    #
    #     Stat.EVA: 2,
    # })
    _INFO = {}

    def get_id(self) -> int:
        return self.value.id

    def get_icon(self) -> Emoji:
        return self.value.emoji

    def get_name(self, lang: str) -> str:
        return tr(lang, f"CLASS.{self.value.name}")

    def get_stats(self) -> Dict[Stat, int]:
        return self.value.stats

    @staticmethod
    def get_from_id(class_id: int) -> 'UserClass':
        return UserClass._INFO['from_id'][class_id]


uci = {
    'from_id': {x.value.id: x for x in UserClass},
}

UserClass._INFO = uci
