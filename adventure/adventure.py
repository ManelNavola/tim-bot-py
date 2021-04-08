import asyncio
from abc import abstractmethod, ABC
from typing import Optional

from discord import Message
from discord_slash import SlashContext

import utils
from commands import messages
from commands.messages import MessagePlus
from user_data.user import User


class Chapter(ABC):
    def __init__(self, icon: str):
        self._adventure: Optional['Adventure'] = None
        self.message: Optional[MessagePlus] = None
        self._prefix: str = ""
        self._log: list[str] = []
        self.icon = icon

    def setup(self, adventure: 'Adventure', prefix: Optional[str]):
        self._prefix = prefix
        self._adventure = adventure
        self.message = adventure.message

    def add_log(self, msg: str):
        self._log.append(msg)

    async def send_log(self, msg: str):
        self.add_log(msg)
        await self.pop_log()

    async def pop_log(self):
        if self._prefix:
            self._log.insert(0, self._prefix)
        await self.message.edit('\n'.join(self._log))
        self._log.clear()

    @abstractmethod
    async def init(self, user: User):
        pass

    async def end(self):
        await self._adventure.end_chapter()


class Adventure:
    DELAY_TIME: int = 2

    def __init__(self, name: str, icon: str):
        self._name: str = name
        self._icon: str = icon
        self._user: Optional[User] = None
        self.message: Optional[MessagePlus] = None
        self._chapters: list[Chapter] = []
        self.saved_data: dict = {}
        self._current_chapter: int = 0

    async def init(self, ctx: SlashContext, user: User):
        assert len(self._chapters) > 0, "Tried starting adventure without chapters"
        self._user = user
        message: Message = await ctx.send(f"{self._user.get_name()} started {self._name}!\n{self.print_progress(None)}")
        await asyncio.sleep(1.5)
        self.message = messages.register_message_reactions(message, [self._user.id])
        chapter: Chapter = self._chapters.pop(0)
        chapter.setup(self, self.print_progress(chapter))
        await chapter.init(self._user)

    def add_chapter(self, chapter: Chapter):
        self._chapters.append(chapter)

    def print_progress(self, current_chapter: Optional[Chapter]) -> str:
        path: list[str] = []
        if current_chapter is None:
            path.append(utils.Emoji.COWBOY)
        else:
            path.append(f"{utils.Emoji.COWBOY}{current_chapter.icon}")
        for chapter in self._chapters:
            path.append(chapter.icon)
        return f"{self._icon} Progress: {' ⎯ '.join(path)}"

    async def end_chapter(self):
        now = utils.current_ms()
        await self.message.clear_reactions()
        diff = (utils.current_ms() - now) / 1000
        if diff < Adventure.DELAY_TIME:
            await asyncio.sleep(Adventure.DELAY_TIME - diff)
        if self._chapters:
            chapter: Chapter = self._chapters.pop(0)
            chapter.setup(self, self.print_progress(chapter))
            await chapter.init(self._user)
        else:
            await self.message.edit(f"{self._user.get_name()} finished {self._name}.")
            self._user.end_adventure()
            messages.unregister(self.message)
