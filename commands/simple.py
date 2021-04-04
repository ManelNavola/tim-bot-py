import discord

import utils
from commands.command import Command
from common import storage


async def inv(cmd: Command):
    await cmd.send_hidden(cmd.user.print(private=True, checking=False))


async def post_inv(cmd: Command):
    await cmd.send(cmd.user.print(private=True, checking=cmd.user.get_name()))


async def check(cmd: Command, member: discord.Member):
    if member.id in [824935594509336576, 824720383596560444]:
        await cmd.send(f"._.")
        return

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


async def leaderboard(cmd: Command):
    await cmd.send(cmd.guild.print_leaderboard())


async def stats(cmd: Command):
    await cmd.send(cmd.user.entity.print_detailed())


async def equip(cmd: Command, index: int):
    result = cmd.user.inventory.equip(index - 1)
    if result is not None:
        cmd.user.entity.update_items(cmd.user.inventory.get_equipment())
        await cmd.send(f"Equipped {result}")
    else:
        await cmd.error(f"Invalid item index!")


async def unequip(cmd: Command, index: int):
    result = cmd.user.inventory.unequip(index - 1)
    if result is not None:
        cmd.user.entity.update_items(cmd.user.inventory.get_equipment())
        await cmd.send(f"Unequipped {result}")
    else:
        await cmd.error(f"Invalid item index!")
