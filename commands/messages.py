from typing import Callable, Optional

import discord  # noqa
from discord import Message, Reaction  # noqa


class MessagePlus:
    def __init__(self, guild, message: Message, react_to: Optional[list[int]]):
        self.message: Message = message
        self.guild = guild
        self.react_to: Optional[list[int]] = react_to
        self._reaction_hooks: dict[str, Callable] = {}

    async def on_reaction(self, user, member: discord.User, input_reaction: Reaction) -> None:
        if user.id in self.react_to:
            for reaction, hook in self._reaction_hooks.items():
                if reaction.startswith(input_reaction.emoji):
                    await hook(self.guild, user, input_reaction.emoji)
                    await input_reaction.remove(member)
                    return

    async def add_reaction(self, reaction: str, hook: Callable) -> None:
        self._reaction_hooks[reaction] = hook
        await self.message.add_reaction(reaction)

    async def remove_reactions(self, reaction: str) -> None:
        del self._reaction_hooks[reaction]
        await self.message.clear_reaction(reaction)


_MESSAGE_ID_TO_MESSAGE_PLUS: dict[int, MessagePlus] = {}


def register_message_reactions(guild, message: Message, react_to: Optional[list[int]]) -> MessagePlus:
    mp: MessagePlus = MessagePlus(guild, message, react_to)
    _MESSAGE_ID_TO_MESSAGE_PLUS[mp.message.id] = mp
    return mp


def unregister(mp: MessagePlus):
    del _MESSAGE_ID_TO_MESSAGE_PLUS[mp.message.id]


async def on_reaction_add(user, member: discord.User, message_id: int, reaction: Reaction) -> None:
    mp: Optional[MessagePlus] = _MESSAGE_ID_TO_MESSAGE_PLUS.get(message_id)
    if mp is not None:
        await mp.on_reaction(user, member, reaction)
