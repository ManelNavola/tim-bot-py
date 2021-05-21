import asyncio
import typing
from asyncio import Event
from typing import Optional

from discord import Message

import utils
from helpers.translate import tr
from item_data.stat import Stat
from user_data.user import User
# from adventure_classes.generic.user_adventure_data import UserAdventureData
from helpers import messages
from helpers.messages import MessagePlus
from enums.emoji import Emoji

if typing.TYPE_CHECKING:
    from adventure_classes.generic.chapter import Chapter
    from helpers.command import Command
    from adventure_classes.game_adventures.adventure_provider import AdventureInstance


class Adventure:
    def __init__(self, instance: 'AdventureInstance'):
        self._lang: str = ''
        self._instance: 'AdventureInstance' = instance
        self._users: set[User] = set()
        self._started_on: int = -1
        self._message: Optional[MessagePlus] = None
        self._chapters: list['Chapter'] = []
        self.saved_data: dict = {}
        self._current_chapter: int = 0
        self._event: Event = Event()
        self.lost: bool = False

    def get_lang(self) -> str:
        return self._lang

    def get_user_names(self) -> str:
        return ', '.join([user.get_name() for user in self._users])

    async def start(self, cmd: 'Command', users: list[User]):
        assert len(self._chapters) > 0, "Tried starting adventure without chapters"
        assert len(users) > 0, "Tried starting adventure without chapters"

        self._lang = cmd.lang

        self._started_on = utils.now()

        have_tokens: bool = True
        for user in users:
            if user.get_tokens() < self._instance.tokens:
                have_tokens = False
                break

        if not have_tokens:
            if len(users) == 1:
                await cmd.error(tr(self._lang, "ADVENTURE.NO_TOKENS_SINGLE",
                                   tokens=self._instance.tokens, EMOJI_TOKEN=Emoji.TOKEN))
            else:
                await cmd.error(tr(self._lang, "ADVENTURE.NO_TOKENS_MULTIPLE",
                                   names=', '.join([x.get_name() for x in users]), tokens=self._instance.tokens,
                                   EMOJI_TOKEN=Emoji.TOKEN))
            return

        self._users = users
        for user in users:
            user.remove_tokens(self._instance.tokens)
            user.start_adventure(self)
        message: Message
        if self._instance.override_str is not None:
            message = await cmd.send(self._instance.override_str.format(self.get_user_names()) + "\n"
                                     + self.print_progress(None))
        else:
            message = await cmd.send(tr(self._lang, "ADVENTURE.START", players=self.get_user_names(),
                                        name=tr(self._lang, self._instance.name)) + "\n" + self.print_progress(None))
        self._message = messages.register_message_reactions(message, [user.id for user in self._users])
        await asyncio.sleep(2)

        while self._chapters:
            chapter: Chapter = self._chapters.pop(0)
            chapter.setup(self, self.print_progress(chapter))
            await chapter.init()
            await self._event.wait()
            if self.lost:
                await self._message.edit(f"{self.get_user_names()} died on {tr(self._lang, self._instance.name)}...")
                for user in self._users:
                    user.end_adventure()
                messages.unregister(self._message)
                return
            else:
                for luser in self._users:
                    user: User = luser
                    ten_percent: int = max(1, round(Stat.HP.get_value(user.user_entity.get_stat(Stat.HP))))
                    if user.user_entity.get_persistent_value(Stat.HP) < ten_percent:
                        user.user_entity.set_persistent_value(Stat.HP, ten_percent)

            self._event.clear()

        await self._message.edit(f"{self.get_user_names()} finished {tr(self._lang, self._instance.name)}.")
        for user in self._users:
            user.end_adventure()
        messages.unregister(self._message)

    def has_finished(self):
        if utils.now() - self._started_on < 10:
            return False
        return self._message.has_finished()

    def get_user(self) -> User:
        assert len(self._users) == 1, "More than one user found"

        return next(iter(self._users))

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
            if not chapter.hidden:
                path.append(chapter.icon.value)
        return tr(self._lang, "ADVENTURE.PROGRESS", icon=self._instance.icon, progress=' ⎯ '.join(path))

    async def add_reaction(self, reaction: Emoji, hook: typing.Callable):
        await self._message.add_reaction(reaction, hook)

    async def remove_reaction(self, user: User, reaction: Emoji):
        await self._message.remove_reaction(user, reaction)

    async def remove_reactions(self, reaction: Emoji):
        await self._message.remove_reactions(reaction)

    async def append_message(self, msg: str):
        await self._message.edit(self._message.message.content + '\n' + msg)

    async def edit_message(self, msg: str):
        await self._message.edit(msg)

    async def _actually_end_chapter(self):
        await self._message.clear_reactions()
        self._event.set()

    async def end_chapter(self, lost: bool = False, skip: bool = False):
        self.lost = lost
        await self._message.clear_reactions()
        if skip:
            await self._actually_end_chapter()
        else:
            await self._message.add_reaction(Emoji.OK, self._actually_end_chapter)
