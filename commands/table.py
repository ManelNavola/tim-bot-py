from commands.command import Command
from data import glob
import utils

async def check(cmd: Command):
    money = get_money(cmd)
    money_str = utils.print_money(money)
    if money == 0:
        await cmd.send(f'There is no money on the table!')
    else:
        await cmd.send(f'There is {money_str} on the table')

async def place(cmd: Command, money: int):
    money_str = utils.print_money(money)
    if money < 10:
        await cmd.send(f"You cannot place less than $10!")
    elif cmd.user.add_money(-money):
        place_money(cmd, money)
        await cmd.send(f"You placed {money_str} on the table")
    else:
        await cmd.send(f"You don't have {money_str}!")

async def take(cmd: Command):
    money = retrieve_money(cmd)
    money_str = utils.print_money(money)
    if money == 0:
        await cmd.send(f'There is no money on the table!')
    else:
        await cmd.send(f'You took {money_str} from the table')
        cmd.user.add_money(money)

def get_money(cmd: Command):
    data = glob.get_global(cmd.guild_id)
    if data['table_money'] == 0:
        return 0
    return data['table_money'] + (utils.now() - data['table_money_time']) // 15

def place_money(cmd: Command, amount: int):
    data = glob.get_global(cmd.guild_id)
    if data['table_money'] == 0:
        data['table_money_time'] = utils.now()
        data['table_money'] += amount
    else:
        data['table_money'] += amount
    glob.update_global(cmd.guild_id)

def retrieve_money(cmd: Command):
    data = glob.get_global(cmd.guild_id)
    money = get_money(cmd)
    if money == 0:
        return money
    data['table_money'] = 0
    glob.update_global(cmd.guild_id)
    return money