from discord_slash import SlashContext

class Command:
    def __init__(self, ctx: SlashContext):
        self.ctx = ctx
        self.user = users.get(ctx.author_id)
        self.user_name = ctx.author.name
        self.guild = guilds.get(ctx.guild_id)

    async def send(self, *args, **kwargs):
        await self.ctx.send(*args, **kwargs)

    def get_user_name(self, user_id: int):
        user = self.ctx.bot.get_user(user_id)
        if not user:
            return "_Unknown_"
        return user.name

    def __str__(self):
        return f"User id: {self.user.id}, Guild id: {self.guild.id}"

from data import users, guilds
from db import database
import utils

async def call(ctx: SlashContext, func, *args):
    cmd = Command(ctx) # Load command
    await func(cmd, *args) # Execute command
    cmd.user.save() # Save user data (if any changed)
    cmd.guild.save() # Save server data (if any changed)
    database.instance.commit() # Commit changes (if any)

