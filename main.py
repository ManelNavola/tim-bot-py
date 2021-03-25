import discord
import os
import psycopg2
from discord_slash import SlashCommand # Importing the newly installed library.

registered_guild_ids = [824723874544746507, 745340672109969440, 368145950717378560]

conn = psycopg2.connect(os.eniron['DATABASE_URL'], sslmode='require')
client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

@client.event
async def on_ready():
    print("Ready!")

@slash.slash(name="hello", description="Greet Tim", guild_ids=registered_guild_ids)
async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
    await ctx.ack()
    await ctx.send("Hey")

client.run(os.environ['CLIENT_KEY'])
