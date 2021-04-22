import utils
from helpers.command import Command
from enums.emoji import Emoji
from guild_data.shop import Shop, ItemPurchase
from item_data.item_classes import Item


async def check(cmd: Command):
    await cmd.send(cmd.guild.shop.print())


async def buy(cmd: Command, number: int):
    if number < 1 or number > Shop.ITEM_AMOUNT:
        await cmd.error("Invalid item index!")
        return
    ip: ItemPurchase = cmd.guild.shop.purchase_item(cmd.user, number - 1)
    if ip.item is not None:
        ts: list[str] = [f"{Emoji.PURCHASE} {cmd.user.get_name()} purchased {ip.item.print()}!"]
        if ip.must_equip is not None:
            ts.append("> Equipped automatically")
            cmd.user.inventory.equip(ip.must_equip)
        await cmd.send('\n'.join(ts))
    else:
        if ip.reload_shop:
            ts = ["The shop has changed since the last time, showing shop...", cmd.guild.shop.print()]
            await cmd.send('\n'.join(ts))
        elif ip.price is not None:
            await cmd.error(f"You don't have {utils.print_money(ip.price)}!")
        else:
            await cmd.error("Your inventory is full!")


async def sell(cmd: Command, number: int):
    success, result = cmd.user.inventory.sell(number - 1, cmd.user.id)
    if success:
        item: Item = result
        price = Shop.get_sell_price(item)
        cmd.user.add_money(price)
        await cmd.send_hidden(f"{Emoji.PURCHASE} Sold {item.print()} for {utils.print_money(price)}")
    else:
        if result:
            await cmd.error("Invalid item index!")
        else:
            await cmd.error("You must unequip the item first!")


async def sell_all(cmd: Command):
    total_items, total_price = cmd.user.inventory.sell_all(cmd.user.id)
    if total_items == 0:
        await cmd.error("You don't have any items to sell!")
    else:
        cmd.user.add_money(total_price)
        await cmd.send_hidden(f"{Emoji.PURCHASE} Sold {total_items} item{'s' if total_items > 0 else ''} "
                              f"for {utils.print_money(total_price)}")
