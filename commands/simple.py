import discord

import utils
from helpers.command import Command
from helpers import storage


async def inv(cmd: Command):
    await cmd.send_hidden(cmd.user.print(private=True, checking=False))


async def post_inv(cmd: Command):
    await cmd.send(cmd.user.print(private=True, checking=cmd.user.get_name()))


async def check(cmd: Command, user: discord.Member):
    if user.id in [824935594509336576, 824720383596560444]:
        await cmd.send("._.")
        return

    user_m = storage.get_user(cmd.db, user.id, False)
    if not user_m:
        await cmd.send_hidden("This user hasn't interacted with me yet!")
        return
    await cmd.send(user_m.print(private=False, checking=True))


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
    await cmd.send_hidden(cmd.user.user_entity.print_detailed_refill(cmd.user.get_refill()))


async def equip(cmd: Command, number: int):
    result = cmd.user.inventory.equip(number - 1)
    if result is not None:
        cmd.user.user_entity.update_equipment(cmd.user.inventory.get_equipment())
        await cmd.send_hidden(f"Equipped {result}")
    else:
        await cmd.error("Invalid item index!")


async def equip_best(cmd: Command):
    tr = []
    cmd.user.inventory.equip_best()
    for item in cmd.user.inventory.get_equipment():
        tr.append(f"Equipped {item.print()}")
    if tr:
        await cmd.send('\n'.join(tr))
    else:
        await cmd.error("You have no equipment")


async def unequip(cmd: Command, number: int):
    result = cmd.user.inventory.unequip(number - 1)
    if result is not None:
        cmd.user.user_entity.update_equipment(cmd.user.inventory.get_equipment())
        await cmd.send_hidden(f"Unequipped {result}")
    else:
        await cmd.error("Invalid item index!")


async def unequip_all(cmd: Command):
    if len(cmd.user.inventory.get_equipment()) == 0:
        await cmd.error("You don't have anything equipped!")
        return
    cmd.user.inventory.unequip_all()
    await cmd.send_hidden("Unequipped all items")


async def abilities(cmd: Command):
    tp = []
    for item in cmd.user.inventory.get_equipment():
        if item.data.ability is not None:
            tp.append(f"{item.data.get_description().type.get_type_icon()} {item.data.ability.get_name()}: "
                      f"{item.data.ability.get_effect()} (once per battle)")
    if not tp:
        await cmd.send_hidden("You currently have no abilities equipped")
    else:
        await cmd.send_hidden('\n'.join(tp))
