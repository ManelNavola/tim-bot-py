from discord_slash import SlashContext

class Command:
    def __init__(self, ctx: SlashContext):
        self.ctx = ctx
        self.user = users.get(ctx.author_id)
        if self.user.data['last_name'] != ctx.author.name:
            self.user.data['last_name'] = ctx.author.name
            self.user.register_changes('last_name')
        self.guild = guilds.get(ctx.guild_id)

    async def send(self, msg):
        await self.ctx.send(msg)

    async def send_hidden(self, msg):
        await self.ctx.send(msg, hidden=True)

from data import users, guilds
from db import database
import utils

async def call(ctx: SlashContext, func, *args):
    cmd = Command(ctx) # Load command
    if cmd.user.upgrade_log:
        await cmd.send_hidden('\n'.join(cmd.user.upgrade_log))
        cmd.user.upgrade_log = None
    await func(cmd, *args) # Execute command
    cmd.user.save() # Save user data (if any changed)
    cmd.guild.save() # Save server data (if any changed)
    database.instance.commit() # Commit changes (if any)