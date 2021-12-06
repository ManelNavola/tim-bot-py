from typing import List, Tuple

from adventure_classes.generic.chapter import Chapter
from item_data.stat_modifier import StatModifier
from enums.emoji import Emoji
from helpers.translate import tr
from item_data.stat import Stat
from user_data.user import User


class BonusChapter(Chapter):
    def __init__(self, text: str):
        super().__init__(Emoji.BOX)
        self._text: str = text
        self._bonus: List[StatModifier] = []
        self._persistent_bonus: List[Tuple[Stat, int]] = []

    def add_modifier(self, modifier: StatModifier):
        self._bonus.append(modifier)

    def add_persistent(self, stat: Stat, value: int):
        self._persistent_bonus.append((stat, value))

    async def init(self):
        self.add_log(self._text)
        users: List[User] = self.get_adventure().get_users()
        for bonus in self._bonus:
            if bonus.duration < 0:
                self.add_log(tr(self.get_lang(), 'BONUS.WHOLE',
                                value=f"{bonus.print(True)}"))
            else:
                self.add_log(tr(self.get_lang(), 'BONUS.NEXT',
                                value=f"{bonus.print(True)}", duration=bonus.duration))
            for user in users:
                user.user_entity.add_modifier(bonus)
        for bonus in self._persistent_bonus:
            stat: Stat = bonus[0]
            amount: int = bonus[1]
            for user in users:
                old_value = user.user_entity.get_persistent_value(stat)
                if old_value:
                    new_value = min(old_value + amount, stat.get_value(user.user_entity.get_stat(stat)))
                    user.user_entity.change_persistent_value(stat, new_value)
                    self.add_log(f"+{amount} {stat.get_abv()} ({old_value} {Emoji.ARROW_RIGHT} {new_value})")
        await self.send_log()
        await self.end()
