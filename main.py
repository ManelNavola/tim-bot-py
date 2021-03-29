# Imports
import os, discord, utils
from commands import command, simple, table, bet, upgrade
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands
from db import database
from db.database import PostgreSQL, JSONDatabase

# Load database
db_instance = None
registered_guild_ids = None
if utils.is_test():
    # Local test
    db_instance = JSONDatabase('local/data.json')
    registered_guild_ids = [824723874544746507] # Update quick
else:
    # Production
    db_instance = PostgreSQL(os.environ['DATABASE_URL'])

database.instance = db_instance

bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands=True)

# Ready event
@bot.event
async def on_ready():
    print("Ready!")
    if utils.is_test():
        from functools import partial
        from concurrent.futures.thread import ThreadPoolExecutor
        import asyncio
        from data import users

        rie = partial(asyncio.get_event_loop().run_in_executor, ThreadPoolExecutor(1))
        while not bot.is_closed():
            print("> ", end='')
            c = await rie(input)
            args = c.split(' ')
            if args[0] == 'restart':
                print("Restarting bot...")
                database.instance.save()
                os.system("python main.py")
                exit()
            elif args[0] == 'reset':
                database.instance.reset()
                print("Data cleared")
                print("Restarting bot...")
                database.instance.save()
                os.system("python main.py")
                exit()
            elif args[0] == 'clear':
                database.instance.reset()
                print("Data cleared")
            elif args[0] == 'setmoney':
                user = users.get(116901729823358977)
                money = int(args[1])
                user.change_money(money - user.get_money())
                user.save()
                database.instance.commit()
                money_str = utils.print_money(money)
                print(f"Set money to {money_str}")
            elif len(args[0]) > 0:
                print("Unknown command")

# Register commands
@slash.slash(name="check", description="Check information about a user",
    options = [
        create_option(
            name="user",
            description="User to check",
            option_type=6,
            required=True
        )
    ], guild_ids=registered_guild_ids)
async def _check(ctx: SlashContext, member: discord.Member):
    await command.call(ctx, simple.check, member)

@slash.slash(name="inv", description="Check your inventory",
    guild_ids=registered_guild_ids)
async def _inv(ctx):
    await command.call(ctx, simple.inv)

@slash.slash(name="transfer", description="Retrieves money from the bank",
    guild_ids=registered_guild_ids)
async def _bank(ctx):
    await command.call(ctx, simple.transfer)

@slash.subcommand(base="bet", name="info", description="Get information about betting", guild_ids=registered_guild_ids)
async def _bet_info(ctx):
    await command.call(ctx, bet.info)

@slash.subcommand(base="bet", name="add", description="Place or start a bet",
    options = [
        create_option(
            name="money",
            description="Amount of money to raised the bet to",
            option_type=4,
            required=True
        )
    ], guild_ids=registered_guild_ids)
async def _bet_add(ctx, money: int):
    await command.call(ctx, bet.add, money)

@slash.subcommand(base="bet", name="check", description="Check the current bet",
    guild_ids=registered_guild_ids)
async def _bet_check(ctx):
    await command.call(ctx, bet.check)

@slash.subcommand(base="upgrade", name="menu", description="View available upgrades", guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.menu)

@slash.subcommand(base="upgrade", name="money_limit", description="Upgrade money capacity", guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.upgrade, 'money_limit')

@slash.subcommand(base="upgrade", name="bank", description="Upgrade bank capacity", guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.upgrade, 'bank')

@slash.subcommand(base="upgrade", name="garden", description="Upgrade garden production", guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.upgrade, 'garden')

@slash.slash(name="postinv", description="Post your inventory",
    guild_ids=registered_guild_ids)
async def _inv(ctx):
    await command.call(ctx, simple.postinv)

@slash.subcommand(base="table", name="check", description="Check money on the table",
    guild_ids=registered_guild_ids)
async def _table_check(ctx):
    await command.call(ctx, table.check)

@slash.subcommand(base="table", name="place", description="Place money on the table",
    options = [
        create_option(
            name="money",
            description="Amount of money to place on the table",
            option_type=4,
            required=True
        )
    ], guild_ids=registered_guild_ids)
async def _table_place(ctx, money):
    await command.call(ctx, table.place, money)

@slash.subcommand(base="table", name="take", description="Take money on the table",
    guild_ids=registered_guild_ids)
async def _table_take(ctx):
    await command.call(ctx, table.take)

# Hacky uwu
if utils.is_test():
    with open('local/d.txt') as f:
        bot.run(f.readline())
else:
    bot.run(os.environ['CLIENT_KEY'])