from discord_slash import SlashContext
from data import users, guilds
from db import database


class Command:
    def __init__(self, ctx: SlashContext):
        self.ctx = ctx
        self.user = users.get(ctx.author_id)
        self.guild = guilds.get(ctx.guild_id)

    def send(self, msg):
        await self.ctx.send(msg)

    def send_hidden(self, msg):
        await self.ctx.send(msg, hidden=True)


async def call(ctx: SlashContext, func, *args):
    cmd = Command(ctx)  # Load command
    func(cmd, *args)  # Execute command
    cmd.user.save()  # Save user data (if any changed)
    cmd.guild.save()  # Save server data (if any changed)
    database.instance.commit()  # Commit changes (if any)
