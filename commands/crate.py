import utils
from helpers.command import Command
from enums.emoji import Emoji
from guild_data.guild import Guild
from helpers.translate import tr


async def check(cmd: Command):
    money = cmd.guild.get_box()
    if money == 0:
        await cmd.send_hidden(tr(cmd.lang, 'CRATE.EMPTY', EMOJI_BOX=Emoji.BOX))
    else:
        rate_str = cmd.guild.print_box_rate()
        if len(rate_str) > 0:
            await cmd.send(tr(cmd.lang, 'CRATE.SHOW_RATE', money=utils.print_money(cmd.lang, money),
                              EMOJI_BOX=Emoji.BOX, EMOJI_CLOCK=Emoji.CLOCK, rate=rate_str))
        else:
            await cmd.send(tr(cmd.lang, 'CRATE.SHOW', money=utils.print_money(cmd.lang, money), EMOJI_BOX=Emoji.BOX))


async def place(cmd: Command, money: int):
    if money < Guild.TABLE_MIN:
        await cmd.error(tr(cmd.lang, 'CRATE.MIN', money=utils.print_money(cmd.lang, Guild.TABLE_MIN)))
        return
    placed = cmd.guild.place_box(cmd.user, money)
    if placed:
        rate_str = cmd.guild.print_box_rate()
        await cmd.send(tr(cmd.lang, 'CRATE.PLACE', EMOJI_BOX=Emoji.BOX, name=cmd.user.get_name(),
                          money=utils.print_money(cmd.lang, money), rate=rate_str, EMOJI_CLOCK=Emoji.CLOCK))
    else:
        await cmd.error(tr(cmd.lang, 'CRATE.LACK', money=utils.print_money(cmd.lang, money)))


async def take(cmd: Command):
    if cmd.user.get_total_money_space() == 0:
        await cmd.error(tr(cmd.lang, 'CRATE.MAX'))
    else:
        took = cmd.guild.retrieve_box(cmd.user)
        if took > 0:
            await cmd.send(tr(cmd.lang, 'CRATE.TAKE', name=cmd.user.get_name(), money=utils.print_money(cmd.lang, took),
                              EMOJI_BOX=Emoji.BOX))
        else:
            await cmd.error(tr(cmd.lang, 'CRATE.EMPTY'))
