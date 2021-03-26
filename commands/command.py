from discord_slash import SlashContext
from data import database

class Command:
    async def __init__(self, ctx: SlashContext, *args):
        self.ctx = ctx
        await ctx.ack()
        self.issue(args)
        database.commit()

    async def issue(self, *args):
        pass

    async def send(self, msg: str):
        await self.ctx.send(msg)