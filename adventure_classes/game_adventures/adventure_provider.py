from typing import Optional, Callable

from adventure_classes.game_adventures import forest, tutorial
from adventure_classes.generic.adventure import Adventure
from enums.emoji import Emoji
from helpers.command import Command


class AdventureInstance:
    def __init__(self, setup_call: Callable, name: str, icon: Emoji, tokens: int = 1,
                 override_str: Optional[str] = None):
        self.name: str = name
        self.icon: Emoji = icon
        self.tokens: int = tokens
        self.override_str = override_str
        self._setup_call: Callable = setup_call

    async def start(self, cmd: Command):
        adventure: Adventure = Adventure(self)
        await self._setup_call(cmd, adventure)
        await adventure.start(cmd, [cmd.user])


name_to_adventure: dict[str, AdventureInstance] = {
    '_tutorial': AdventureInstance(tutorial.setup, 'TUTORIAL.NAME', Emoji.TUTORIAL, tokens=0),
    'Forest': AdventureInstance(forest.setup, 'FOREST.NAME', Emoji.FOREST)
}
