from helpers.command import Command
from helpers.translate import tr


async def equip(cmd: Command, number: int):
    result = cmd.user.inventory.equip(number - 1)
    if result is not None:
        cmd.user.user_entity.update_equipment(cmd.user.inventory.get_equipment())
        await cmd.send_hidden(tr(cmd.lang, 'EQUIPMENT.EQUIP', item=result))
    else:
        await cmd.error(tr(cmd.lang, 'EQUIPMENT.INVALID_INDEX'))


async def equip_best(cmd: Command):
    tp = []
    cmd.user.inventory.equip_best()
    for item in cmd.user.inventory.get_equipment():
        tp.append(tr(cmd.lang, 'EQUIPMENT.EQUIP', item=item.print()))
    if tp:
        await cmd.send_hidden('\n'.join(tp))
    else:
        await cmd.error(tr(cmd.lang, 'EQUIPMENT.EMPTY'))


async def unequip(cmd: Command, number: int):
    result = cmd.user.inventory.unequip(number - 1)
    if result is not None:
        cmd.user.user_entity.update_equipment(cmd.user.inventory.get_equipment())
        await cmd.send_hidden(tr(cmd.lang, 'EQUIPMENT.UNEQUIP', item=result))
    else:
        await cmd.error(tr(cmd.lang, 'EQUIPMENT.INVALID_INDEX'))


async def unequip_all(cmd: Command):
    if len(cmd.user.inventory.get_equipment()) == 0:
        await cmd.error(tr(cmd.lang, 'EQUIPMENT.NO_EQUIPPED'))
        return
    cmd.user.inventory.unequip_all()
    await cmd.send_hidden(tr(cmd.lang, 'EQUIPMENT.UNEQUIP_ALL'))
