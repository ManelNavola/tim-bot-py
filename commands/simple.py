import discord

import utils
from commands.command import Command
from data import storage


async def inv(cmd: Command):
    await cmd.send_hidden(cmd.user.print(private=True, checking=False))


async def post_inv(cmd: Command):
    await cmd.send(cmd.user.print(private=True, checking=cmd.user.get_name()))


async def check(cmd: Command, member: discord.Member):
    user = storage.get_user(member.id, False)
    if not user:
        await cmd.send(f"This user hasn't interacted with me yet")
        return
    await cmd.send(user.print(private=False, checking=True))


async def transfer(cmd: Command):
    if cmd.user.get_bank() == 0:
        await cmd.error("Your bank is empty!")
    else:
        transferred = cmd.user.withdraw_bank()
        if transferred == 0:
            await cmd.error("You cannot hold more money!")
        else:
            await cmd.send_hidden(f"Transferred {utils.print_money(transferred)} from the bank "
                                  f"(you now have {utils.print_money(cmd.user.get_money())})")
