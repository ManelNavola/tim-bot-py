from commands.command import Command
import utils

def format_row(info):
    info = list(map(str, info))
    info = info + ["","","","",""]
    return f"{info[0]:<20s}|{info[1]:^7}|{info[2]:^16}|{info[3]:^14}|{info[4]:^16}"

def custom_print(upgrade, f):
    lvl = upgrade.level + 1
    s = f(upgrade.get_value())
    s2 = utils.print_money(upgrade.get_cost())
    if s2:
        s3 = upgrade.get_next_value()
        s3 = f(s3)
        return format_row([upgrade.name, lvl, s, f"-{s2}", s3])
    else:
        return format_row([upgrade.name, lvl, s])

def rate_hour(value):
    return f"(+{utils.print_money(value)}/hour)"

async def menu(cmd: Command):
    tp = ["```fix"]
    tp.append(format_row(['Upgrade Name', 'Level', 'Current', 'Upgrade Cost', 'Next Value']))
    tp.append(format_row(['--------------------', '-------', '----------------', '--------------', '----------------']))
    tp.append(custom_print(cmd.user._upgrades['money_limit'], utils.print_money))
    tp.append(custom_print(cmd.user._upgrades['bank'], utils.print_money))
    tp.append(custom_print(cmd.user._upgrades['garden'], rate_hour))
    #tp.append(custom_print(cmd.user.upgrades['inventory'], lambda x: x))
    tp.append('```')
    await cmd.send_hidden('\n'.join(tp))

async def upgrade(cmd: Command, key: str):
    cost = cmd.user._upgrades[key].get_cost()
    if cost:
        if cmd.user.change_money(-cost):
            cmd.user._upgrades[key].level += 1
            cmd.user.data[key + '_lvl'] += 1
            cmd.user.register_changes(key + '_lvl')
            await cmd.send_hidden(f"Upgraded {key} to Level {cmd.user._upgrades[key].level + 1}!")
            if key == 'garden':
                cmd.user.storage.set(cmd.user.storage.get())
                cmd.user.storage.set_increment(cmd.user.storage.every, cmd.user._upgrades[key].get_value())
        else:
            cost_str = utils.print_money(cost)
            await cmd.send_hidden(f"You need {cost_str} for the upgrade!")
    else:
        await cmd.send_hidden("You are already at max level!")