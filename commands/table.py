from commands.command import Command
import utils

async def check(cmd: Command):
    money = cmd.guild.get_table_money()
    money_str = utils.print_money(money)
    if money == 0:
        await cmd.send(f'There is no money on the table!')
    else:
        await cmd.send(f'There is {money_str} on the table')

async def place(cmd: Command, money: int):
    money_str = utils.print_money(money)
    if money < 10:
        await cmd.send(f"You cannot place less than $10!")
    elif cmd.user.change_money(-money):
        cmd.guild.place_table_money(money)
        await cmd.send(f"You placed {money_str} on the table")
    else:
        await cmd.send(f"You don't have {money_str}!")

async def take(cmd: Command):
    money = cmd.guild.get_table_money()
    money_str = utils.print_money(money)
    if money == 0:
        await cmd.send(f'There is no money on the table!')
    else:
        await cmd.send(f'You took {money_str} from the table')
        cmd.user.change_money(money)
        cmd.guild.take_table_money()