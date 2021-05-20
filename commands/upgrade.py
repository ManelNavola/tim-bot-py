import utils
from helpers.command import Command
from enums.emoji import Emoji
from helpers.translate import tr
from user_data.upgrades import UpgradeLink


def format_row(info) -> str:
    info = list(map(str, info))
    info = info + ["", "", "", "", ""]
    return f"{info[0]:<22s}|{info[1]:^7}|{info[2]:^16}|{info[3]:^14}|{info[4]:^16}"


def custom_print(lang: str, upg: UpgradeLink, f=lambda x: x, mobile: bool = False) -> str:
    s = f(upg.get_value())
    if upg.is_max_level():
        if mobile:
            return tr(lang, 'UPGRADE.SHORT_MAX', EMOJI_ICON=upg.get_icon(), name=upg.get_name(), level=upg.get_level(),
                      max_word=tr(lang, 'UPGRADE.MAX'))
        else:
            return format_row([upg.get_name(), tr(lang, 'UPGRADE.MAX'), s])
    else:
        s3 = upg.get_value(upg.get_level() + 1)
        s3 = f(s3)
        if mobile:
            return tr(lang, 'UPGRADE.SHORT', ICON_UPGRADE=upg.get_icon(), name=upg.get_name(), level=upg.get_level(),
                      value=s, EMOJI_ARROW_RIGHT=Emoji.ARROW_RIGHT, next_value=s3,
                      money=utils.print_money(lang, -upg.get_cost()))
        else:
            return format_row([upg.get_name(), upg.get_level(), s, f"{utils.print_money(lang, -upg.get_cost())}", s3])


def rate_hour_wrapper(lang: str):
    def rhw(value):
        t: str = tr(lang, 'MISC.RATE', amount=utils.print_money(lang, value),
                    time=utils.TimeMetric.HOUR.abbreviation(lang))
        return f"+{t}"
    return rhw


def print_money_wrapper(lang: str):
    def pmw(value):
        return utils.print_money(lang, value)
    return pmw


async def menu(cmd: Command):
    tp = ["```fix",
          format_row([tr(cmd.lang, 'UPGRADE.UPGRADE_NAME'), tr(cmd.lang, 'UPGRADE.LEVEL'),
                      tr(cmd.lang, 'UPGRADE.CURRENT'), tr(cmd.lang, 'UPGRADE.UPGRADE_COST'),
                      tr(cmd.lang, 'UPGRADE.NEXT_VALUE')]),
          format_row(['----------------------', '-------', '----------------',
                      '--------------', '----------------']),
          custom_print(cmd.lang, cmd.user.upgrades['money'], print_money_wrapper(cmd.lang)),
          custom_print(cmd.lang, cmd.user.upgrades['bank'], print_money_wrapper(cmd.lang)),
          custom_print(cmd.lang, cmd.user.upgrades['garden'], rate_hour_wrapper(cmd.lang)),
          custom_print(cmd.lang, cmd.user.upgrades['inventory']),
          '```']
    await cmd.send_hidden('\n'.join(tp))


async def short_menu(cmd: Command):
    tp = [tr(cmd.lang, 'UPGRADE.AVAILABLE'),
          custom_print(cmd.lang, cmd.user.upgrades['money'], print_money_wrapper(cmd.lang), mobile=True),
          custom_print(cmd.lang, cmd.user.upgrades['bank'], print_money_wrapper(cmd.lang), mobile=True),
          custom_print(cmd.lang, cmd.user.upgrades['garden'], rate_hour_wrapper(cmd.lang), mobile=True),
          custom_print(cmd.lang, cmd.user.upgrades['inventory'], mobile=True),
          ]
    await cmd.send_hidden('\n'.join(tp))


async def upgrade(cmd: Command, key: str):
    upgrade_link = cmd.user.upgrades[key]
    if upgrade_link.is_max_level():
        await cmd.error(tr(cmd.lang, 'UPGRADE.MAX_LEVEL'))
    else:
        cost = upgrade_link.get_cost()
        if cmd.user.remove_money(cost):
            upgrade_link.level_up()
            await cmd.send_hidden(tr(cmd.lang, 'UPGRADE.EXECUTE', EMOJI_ICON=upgrade_link.get_icon_str(),
                                     name=upgrade_link.get_name(), level=upgrade_link.get_level()))
        else:
            await cmd.error(tr(cmd.lang, 'UPGRADE.LACK', money=cost))
