import calendar
import os
import time

from enum import unique, Enum
from typing import Optional

from autoslot import Slots
from discord.ext.commands import Bot

BOT_CLIENT: Optional[Bot] = None


# Time metric enum
from helpers.translate import tr


@unique
class TimeMetric(Enum):
    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4

    def seconds(self, amount: int = 1) -> int:
        if self == TimeMetric.SECOND:
            return amount
        elif self == TimeMetric.MINUTE:
            return amount * 60
        elif self == TimeMetric.HOUR:
            return amount * 3600
        else:
            return amount * 86400

    def abbreviation(self, lang: str) -> str:
        if self == TimeMetric.SECOND:
            return tr(lang, 'MISC.TIME.SEC')
        elif self == TimeMetric.MINUTE:
            return tr(lang, 'MISC.TIME.MIN')
        elif self == TimeMetric.HOUR:
            return tr(lang, 'MISC.TIME.HOUR')
        else:
            return tr(lang, 'MISC.TIME.DAY')

    def from_seconds(self, diff: int) -> int:
        return diff // self.seconds()


class TimeSlot(Slots):
    def __init__(self, metric: TimeMetric, amount: int):
        self.metric = metric
        self.amount = amount

    def metric_abbreviation(self, lang: str):
        return self.metric.abbreviation(lang)

    def seconds(self):
        return self.metric.seconds(self.amount)


NUMERAL_TO_ROMAN: dict[int, str] = {
    1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI'
}


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


def now() -> int:
    return int(calendar.timegm(time.gmtime()))


def current_ms() -> int:
    return round(time.time() * 1000)


def print_float(lang: str, number: float, decimals: int) -> str:
    if number < 0:
        return '-' + print_float(lang, -number, decimals)
    result = ''
    thousand_sep = tr(lang, 'MISC.THOUSAND_SEP')
    while number >= 1000:
        number, r = divmod(number, 1000)
        result = "%s%03d%s" % (thousand_sep, r, result)
    rest: float = number % 1
    return "%d%s%s%s" % (number, result, tr(lang, 'MISC.DECIMAL_SEP'), f"{rest:.{decimals}f}"[2:])


def print_int(lang: str, number: int) -> str:
    if number < 0:
        return '-' + print_int(lang, -number)
    result = ''
    thousand_sep = tr(lang, 'MISC.THOUSAND_SEP')
    while number >= 1000:
        number, r = divmod(number, 1000)
        result = "%s%03d%s" % (thousand_sep, r, result)
    return "%d%s" % (number, result)


def print_money(lang: str, money: int):
    money_str: str = print_int(lang, money)
    return tr(lang, 'MISC.MONEY', number=money_str)


def is_test():
    return 'DATABASE_URL' not in os.environ


def print_time(lang: str, seconds: int):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{tr(lang, 'MISC.TIME.PRINT', number=hours, abv=tr(lang, 'MISC.TIME.HOUR_SHORT'))}, " \
               f"{tr(lang, 'MISC.TIME.PRINT', number=minutes, abv=tr(lang, 'MISC.TIME.MIN_SHORT'))}"
    elif minutes > 0:
        return f"{tr(lang, 'MISC.TIME.PRINT', number=minutes, abv=tr(lang, 'MISC.TIME.MIN_SHORT'))}, " \
               f"{tr(lang, 'MISC.TIME.PRINT', number=seconds, abv=tr(lang, 'MISC.TIME.SEC_SHORT'))}"
    else:
        return f"{tr(lang, 'MISC.TIME.PRINT', number=seconds, abv=tr(lang, 'MISC.TIME.SEC_SHORT'))}"
