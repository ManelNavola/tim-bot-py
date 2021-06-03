from typing import Optional, Callable

from adventure_classes.game_adventures import forest, tutorial, lake, duel
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.chapter import Chapter
from enums.emoji import Emoji
from helpers.command import Command
from user_data.user import User


class AdventureInstance:
    def __init__(self, setup_call: Callable, name: str, icon: Emoji, tokens: int = 1):
        self.name: str = name
        self.icon: Emoji = icon
        self.tokens: int = tokens
        self._setup_call: Callable = setup_call

    async def start(self, cmd: Command, users: list[User], saved_data=None):
        if saved_data is None:
            saved_data = {}
        adventure: Adventure = Adventure(cmd.lang, self, saved_data)
        await self._setup_call(cmd, adventure)
        await adventure.start(cmd, users)


name_to_adventure: dict[str, AdventureInstance] = {
    '_tutorial': AdventureInstance(tutorial.setup, 'TUTORIAL.NAME', Emoji.TUTORIAL, tokens=0),
    'Forest': AdventureInstance(forest.setup, 'FOREST.NAME', Emoji.FOREST),
    'Lake': AdventureInstance(lake.setup, 'LAKE.NAME', Emoji.LAKE),
    '_duel': AdventureInstance(duel.setup, 'DUEL.NAME', Emoji.BATTLE, tokens=0)
}


async def nothing():
    return


async def quick_adventure(cmd, users: list[User], name: str, icon: Emoji, tokens: int, chapters: list[Chapter]):
    adventure: Adventure = Adventure(cmd.lang, AdventureInstance(nothing, name, icon, tokens))
    for chapter in chapters:
        adventure.add_chapter(chapter)
    await adventure.start(cmd, users)
