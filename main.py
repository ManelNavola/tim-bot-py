import discord
import os
from discord_slash import SlashCommand # Importing the newly installed library.
from utils import utils
from data import user_management
import asyncio

cache = {}
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
    user = user_management.get(ctx.author_id)
    money = user.get_money()
    await ctx.send(f'You have ${money}')

client.run(os.environ['CLIENT_KEY'])
