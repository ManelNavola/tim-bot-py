from discord_slash import SlashContext

from adventure_classes.adventure import Adventure, Chapter
from adventure_classes.battle import BattleChapter
from enemy_data import enemies
from enums.emoji import Emoji
from user_data.user import User


class ColiseumRewardChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.BOX)

    async def init(self, user: User):
        self.add_log("You find a box beneath your feet.")
        self.add_log("You may collect the reward and exit, or venture further to find bigger rewards.")
        await self.pop_log()
        await self.message.add_reaction(Emoji.BOX, self.reward)
        await self.message.add_reaction(Emoji.COLISEUM, self.venture)

    async def reward(self):
        await self.send_log("COWARD LMAO")
        await self.end()

    async def venture(self):
        level: int = self._adventure.saved_data['level'] + 1
        self._adventure.saved_data['level'] = level
        for i in range(3):
            self._adventure.add_chapter(BattleChapter(enemies.get_random_enemy(level).instance()))
        self._adventure.add_chapter(ColiseumRewardChapter())
        await self.end()


async def start(ctx: SlashContext, user: User):
    adventure: Adventure = Adventure("Coliseum", Emoji.COLISEUM.value)
    adventure.saved_data['level'] = -1
    for i in range(3):
        adventure.add_chapter(BattleChapter(enemies.get_random_enemy(-1).instance()))
    adventure.add_chapter(ColiseumRewardChapter())
    await user.start_adventure(ctx, adventure)
