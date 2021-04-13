import utils
from helpers.command import Command
from enums.emoji import Emoji
from guild_data.guild import Guild


async def check(cmd: Command):
    money = cmd.guild.get_box()
    if money == 0:
        await cmd.send_hidden(f"{Emoji.BOX} There is no money in the crate")
    else:
        rate_str = cmd.guild.print_box_rate()
        if len(rate_str) > 0:
            await cmd.send(f'{Emoji.BOX} There is {utils.print_money(money)} in the crate '
                           f'({rate_str}{Emoji.CLOCK})')
        else:
            await cmd.send(f'{Emoji.BOX} There is {utils.print_money(money)} in the crate')


async def place(cmd: Command, money: int):
    if money < Guild.TABLE_MIN:
        await cmd.error(f"You must place a minimum of {utils.print_money(Guild.TABLE_MIN)}!")
        return
    placed = cmd.guild.place_box(cmd.user, money)
    if placed:
        rate_str = cmd.guild.print_box_rate()
        await cmd.send(f"{Emoji.BOX} {cmd.user.get_name()} placed {utils.print_money(money)} "
                       f"in the crate ({rate_str}{Emoji.CLOCK})")
    else:
        await cmd.error(f"You don't have {utils.print_money(money)}!")


async def take(cmd: Command):
    if cmd.user.get_total_money_space() == 0:
        await cmd.error("You cannot hold more money!")
    else:
        took = cmd.guild.retrieve_box(cmd.user)
        if took > 0:
            await cmd.send(f"{Emoji.BOX} {cmd.user.get_name()} took {utils.print_money(took)} from the crate!")
        else:
            await cmd.error("There is no money in the crate")
