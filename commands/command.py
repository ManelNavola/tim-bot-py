from discord_slash import SlashContext
from data import database, users

async def call(ctx: SlashContext, func, *args):
    #await ctx.ack()
    await func(Command(ctx), *args)
    database.commit()

class Command:
    def __init__(self, ctx: SlashContext):
        self.ctx = ctx
        self.user = users.get(str(ctx.author_id))
        self.guild_id = ctx.guild_id

    async def send(self, msg: str):
        await self.ctx.send(msg)