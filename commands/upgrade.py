import utils
from commands.command import Command
from data.upgrades import Upgrade


def format_row(info) -> str:
    info = list(map(str, info))
    info = info + ["", "", "", "", ""]
    return f"{info[0]:<22s}|{info[1]:^7}|{info[2]:^16}|{info[3]:^14}|{info[4]:^16}"


def custom_print(upg: Upgrade, f) -> str:
    s = f(upg.get_value())
    if upg.is_max_level():
        return format_row([upg.name, 'MAX', s])
    else:
        s3 = upg.get_next_value()
        s3 = f(s3)
        return format_row([upg.name, upg.get_level() + 1, s, f"-{utils.print_money(upg.get_cost())}", s3])


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
    cost = cmd.user.upgrades[key].get_cost()
    if cost:
        if cmd.user.remove_money(cost):
            cmd.user.upgrades[key].level_up()
            await cmd.send_hidden(f"{utils.emoji(cmd.user.upgrades[key].icon)} Upgraded {key} "
                                  f"to Level {cmd.user.upgrades[key].get_level() + 1}!"
                                  f"{utils.emoji(cmd.user.upgrades[key].icon)}")
        else:
            await cmd.error(f"You need {utils.print_money(cost)} for the upgrade!")
    else:
        await cmd.error("You are already at max level!")
