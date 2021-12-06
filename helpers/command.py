import traceback
import typing
from typing import Optional, Callable, List

from discord_slash import SlashCommand, SlashContext

from commands import tutorial
from db.database import PostgreSQL
from helpers import storage
from enums.emoji import Emoji
from helpers.translate import tr

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
                         guild_ids: Optional[List[int]] = None,
                         options: Optional[List[dict]] = None,
                         ignore_battle: bool = False,
                         guild_only: bool = False,
                         ignore_all: bool = False):
        if options is None:
            options = []
        if guild_only:
            description = '[G] ' + description
        if base:
            @self.slash.subcommand(base=base, name=name, description=description, options=options, guild_ids=guild_ids)
            async def async_call(ctx: SlashContext, **kwargs):
                kwargs['ignore_battle'] = ignore_battle or ignore_all
                kwargs['guild_only'] = guild_only
                kwargs['ignore_all'] = ignore_all
                await self.call(ctx, cmd_calls, *args, **kwargs)
        else:
            @self.slash.slash(name=name, description=description, options=options, guild_ids=guild_ids)
            async def async_call(ctx: SlashContext, **kwargs):
                kwargs['ignore_battle'] = ignore_battle or ignore_all
                kwargs['guild_only'] = guild_only
                kwargs['ignore_all'] = ignore_all
                await self.call(ctx, cmd_calls, **kwargs)

    async def call(self, ctx: SlashContext, func, *args, **kwargs):
        cmd = Command(ctx, self.db)  # Create command

        # PREVIOUS UPDATES
        if cmd.guild:
            cmd.guild.register_user_id(cmd.user.id)
        cmd.user.update(ctx.author.display_name, ctx.author)

        # CALL COMMAND
        if (cmd.user.get_adventure() is not None) and (not kwargs['ignore_battle']):
            await cmd.error(tr(cmd.lang, 'COMMAND.IN_ADVENTURE'))
            return
        if kwargs['guild_only'] and (cmd.guild is None):
            await cmd.error(tr(cmd.lang, 'COMMAND.GUILD_ONLY'))
            return

        ignore_all: bool = kwargs['ignore_all']
        del kwargs['ignore_battle']
        del kwargs['ignore_all']
        del kwargs['guild_only']

        tutorial_stage: int = cmd.user.get_tutorial_stage()
        if tutorial_stage != -1 and (cmd.user.get_adventure() is None) and (not ignore_all):
            if cmd.guild:
                await tutorial.play_tutorial(cmd, tutorial_stage)
            else:
                await cmd.send_hidden("You must first talk to me in a guild to be able to DM me!")
        else:
            try:
                await func(cmd, *args, **kwargs)  # Execute command
            except Exception as e:  # noqa
                # Cursor fallback
                cmd.db.rollback()
                if cmd.db.get_cursor().closed:
                    cmd.db.reset_cursor()
                traceback.print_exc()

        # SAVE
        cmd.user.save()  # Save user data (if any changed)
        if cmd.guild:
            cmd.guild.save()  # Save server data (if any changed)
        cmd.db.commit()  # Commit changes (if any)


class Command:
    def __init__(self, ctx: SlashContext, db: PostgreSQL):
        self.ctx: SlashContext = ctx
        self.db = db
        self.user: User = storage.get_user(db, ctx.author_id)
        self.guild: Optional[Guild] = None
        self.lang: str = 'en'
        if ctx.guild_id is not None:
            self.guild = storage.get_guild(db, ctx.guild_id)
            self.lang = self.guild.get_lang()
        else:
            self.lang = self.user.get_lang()

    async def send(self, msg: str):
        return await self.ctx.send(msg)

    async def send_hidden(self, msg: str):
        if self.guild:
            await self.ctx.send(msg, hidden=True)
        else:
            await self.send(msg)

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
