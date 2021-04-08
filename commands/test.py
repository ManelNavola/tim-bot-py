import utils
from adventure.adventure import Adventure
from adventure.battle import BattleChapter
from adventure.reward import RewardChapter
from commands.command import Command
from inventory_data.entity import BotEntityBuilder
from inventory_data.stats import Stats

FITE_BOT: bool = True


async def test(cmd: Command):
    if FITE_BOT:
        potato = BotEntityBuilder('Potato', 4, 0, {
            Stats.STR: -1,
        })
        adventure: Adventure = Adventure("Test Adventure", f"{utils.Emoji.BANK}")
        adventure.add_chapter(BattleChapter(potato.instance()))
        adventure.add_chapter(RewardChapter())
        await cmd.user.start_adventure(cmd.ctx, adventure)
    else:
        pass
        # if saved is None:
        #    saved = cmd.user
        # else:
        #    pass
        #    await cmd.guild.start_battle(cmd.ctx, cmd.user, opponent_user=saved)
