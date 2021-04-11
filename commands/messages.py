import inspect
from typing import Callable, Optional

import discord
from discord import Message, Reaction

import utils
from enums.emoji import Emoji


class MessagePlus:
    FINISH_SECONDS: int = utils.TimeSlot(utils.TimeMetric.MINUTE, 30).seconds()

    def __init__(self, message: Message, react_to: Optional[list[int]]):
        self.message: Message = message
        self.react_to: Optional[list[int]] = react_to
        self._reaction_hooks: dict[Emoji, Callable] = {}
        self.last_interaction: int = utils.now()
        self._finished: bool = False

    async def edit(self, msg: str):
        self.last_interaction = utils.now()
        await self.message.edit(content=msg)

    async def on_reaction(self, user, member: discord.User, input_reaction: Reaction) -> None:
        if user.id in self.react_to:
            self.last_interaction = utils.now()
            for reaction, hook in self._reaction_hooks.items():
                if reaction.compare(input_reaction.emoji):
                    li = [user, input_reaction.emoji]
                    await hook(*[li[i] for i in range(len(inspect.getfullargspec(hook).args) - 1)])
                    await input_reaction.remove(member)
                    return

    async def add_reaction(self, reaction: Emoji, hook: Callable) -> None:
        self.last_interaction = utils.now()
        self._reaction_hooks[reaction] = hook
        await self.message.add_reaction(reaction.first())

    async def remove_reactions(self, reaction: Emoji) -> None:
        self.last_interaction = utils.now()
        del self._reaction_hooks[reaction]
        await self.message.clear_reaction(reaction)

    async def clear_reactions(self):
        self.last_interaction = utils.now()
        self._reaction_hooks.clear()
        await self.message.clear_reactions()

    def has_finished(self) -> bool:
        if utils.now() - self.last_interaction > MessagePlus.FINISH_SECONDS:
            self._finished = True
        return self._finished


_MESSAGE_ID_TO_MESSAGE_PLUS: dict[int, MessagePlus] = {}


def register_message_reactions(message: Message, react_to: Optional[list[int]]) -> MessagePlus:
    mp: MessagePlus = MessagePlus(message, react_to)
    _MESSAGE_ID_TO_MESSAGE_PLUS[mp.message.id] = mp
    if len(_MESSAGE_ID_TO_MESSAGE_PLUS) > 100:
        to_remove: list[int] = []
        for k, mp in _MESSAGE_ID_TO_MESSAGE_PLUS.items():
            if mp.has_finished():
                to_remove.append(k)
        for k in to_remove:
            del _MESSAGE_ID_TO_MESSAGE_PLUS[k]
    return mp


def unregister(mp: MessagePlus):
    del _MESSAGE_ID_TO_MESSAGE_PLUS[mp.message.id]


async def on_reaction_add(user, member: discord.User, message_id: int, reaction: Reaction) -> None:
    mp: Optional[MessagePlus] = _MESSAGE_ID_TO_MESSAGE_PLUS.get(message_id)
    if mp is not None:
        await mp.on_reaction(user, member, reaction)
