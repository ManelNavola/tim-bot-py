import utils
from commands.command import Command
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
        if ip.must_equip:
            ts.append("> Equipped automatically")
            cmd.user.inventory.equip(len(cmd.user.inventory.items) - 1)
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
        price = int(item.get_price() * Shop.SELL_MULTIPLIER)
        cmd.user.add_money(price)
        await cmd.send(f"{Emoji.PURCHASE} Sold {item.print()} for {utils.print_money(price)}")
    else:
        if result:
            await cmd.error("Invalid item index!")
        else:
            await cmd.error("You must unequip the item first!")


async def sell_all(cmd: Command):
    number: int = 0
    total_items: int = 0
    total_price: int = 0
    while number < len(cmd.user.inventory.items):
        success, result = cmd.user.inventory.sell(number, cmd.user.id)
        if success:
            item: Item = result
            price = int(item.get_price() * Shop.SELL_MULTIPLIER)
            total_price += price
            total_items += 1
        else:
            if result:
                number = 9999999
            else:
                number += 1
    if total_items == 0:
        await cmd.error("You don't have any items to sell!")
    else:
        cmd.user.add_money(total_price)
        await cmd.send_hidden(f"{Emoji.PURCHASE} Sold {total_items} items for {utils.print_money(total_price)}")
