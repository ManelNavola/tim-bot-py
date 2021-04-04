from typing import Optional, Union

from discord import Message
from discord_slash import SlashContext

import utils
from common import storage
from guild_data.guild import Guild
from user_data.user import User
from db import database


class Command:
    def __init__(self, ctx: SlashContext):
        self.ctx: SlashContext = ctx
        self.user: User = storage.get_user(ctx.author_id)
        self.guild: Guild = storage.get_guild(ctx.guild_id)

    async def send(self, msg: str):
        await self.ctx.send(msg)

    async def send_hidden(self, msg: str):
        await self.ctx.send(msg, hidden=True)

    async def error(self, msg: str, hidden: bool = True):
        await self.ctx.send(f"{utils.Emoji.ERROR} {msg}", hidden=hidden)


class MockSlashContext(SlashContext):
    def __init__(self): # noqa
        pass

    async def send(self, msg: str, hidden: bool = False):  # noqa
        if hidden:
            print("(hidden) >", msg)
        else:
            print(msg)


class MockCommand(Command):
    def __init__(self): # noqa
        self.ctx = MockSlashContext()

    def send(self, msg: str):
        print(msg)

    def send_hidden(self, msg: str):
        print("(hidden) >", msg)

    def error(self, msg: str, hidden: bool=True):
        if hidden:
            print("[X] (hidden) >", msg)
        else:
            print("[X]", msg)


async def call(ctx: SlashContext, func, *args):
    cmd = Command(ctx)  # Load command

    # PREVIOUS UPDATES
    cmd.guild.register_user_id(cmd.user.id)
    cmd.user.update_name(ctx.author.display_name)

    # CALL COMMAND
    await func(cmd, *args)  # Execute command

    # SAVE
    cmd.user.save()  # Save user data (if any changed)
    cmd.guild.save()  # Save server data (if any changed)
    database.INSTANCE.commit()  # Commit changes (if any)
