# Imports
import os, discord, utils
from commands import command, simple, table, bet
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
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

@slash.subcommand(base="bet", name="place", description="Place or start a bet",
    options = [
        create_option(
            name="money",
            description="Amount of money to raised the bet to",
            option_type=4,
            required=True
        )
    ], guild_ids=registered_guild_ids)
async def _bet_place(ctx, money: int):
    await command.call(ctx, bet.place, money)

@slash.subcommand(base="bet", name="check", description="Check the current bet",
    guild_ids=registered_guild_ids)
async def _bet_check(ctx):
    await command.call(ctx, bet.check)

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