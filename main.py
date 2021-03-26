#import os
#import discord
#from discord.ext import commands
#from discord_slash import SlashCommand, SlashContext
#from discord_slash.utils.manage_commands import create_option
#from utils import utils
#from data import database
#from data.glob import Table
#from commands import command, simple

import os
import discord
from commands import command, simple, table
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
from data import database

registered_guild_ids = None
if not database.cursor():
    registered_guild_ids = [824723874544746507]

bot = commands.Bot(command_prefix='/') # intents=discord.Intents.all()
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print("Ready!")

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
            required=False
        )
    ], guild_ids=registered_guild_ids)
async def _table_place(ctx, money):
    await command.call(ctx, table.place, money)

@slash.subcommand(base="table", name="take", description="Take money on the table",
    guild_ids=registered_guild_ids)
async def _table_take(ctx):
    await command.call(ctx, table.take)

if os.environ.get('CLIENT_KEY'):
    bot.run(os.environ['CLIENT_KEY'])
else:
    with open('local/d.txt') as f:
        bot.run(f.readline())