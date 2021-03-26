import discord
import os
from discord_slash import SlashCommand # Importing the newly installed library.
from discord_slash.utils.manage_commands import create_option
from utils import utils
from data import user_management
from data.glob import Table
import asyncio

cache = {}
table = Table()
registered_guild_ids = [824723874544746507, 745340672109969440, 368145950717378560]

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

@client.event
async def on_ready():
    print("Ready!")

@slash.slash(name="hello", description="Greet Tim", guild_ids=registered_guild_ids)
async def _ping(ctx):
    await ctx.ack()
    await ctx.send("Hey")

@slash.slash(name="money", description="Check your balance", guild_ids=registered_guild_ids)
async def _money(ctx):
    await ctx.ack()
    user = user_management.get(ctx)
    money = user.get_money()
    await ctx.send(f'You have ${money} (+$1/min)')

@slash.slash(name="table", description="Place or get money from the table",
    options=[
        create_option(
            name="money",
            description="Amount of money to place on the table",
            option_type=4,
            required=False
        )
    ], guild_ids=registered_guild_ids)
async def _table(ctx, money: int):
    await ctx.ack()
    user = user_management.get(ctx)
    if money:
        if user.add_money(-money):
            await ctx.send(f"You placed ${money} on the table")
        else:
            await ctx.send(f"You don't have ${money}!")
    else:
        money = table.retrieve_money()
        if money == 0:
            await ctx.send(f'There is no money on the table!')
        else:
            await ctx.send(f'You took ${money} from the table')
            user.add_money(money)
    user_management.save(user)

client.run(os.environ['CLIENT_KEY'])
