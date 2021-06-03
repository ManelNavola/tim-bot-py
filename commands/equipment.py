from helpers.action_result import ActionResult
from helpers.command import Command


async def equip(cmd: Command, slot: str):
    result: ActionResult = cmd.user.inventory.equip(slot)
    if result.success:
        await cmd.send_hidden(result.tr(cmd.lang))
    else:
        await cmd.error(result.tr(cmd.lang))


async def equip_best(cmd: Command):
    result = cmd.user.inventory.equip_best()
    if result.success:
        await cmd.send_hidden(result.tr(cmd.lang))
    else:
        await cmd.error(result.tr(cmd.lang))


async def unequip(cmd: Command, slot: str):
    result = cmd.user.inventory.unequip(slot)
    if result.success:
        await cmd.send_hidden(result.tr(cmd.lang))
    else:
        await cmd.error(result.tr(cmd.lang))


async def sell(cmd: Command, slot: str):
    result: ActionResult = cmd.user.inventory.sell(cmd.lang, slot)
    if result.success:
        cmd.user.add_money(result.price)
        await cmd.send_hidden(result.tr(cmd.lang))
    else:
        await cmd.error(result.tr(cmd.lang))
