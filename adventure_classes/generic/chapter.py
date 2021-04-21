from abc import ABC, abstractmethod
from typing import Optional

from adventure_classes.generic.adventure import Adventure
from enums.emoji import Emoji


class Chapter(ABC):
    def __init__(self, icon: Emoji):
        self._adventure: Optional[Adventure] = None
        self._prefix: str = ""
        self._log: list[str] = []
        self.icon: Emoji = icon

    def get_adventure(self) -> Adventure:
        return self._adventure

    def setup(self, adventure: Adventure, prefix: Optional[str]) -> None:
        self._prefix = prefix
        self._adventure = adventure

    def add_log(self, msg: str) -> None:
        self._log.append(msg)

    async def send_log(self, msg: str) -> None:
        self.add_log(msg)
        await self.pop_log()

    async def pop_log(self) -> None:
        if self._prefix:
            self._log.insert(0, self._prefix)
        await self._adventure.edit_message('\n'.join(self._log))
        self._log.clear()

    @abstractmethod
    async def init(self) -> None:
        pass

    async def end(self, lost: bool = False, skip: bool = False) -> None:
        await self._adventure.end_chapter(lost, skip)
