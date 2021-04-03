import utils
from commands.command import Command


async def check(cmd: Command):
    await cmd.send(cmd.guild.print_shop())


async def buy(cmd: Command, number: int):
    if number < 1 or number > 5:
        await cmd.error(f"Invalid item index!")
        return
    success, result = cmd.guild.purchase_item(cmd.user, number)
    if success:
        await cmd.send(f"{utils.Emoji.PURCHASE} {cmd.user.get_name()} purchased {result}!")
    else:
        if result is None:
            await cmd.error(f"Your inventory is full!")
        elif result == -1:
            ts = [f"The shop has changed since the last time, showing shop...", cmd.guild.print_shop()]
            await cmd.send('\n'.join(ts))
        else:
            await cmd.error(f"You don't have {utils.print_money(result)}!")
