import traceback
import typing
from typing import Optional, Callable

from discord_slash import SlashCommand, SlashContext

from db.database import PostgreSQL
from helpers import storage
from enums.emoji import Emoji
if typing.TYPE_CHECKING:
    from user_data.user import User
    from guild_data.guild import Guild


class CommandHandler:
    def __init__(self, db: PostgreSQL, slash: SlashCommand):
        self.db = db
        self.slash = slash

    def register_command(self,
                         cmd_calls: Callable,
                         *args,
                         base: Optional[str] = None,
                         name: Optional[str] = None,
                         description: Optional[str] = None,
                         guild_ids: Optional[list[int]] = None,
                         options: Optional[list[dict]] = None,
                         ignore_battle: bool = False):
        if options is None:
            options = []
        if base:
            @self.slash.subcommand(base=base, name=name, description=description, options=options, guild_ids=guild_ids)
            async def async_call(ctx: SlashContext, **kwargs):
                kwargs['ignore_battle'] = ignore_battle
                await self.call(ctx, cmd_calls, *args, **kwargs)
        else:
            @self.slash.slash(name=name, description=description, options=options, guild_ids=guild_ids)
            async def async_call(ctx: SlashContext, **kwargs):
                kwargs['ignore_battle'] = ignore_battle
                await self.call(ctx, cmd_calls, **kwargs)

    async def call(self, ctx: SlashContext, func, *args, **kwargs):
        cmd = Command(ctx, self.db)  # Create command

        # PREVIOUS UPDATES
        cmd.guild.register_user_id(cmd.user.id)
        cmd.user.update(ctx.author.display_name)

        # CALL COMMAND
        if (cmd.user.get_adventure() is not None) and (not kwargs['ignore_battle']):
            await cmd.error("You cannot issue commands while in an adventure!")
            return

        del kwargs['ignore_battle']
        try:
            await func(cmd, *args, **kwargs)  # Execute command
        except Exception as e:  # noqa
            cmd.db.rollback()
            traceback.print_exc()

        # SAVE
        cmd.user.save()  # Save user data (if any changed)
        cmd.guild.save()  # Save server data (if any changed)
        cmd.db.commit()  # Commit changes (if any)


class Command:
    def __init__(self, ctx: SlashContext, db: PostgreSQL):
        self.ctx: SlashContext = ctx
        self.db = db
        self.user: User = storage.get_user(db, ctx.author_id)
        self.guild: Guild = storage.get_guild(db, ctx.guild_id)

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
