import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand # Importing the newly installed library.
from discord_slash.utils.manage_commands import create_option
from utils import utils
from data import user_management, database
from data.glob import Table
import asyncio

registered_guild_ids = None
if not database.cursor():
    registered_guild_ids = [824723874544746507]

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print("Ready!")

@slash.slash(name="hello", description="Greet Tim",
    guild_ids=registered_guild_ids)
async def _hello(ctx):
    await ctx.ack()
    await ctx.send("Hey")

@slash.slash(name="money", description="Check your balance",
    guild_ids=registered_guild_ids)
async def _money(ctx):
    await ctx.ack()
    user = user_management.get(ctx)
    money = user.get_money()
    await ctx.send(f'You have ${money} (+$1/min)')
    database.commit()

@slash.subcommand(base="table", name="check", description="Check money on the table",
    guild_ids=registered_guild_ids)
async def _table_check(ctx):
    money = Table.get_money(ctx)
    if money == 0:
        await ctx.send(f'There is no money on the table!')
    else:
        await ctx.send(f'There is ${money} on the table')
        user = user_management.get(ctx)
        user.add_money(money)
        user_management.save(user)

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
    await ctx.ack()
    user = user_management.get(ctx)
    if money < 10:
        await ctx.send(f"You cannot place less than $10!")
    elif user.add_money(-money):
        Table.place_money(ctx, money)
        await ctx.send(f"You placed ${money} on the table")
    else:
        await ctx.send(f"You don't have ${money}!")
    database.commit()

@slash.subcommand(base="table", name="take", description="Take money on the table",
    guild_ids=registered_guild_ids)
async def _table_take(ctx):
    await ctx.ack()
    money = Table.retrieve_money(ctx)
    if money == 0:
        await ctx.send(f'There is no money on the table!')
    else:
        await ctx.send(f'You took ${money} from the table')
        user = user_management.get(ctx)
        user.add_money(money)
        user_management.save(user)
    database.commit()

if os.environ.get('CLIENT_KEY'):
    bot.run(os.environ['CLIENT_KEY'])
else:
    with open('local/d.txt') as f:
        bot.run(f.readline())