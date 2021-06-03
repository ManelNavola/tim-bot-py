from helpers.action_result import ActionResult
from helpers.command import Command
from enums.emoji import Emoji
from helpers.translate import tr
from user_data.inventory import SlotType


async def check(cmd: Command):
    await cmd.send(cmd.guild.shop.print())


def get_slot_type(slot: str):
    if slot.isnumeric():
        # Inventory item
        if 0 < int(slot) <= 3:
            return SlotType.ITEMS
    elif slot.lower() == 'p':
        # Potion bag?
        return SlotType.POTION_BAG
    return SlotType.INVALID


async def buy(cmd: Command, slot: str) -> None:
    result: ActionResult = cmd.guild.shop.buy(cmd.user, slot)
    if result.success:
        ts: list[str] = [tr(cmd.lang, 'SHOP.PURCHASE', EMOJI_PURCHASE=Emoji.PURCHASE, name=cmd.user.get_name(),
                            item=result.item)]
        if hasattr(result, 'must_equip'):
            ts.append(f"> {tr(cmd.lang, 'SHOP.AUTO_EQUIP')}")
        await cmd.send('\n'.join(ts))
    else:
        if hasattr(result, 'reload_shop'):
            ts = [tr(cmd.lang, 'SHOP.CHANGE'), cmd.guild.shop.print()]
            await cmd.send('\n'.join(ts))
        else:
            await cmd.error(result.tr(cmd.lang))
