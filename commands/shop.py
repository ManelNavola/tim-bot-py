import utils
from commands.command import Command
from guild_data.shop import Shop
from inventory_data.items import Item


async def check(cmd: Command):
    await cmd.send(cmd.guild.shop.print())


async def buy(cmd: Command, number: int):
    if number < 1 or number > 5:
        await cmd.error(f"Invalid item index!")
        return
    success, result = cmd.guild.shop.purchase_item(cmd.user, number)
    if success:
        await cmd.send(f"{utils.Emoji.PURCHASE} {cmd.user.get_name()} purchased {result}!")
    else:
        if result is None:
            await cmd.error(f"Your inventory is full!")
        elif result == -1:
            ts = [f"The shop has changed since the last time, showing shop...", cmd.guild.shop.print()]
            await cmd.send('\n'.join(ts))
        else:
            await cmd.error(f"You don't have {utils.print_money(result)}!")


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
