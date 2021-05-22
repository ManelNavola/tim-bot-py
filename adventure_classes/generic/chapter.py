import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from adventure_classes.generic.adventure import Adventure
from enums.emoji import Emoji


class Chapter(ABC):
    def __init__(self, icon: Emoji):
        self._adventure: Optional[Adventure] = None
        self._prefix: str = ""
        self._log: list[list[str]] = []
        self.icon: Emoji = icon
        self.hidden: bool = False
        self._cleared: bool = True

    def get_lang(self) -> str:
        return self._adventure.get_lang()

    def get_adventure(self) -> Adventure:
        return self._adventure

    def setup(self, adventure: Adventure, prefix: Optional[str]) -> None:
        self._prefix = prefix
        self._adventure = adventure

    async def append(self, msg: str) -> None:
        if self._cleared:
            self._cleared = False
            await self.get_adventure().edit_message(self._prefix + '\n' + msg)
        else:
            await self.get_adventure().append_message(msg)

    async def append_and_wait(self, msg: str, time: int) -> None:
        await self.append(msg)
        await asyncio.sleep(time)

    def _get_log(self) -> list[str]:
        return self._log[len(self._log) - 1]

    def start_log(self) -> None:
        self._log.append([])

    def clear_log(self):
        self._log.clear()
        self._cleared = True

    def add_log(self, msg: str) -> None:
        if not msg:
            return
        if not self._log:
            self.start_log()
        self._get_log().append(msg)

    async def send_log(self, msg: str = '') -> None:
        if msg:
            if not self._log:
                self.start_log()
            self.add_log(msg)
        popped_log: str = '\n'.join(self._log.pop(len(self._log) - 1))
        if self._log:
            self._log[len(self._log) - 1].append(popped_log)
        else:
            await self.append(popped_log)

    @abstractmethod
    async def init(self) -> None:
        pass

    async def end(self, lost: bool = False, skip: bool = False) -> None:
        self.clear_log()
        await self._adventure.end_chapter(lost, skip)
