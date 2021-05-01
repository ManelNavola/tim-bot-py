from typing import Callable

from adventure_classes.generic.chapter import Chapter
from enums.emoji import Emoji


class ChoiceChapter(Chapter):
    def __init__(self, emoji: Emoji, msg: str = '', skip: bool = True):
        super().__init__(emoji)
        self.msg: str = msg
        self.choices: list[tuple[Emoji, str, Callable]] = []
        self.skip = skip

    def add_choice(self, icon: Emoji, desc: str, result: Callable):
        self.choices.append((icon, desc, result))
        return self

    async def init(self):
        self.add_log(self.msg)
        for choice in self.choices:
            self.add_log(f"{choice[0].first()} {choice[1]}")
        await self.send_log()
        for choice in self.choices:
            await self.get_adventure().add_reaction(choice[0], self.choose_path(choice[2]))

    def choose_path(self, action: Callable):
        async def end_path():
            action(self.get_adventure())
            await self.end(skip=self.skip)
        return end_path
