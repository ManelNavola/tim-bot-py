import asyncio
import typing
from typing import Optional

from discord import Message
from discord_slash import SlashContext

from user_data.user import User
from adventure_classes.generic.user_adventure_data import UserAdventureData
from helpers import messages
from helpers.messages import MessagePlus
from enums.emoji import Emoji
if typing.TYPE_CHECKING:
    from adventure_classes.generic.chapter import Chapter


class Adventure:
    MIN_HEALTH: int = 10

    def __init__(self, name: str, icon: Emoji):
        self._name: str = name
        self._icon: Emoji = icon
        self._users: dict[User, UserAdventureData] = {}
        self._message: Optional[MessagePlus] = None
        self._chapters: list['Chapter'] = []
        self.saved_data: dict = {}
        self._current_chapter: int = 0
        self.lost: bool = False

    def get_user_names(self) -> str:
        return ', '.join([user.get_name() for user in self._users.keys()])

    async def start(self, ctx: SlashContext, users: list[User]):
        assert len(self._chapters) > 0, "Tried starting adventure without chapters"
        self._users = {user: UserAdventureData(user) for user in users}
        for user in users:
            user.start_adventure(self)
        message: Message = await ctx.send(f"{self.get_user_names()} started {self._name}!\n{self.print_progress(None)}")
        await asyncio.sleep(1.5)
        self._message = messages.register_message_reactions(message, [user.id for user in self._users])
        chapter: Chapter = self._chapters.pop(0)
        chapter.setup(self, self.print_progress(chapter))
        await chapter.init()

    # TODO: huh confirm
    def has_finished(self):
        return self._message.has_finished()

    def get_users(self):
        return self._users

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
