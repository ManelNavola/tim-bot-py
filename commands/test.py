from adventures.adventure import Adventure
from adventures.battle import BattleChapter
from adventures.reward import RewardChapter
from commands.command import Command
from entities.bot_entity import BotEntityBuilder
from enums.emoji import Emoji
from item_data.stats import Stats

FIGHT_BOT: bool = True


async def rich(cmd: Command):
    for upg_name in cmd.user.upgrades:
        upg = cmd.user.upgrades[upg_name]
        while not upg.is_max_level():
            upg.level_up()
    cmd.user.add_money(999999999999)
    await cmd.send_hidden("yay")


async def test(cmd: Command):
    if FIGHT_BOT:
        potato = BotEntityBuilder('Potato', {
            Stats.HP: -16,
            Stats.MP: 0,
            Stats.STR: -1,
        })
        adventure: Adventure = Adventure("Test Adventure", f"{Emoji.BANK}")
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
