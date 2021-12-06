import inspect
import typing
from typing import Callable, Optional, List, Set, Dict

import discord
from discord import Message, Reaction

import utils
from enums.emoji import Emoji

if typing.TYPE_CHECKING:
    from user_data.user import User
    from adventure_classes.generic.adventure import Adventure


class MessagePlus:
    FINISH_SECONDS: int = utils.TimeSlot(utils.TimeMetric.MINUTE, 14).seconds()

    def __init__(self, message: Message, react_to: Optional[Set[int]]):
        self.message: Message = message
        self.react_to: Optional[Set[int]] = react_to
        self._reaction_hooks: Dict[Emoji, Callable] = {}
        self._first_interaction: int = utils.now()
        self._finished: bool = False

    async def edit(self, msg: str):
        await self.message.edit(content=msg)

    def register(self, user_id: int):
        self.react_to.add(user_id)

    def unregister(self, user_id: int):
        self.react_to.remove(user_id)

    async def on_reaction(self, user: 'User', member: discord.Member, input_reaction: Reaction) -> None:
        if user.id in self.react_to:
            adventure: Optional['Adventure'] = user.get_adventure()
            if adventure is not None:
                if adventure._message != self:  # noqa
                    return
            for reaction, hook in self._reaction_hooks.items():
                if reaction.compare(input_reaction.emoji):
                    li = [user, reaction]
                    user.update(member.display_name, member)
                    await hook(*[li[i] for i in range(len(inspect.getfullargspec(hook).args) - 1)])
                    await input_reaction.remove(member)
                    user.save()  # Save user data (if any changed)
                    return

    async def add_reaction(self, reaction: Emoji, hook: Callable) -> None:
        self._reaction_hooks[reaction] = hook
        await self.message.add_reaction(reaction.first())

    async def remove_reaction(self, user: 'User', reaction: Emoji):
        await self.message.remove_reaction(reaction.first(), user.member)

    async def remove_reactions(self, reaction: Emoji) -> None:
        del self._reaction_hooks[reaction]
        await self.message.clear_reaction(reaction)

    async def clear_reactions(self):
        self._reaction_hooks.clear()
        await self.message.clear_reactions()

    def has_finished(self) -> bool:
        if utils.now() - self._first_interaction > MessagePlus.FINISH_SECONDS:
            self._finished = True
        return self._finished


_MESSAGE_ID_TO_MESSAGE_PLUS: Dict[int, MessagePlus] = {}


def register_message_reactions(message: Message, react_to: Optional[Set[int]]) -> MessagePlus:
    mp: MessagePlus = MessagePlus(message, react_to)
    _MESSAGE_ID_TO_MESSAGE_PLUS[mp.message.id] = mp
    if len(_MESSAGE_ID_TO_MESSAGE_PLUS) > 100:
        to_remove: List[int] = []
        for k, mp in _MESSAGE_ID_TO_MESSAGE_PLUS.items():
            if mp.has_finished():
                to_remove.append(k)
        for k in to_remove:
            del _MESSAGE_ID_TO_MESSAGE_PLUS[k]
    return mp


def unregister(mp: MessagePlus):
    del _MESSAGE_ID_TO_MESSAGE_PLUS[mp.message.id]


async def on_reaction_add(user, member: discord.Member, message_id: int, reaction: Reaction) -> None:
    mp: Optional[MessagePlus] = _MESSAGE_ID_TO_MESSAGE_PLUS.get(message_id)
    if mp is not None:
        await mp.on_reaction(user, member, reaction)
