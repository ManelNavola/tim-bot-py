from discord_slash import SlashContext

import utils
from adventures.adventure import Adventure
from adventures.battle import BattleChapter
from enemy_data import enemies
from user_data.user import User


async def start(ctx: SlashContext, user: User):
    adventure: Adventure = Adventure("Coliseum", utils.Emoji.COLISEUM)
    for i in range(3):
        adventure.add_chapter(BattleChapter(enemies.get_random_enemy().instance()))
    await user.start_adventure(ctx, adventure)
