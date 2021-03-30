import utils
from commands.command import Command
from data.guild import Guild


async def check(cmd: Command):
    money = cmd.guild.get_table()
    if money == 0:
        await cmd.send_hidden("There is no money on the table")
    else:
        rate_str = cmd.guild.print_table_rate()
        if len(rate_str) > 0:
            await cmd.send(f'There is {utils.print_money(money)} on the table ({rate_str})')
        else:
            await cmd.send(f'There is {utils.print_money(money)} on the table')


async def place(cmd: Command, money: int):
    if money < Guild.TABLE_MIN:
        await cmd.error(f"You must place a minimum of {utils.print_money(Guild.TABLE_MIN)}!")
        return
    placed = cmd.guild.place_table(cmd.user, money)
    if placed:
        await cmd.send(f"You placed {utils.print_money(money)} on the table")
    else:
        await cmd.error(f"You don't have {utils.print_money(money)}!")


async def take(cmd: Command):
    if cmd.user.get_total_money_space() == 0:
        await cmd.error("You cannot hold more money!")
    else:
        took = cmd.guild.retrieve_table(cmd.user)
        await cmd.send(f"{cmd.user.get_name()} took {utils.print_money(took)} from the table!")
