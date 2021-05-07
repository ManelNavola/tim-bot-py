import utils
from helpers.command import Command
from enums.emoji import Emoji
from guild_data.shop import Shop, ItemPurchase
from helpers.translate import tr
from item_data.item_classes import Item


async def check(cmd: Command):
    await cmd.send(cmd.guild.shop.print())


async def buy(cmd: Command, number: int):
    if number < 1 or number > Shop.ITEM_AMOUNT:
        await cmd.error(tr(cmd.lang, 'SHOP.INVALID'))
        return
    ip: ItemPurchase = cmd.guild.shop.purchase_item(cmd.user, number - 1)
    if ip.item is not None:
        ts: list[str] = [tr(cmd.lang, 'SHOP.PURCHASE', EMOJI_PURCHASE=Emoji.PURCHASE, name=cmd.user.get_name(),
                            item=ip.item.print())]
        if ip.must_equip is not None:
            ts.append(f"> {tr(cmd.lang, 'SHOP.AUTO_EQUIP')}")
            cmd.user.inventory.equip(ip.must_equip)
        await cmd.send('\n'.join(ts))
    else:
        if ip.reload_shop:
            ts = [tr(cmd.lang, 'SHOP.CHANGE'), cmd.guild.shop.print()]
            await cmd.send('\n'.join(ts))
        elif ip.price is not None:
            await cmd.error(tr(cmd.lang, 'SHOP.LACK', money=utils.print_money(ip.price)))
        else:
            await cmd.error(tr(cmd.lang, 'SHOP.INVENTORY_FULL'))


async def sell(cmd: Command, number: int):
    success, result = cmd.user.inventory.sell(number - 1, cmd.user.id)
    if success:
        item: Item = result
        price = Shop.get_sell_price(item)
        cmd.user.add_money(price)
        await cmd.send_hidden(tr(cmd.lang, 'SHOP.SOLD', EMOJI_PURCHASE=Emoji.PURCHASE, item=item.print(),
                                 money=utils.print_money(price)))
    else:
        if result:
            await cmd.error(tr(cmd.lang, 'SHOP.INVALID'))
        else:
            await cmd.error(tr(cmd.lang, 'SHOP.MUST_UNEQUIP'))


async def sell_all(cmd: Command):
    total_items, total_price = cmd.user.inventory.sell_all()
    if total_items == 0:
        await cmd.error(tr(cmd.lang, 'SHOP.NO_SELL'))
    else:
        cmd.user.add_money(total_price)
        await cmd.send_hidden(tr(cmd.lang, 'SHOP.SOLD_MANY', EMOJI_PURCHASE=Emoji.PURCHASE, total=total_items,
                                 money=total_price))
