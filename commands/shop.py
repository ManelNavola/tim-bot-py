import utils
from commands.command import Command
from guild_data.shop import Shop, ItemPurchase
from inventory_data.items import Item


async def check(cmd: Command):
    await cmd.send(cmd.guild.shop.print())


async def buy(cmd: Command, number: int):
    if number < 1 or number > Shop.SHOP_ITEMS:
        await cmd.error(f"Invalid item index!")
        return
    ip: ItemPurchase = cmd.guild.shop.purchase_item(cmd.user, number - 1)
    if ip.item is not None:
        ts: list[str] = [f"{utils.Emoji.PURCHASE} {cmd.user.get_name()} purchased {ip.item.print()}!"]
        if ip.must_equip:
            ts.append(f"> Equipped automatically")
            cmd.user.inventory.equip(len(cmd.user.inventory.items) - 1)
        await cmd.send('\n'.join(ts))
    else:
        if ip.reload_shop:
            ts = [f"The shop has changed since the last time, showing shop...", cmd.guild.shop.print()]
            await cmd.send('\n'.join(ts))
        elif ip.price is not None:
            await cmd.error(f"You don't have {utils.print_money(ip.price)}!")
        else:
            await cmd.error(f"Your inventory is full!")


async def sell(cmd: Command, number: int):
    success, result = cmd.user.inventory.sell(number - 1, cmd.user.id)
    if success:
        item: Item = result
        price = int(item.get_price() * Shop.SELL_MULTIPLIER)
        cmd.user.add_money(price)
        await cmd.send(f"{utils.Emoji.PURCHASE} Sold {item.print()} for {utils.print_money(price)}")
    else:
        if result:
            await cmd.error(f"Invalid item index!")
        else:
            await cmd.error(f"You must unequip the item first!")
