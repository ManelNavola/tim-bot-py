import asyncio
import typing
from typing import Optional

from discord import Message
from discord_slash import SlashContext

import utils
from user_data.user import User
from adventure_classes.generic.user_adventure_data import UserAdventureData
from helpers import messages
from helpers.messages import MessagePlus
from enums.emoji import Emoji
if typing.TYPE_CHECKING:
    from adventure_classes.generic.chapter import Chapter


class Adventure:
    MIN_HEALTH: int = 10

    def __init__(self, name: str, icon: Emoji, tokens: int = 1):
        self._name: str = name
        self._icon: Emoji = icon
        self._users: dict[User, UserAdventureData] = {}
        self._started_on: int = -1
        self._message: Optional[MessagePlus] = None
        self._chapters: list['Chapter'] = []
        self.saved_data: dict = {}
        self._current_chapter: int = 0
        self._tokens: int = tokens
        self.lost: bool = False

    def get_user_names(self) -> str:
        return ', '.join([user.get_name() for user in self._users.keys()])

    async def start(self, ctx: SlashContext, users: list[User]):
        assert len(self._chapters) > 0, "Tried starting adventure without chapters"
        assert len(users) > 0, "Tried starting adventure without chapters"

        self._started_on = utils.now()

        have_tokens: bool = True
        for user in users:
            if user.get_tokens() < self._tokens:
                have_tokens = False
                break

        if not have_tokens:
            if len(users) == 1:
                await ctx.send(f"{Emoji.ERROR} You don't have enough tokens! (Required: {self._tokens}{Emoji.TOKEN})",
                               hidden=True)
            else:
                await ctx.send(f"{Emoji.ERROR} {', '.join([x.get_name() for x in users])} "
                               f"don't have enough tokens! (Required: {self._tokens}{Emoji.TOKEN})")
            return

        self._users = {user: UserAdventureData(user) for user in users}
        for user in users:
            user.remove_tokens(self._tokens)
            user.start_adventure(self)
        message: Message = await ctx.send(f"{self.get_user_names()} started {self._name}!\n{self.print_progress(None)}")
        self._message = messages.register_message_reactions(message, [user.id for user in self._users])
        await asyncio.sleep(1.5)
        chapter: Chapter = self._chapters.pop(0)
        chapter.setup(self, self.print_progress(chapter))
        await chapter.init()

    def has_finished(self):
        if utils.now() - self._started_on < 10:
            return False
        return self._message.has_finished()

    def get_users(self):
        return self._users

    def insert_chapter(self, chapter: 'Chapter', index: int = 0) -> None:
        self._chapters.insert(index, chapter)

    def add_chapter(self, chapter: 'Chapter') -> None:
        self._chapters.append(chapter)

    def print_progress(self, current_chapter: Optional['Chapter']) -> str:
        path: list[str] = []
        if current_chapter is None:
            path.append(Emoji.COWBOY.value)
        else:
            path.append(f"{Emoji.COWBOY}{current_chapter.icon}")
        for chapter in self._chapters:
            path.append(chapter.icon.value)
        return f"{self._icon} Progress: {' ⎯ '.join(path)}"

    async def add_reaction(self, reaction: Emoji, hook: typing.Callable):
        await self._message.add_reaction(reaction, hook)

    async def remove_reactions(self, reaction: Emoji):
        await self._message.remove_reactions(reaction)

    async def append_message(self, msg: str):
        await self._message.edit(self._message.message.content + '\n' + msg)

    async def edit_message(self, msg: str):
        await self._message.edit(msg)

    async def _actually_end_chapter(self):
        await self._message.clear_reactions()
        if self.lost:
            await self._message.edit(f"{self.get_user_names()} died on {self._name}...")
            for user in self._users:
                user.end_adventure()
            messages.unregister(self._message)
        else:
            if self._chapters:
                chapter: Chapter = self._chapters.pop(0)
                chapter.setup(self, self.print_progress(chapter))
                await chapter.init()
            else:
                await self._message.edit(f"{self.get_user_names()} finished {self._name}.")
                for user in self._users:
                    user.end_adventure()
                messages.unregister(self._message)

    async def end_chapter(self, lost: bool = False, skip: bool = False):
        self.lost = lost
        await self._message.clear_reactions()
        if skip:
            await self._actually_end_chapter()
        else:
            await self._message.add_reaction(Emoji.OK, self._actually_end_chapter)