from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import BattleChapter
from adventure_classes.generic.stat_modifier import StatModifierAdd
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
    cmd.user.user_entity.add_modifier(StatModifierAdd(Stat.EVA, 9999))
    cmd.user.user_entity.add_modifier(StatModifierAdd(Stat.STR, 9999))
    await cmd.send_hidden("cheater...")


async def test(cmd: Command):
    if FIGHT_BOT:
        potato = BotEntityBuilder('Potato', {
            Stat.HP: -16,
            Stat.MP: 0,
            Stat.STR: -1,
        })
        adventure: Adventure = Adventure("Test Adventure", Emoji.BANK)
        adventure.add_chapter(BattleChapter(potato.instance()))
        await adventure.start(cmd.ctx, [cmd.user])
    else:
        pass
        # if saved is None:
        #    saved = cmd.user
        # else:
        #    pass
        #    await cmd.guild.start_battle(cmd.ctx, cmd.user, opponent_user=saved)
