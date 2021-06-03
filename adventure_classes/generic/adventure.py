import asyncio
import typing
from asyncio import Event
from typing import Optional

from discord import Message

import utils
from helpers.translate import tr
from item_data.item_classes import Equipment
from user_data.user import User
from helpers import messages
from helpers.messages import MessagePlus
from enums.emoji import Emoji

if typing.TYPE_CHECKING:
    from adventure_classes.generic.chapter import Chapter
    from helpers.command import Command
    from adventure_classes.game_adventures.adventure_provider import AdventureInstance


class UserAdventureData:
    def __init__(self, user: User):
        self._user: User = user
        self._earned_money: int = 0
        self._enemies_defeated: int = 0
        self._items_found: list[Equipment] = []
        self._user.on_money_changed += self._on_money_changed

    def _on_money_changed(self, money: int):
        self._earned_money += money

    def unregister_all(self):
        self._user.on_money_changed -= self._on_money_changed

    def print(self, lang: str) -> str:
        has_plus: str = ''
        if self._earned_money > 0:
            has_plus = '+'
        return f"{has_plus}{utils.print_money(lang, self._earned_money)}"


class Adventure:
    def __init__(self, lang: str, instance: 'AdventureInstance', saved_data=None):
        if saved_data is None:
            saved_data = {}
        self._lang: str = lang
        self._instance: 'AdventureInstance' = instance
        self._users: dict[User, UserAdventureData] = {}
        self._started_on: int = -1
        self._message: Optional[MessagePlus] = None
        self._chapters: list['Chapter'] = []
        self.saved_data: dict = saved_data
        self._current_chapter: int = 0
        self._event: Event = Event()
        self.lost: bool = False
        self._finished: bool = False
        self.start_override_text: Optional[str] = None
        self.end_override_text: Optional[str] = None

    def get_message(self) -> MessagePlus:
        return self._message

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

        self._users = {user: UserAdventureData(user) for user in users}
        for user in users:
            user.remove_tokens(self._instance.tokens)
            user.start_adventure(self)
        message: Message
        if self.start_override_text is not None:
            message = await cmd.send(self.start_override_text + "\n"
                                     + self.print_progress(None))
        else:
            message = await cmd.send(tr(self._lang, "ADVENTURE.START", players=self.get_user_names(),
                                        name=tr(self._lang, self._instance.name)) + "\n" + self.print_progress(None))
        self._message = messages.register_message_reactions(message, {user.id for user in self._users})

        await asyncio.sleep(2)

        while self._chapters:
            chapter: Chapter = self._chapters.pop(0)
            chapter.setup(self, self.print_progress(chapter))
            await chapter.init()
            await self._event.wait()
            if self.lost:
                await self.finish(lost=True)
                return

            self._event.clear()

        await self.finish(lost=False)

    async def finish(self, lost: bool) -> None:
        # Ensure not finished
        if self._finished:
            return
        self._finished = True

        # End message
        end_log: str = '\n'.join([
            f"{user.get_name()}: {data.print(self._lang)}" for user, data in self._users.items()
        ])
        if self.end_override_text:
            await self._message.edit(self.end_override_text)
        else:
            if lost:
                await self._message.edit(tr(self._lang, 'ADVENTURE.DIED', EMOJI_SKULL=Emoji.DEAD,
                                            name=self.get_user_names(), location=tr(self._lang, self._instance.name))
                                         + f"\n({end_log})")
            else:
                await self._message.edit(tr(self._lang, 'ADVENTURE.FINISH', EMOJI_LOCATION=self._instance.icon,
                                            name=self.get_user_names(), location=tr(self._lang, self._instance.name))
                                         + f"\n({end_log})")

        # Cleanup
        for user in self._users:
            user.end_adventure()
        messages.unregister(self._message)

    def has_finished(self) -> bool:
        if utils.now() - self._started_on < 10:
            return False
        return self._message.has_finished()

    def get_user(self) -> User:
        assert len(self._users) == 1, "More than one user found"

        return next(iter(self._users.keys()))

    def get_users(self) -> list[User]:
        return list(self._users.keys())

    def insert_user(self, user: User) -> None:
        self._users[user] = UserAdventureData(user)

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
