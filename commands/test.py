from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import BattleChapter
from helpers.command import Command
from entities.bot_entity import BotEntityBuilder
from enums.emoji import Emoji
from item_data.stat import Stat

FIGHT_BOT: bool = True


async def rich(cmd: Command):
    for upg_name in cmd.user.upgrades:
        upg = cmd.user.upgrades[upg_name]
        while not upg.is_max_level():
            upg.level_up()
    cmd.user.add_money(999999999999)
    await cmd.send_hidden("capitalism ho")


async def heal(cmd: Command):
    cmd.user.user_entity.change_persistent(Stat.HP, 999999)
    await cmd.send_hidden("cheater... healed")


async def test(cmd: Command):
    if FIGHT_BOT:
        potato = BotEntityBuilder('Potato', {
            Stat.HP: -16,
            Stat.MP: 0,
            Stat.STR: -1,
        })
        adventure: Adventure = Adventure("Test Adventure", f"{Emoji.BANK}")
        adventure.add_chapter(BattleChapter(potato.instance()))
        await cmd.user.start_adventure(cmd.ctx, adventure)
    else:
        pass
        # if saved is None:
        #    saved = cmd.user
        # else:
        #    pass
        #    await cmd.guild.start_battle(cmd.ctx, cmd.user, opponent_user=saved)
