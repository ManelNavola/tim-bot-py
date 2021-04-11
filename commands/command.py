import traceback

from discord_slash import SlashContext

from common import storage
from db import database
from enums.emoji import Emoji
from guild_data.guild import Guild
from user_data.user import User


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
        await self.ctx.send(f"{Emoji.ERROR} {msg}", hidden=hidden)


class MockSlashContext(SlashContext):
    def __init__(self):  # noqa
        pass

    async def send(self, msg: str, hidden: bool = False):  # noqa
        if hidden:
            print("(hidden) >", msg)
        else:
            print(msg)


class MockCommand(Command):
    def __init__(self):  # noqa
        self.ctx = MockSlashContext()

    def send(self, msg: str):
        print(msg)

    def send_hidden(self, msg: str):
        print("(hidden) >", msg)

    def error(self, msg: str, hidden: bool = True):
        if hidden:
            print("[X] (hidden) >", msg)
        else:
            print("[X]", msg)


async def call(ctx: SlashContext, func, *args, ignore_battle: bool = False):
    cmd = Command(ctx)  # Load command

    # PREVIOUS UPDATES
    cmd.guild.register_user_id(cmd.user.id)
    cmd.user.update_name(ctx.author.display_name)

    # CALL COMMAND
    if (cmd.user.get_adventure() is not None) and (not ignore_battle):
        await cmd.error("You cannot issue commands while in an adventure!")
        return

    try:
        await func(cmd, *args)  # Execute command
    except Exception as e:  # noqa
        database.INSTANCE.rollback()
        traceback.print_exc()

    # SAVE
    cmd.user.save()  # Save user data (if any changed)
    cmd.guild.save()  # Save server data (if any changed)
    database.INSTANCE.commit()  # Commit changes (if any)
