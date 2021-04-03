import utils
from commands.command import Command
from data.upgrades import UpgradeLink


def format_row(info) -> str:
    info = list(map(str, info))
    info = info + ["", "", "", "", ""]
    return f"{info[0]:<22s}|{info[1]:^7}|{info[2]:^16}|{info[3]:^14}|{info[4]:^16}"


def custom_print(upg: UpgradeLink, f) -> str:
    s = f(upg.get_value())
    if upg.is_max_level():
        return format_row([upg.get_name(), 'MAX', s])
    else:
        s3 = upg.get_value(upg.get_level() + 1)
        s3 = f(s3)
        return format_row([upg.get_name(), upg.get_level(), s, f"-{utils.print_money(upg.get_cost())}", s3])


def rate_hour(value):
    return f"(+{utils.print_money(value)}/hour)"


async def menu(cmd: Command):
    tp = ["```fix",
          format_row(['Upgrade Name', 'Level', 'Current', 'Upgrade Cost', 'Next Value']),
          format_row(['----------------------', '-------', '----------------', '--------------', '----------------']),
          custom_print(cmd.user.upgrades['money_limit'], utils.print_money),
          custom_print(cmd.user.upgrades['bank'], utils.print_money),
          custom_print(cmd.user.upgrades['garden'], rate_hour), '```']
    # tp.append(custom_print(cmd.user.upgrades['inventory'], lambda x: x))
    await cmd.send_hidden('\n'.join(tp))


async def upgrade(cmd: Command, key: str):
    upgrade_link = cmd.user.upgrades[key]
    if upgrade_link.is_max_level():
        await cmd.error("You are already at max level!")
    else:
        cost = upgrade_link.get_cost()
        if cmd.user.remove_money(cost):
            upgrade_link.level_up()
            await cmd.send_hidden(f"{upgrade_link.get_icon()} Upgraded {upgrade_link.get_name()} "
                                  f"to Level {upgrade_link.get_level()}!"
                                  f" {upgrade_link.get_icon()}")
        else:
            await cmd.error(f"You need {utils.print_money(cost)} for the upgrade!")
