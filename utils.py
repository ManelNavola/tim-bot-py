import calendar
import os
import time

from enum import unique, Enum

from autoslot import Slots


# Time metric enum
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

    def abbreviation(self) -> str:
        if self == TimeMetric.SECOND:
            return 'sec'
        elif self == TimeMetric.MINUTE:
            return 'min'
        elif self == TimeMetric.HOUR:
            return 'hour'
        else:
            return 'day'

    def from_seconds(self, diff: int) -> int:
        return diff // self.seconds()


class TimeSlot(Slots):
    def __init__(self, metric: TimeMetric, amount: int):
        self.metric = metric
        self.amount = amount

    def metric_abbreviation(self):
        return self.metric.abbreviation()

    def seconds(self):
        return self.metric.seconds(self.amount)


NUMERAL_TO_ROMAN: dict[int, str] = {
    1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI'
}


def now() -> int:
    return int(calendar.timegm(time.gmtime()))


def current_ms() -> int:
    return round(time.time() * 1000)


def print_money(money: int, decimals: int = 0):
    return f"${money:,.{decimals}f}"


def is_test():
    return 'DATABASE_URL' not in os.environ


def print_time(seconds: int):
    minutes = seconds // 60
    seconds = seconds % 60
    if minutes > 0:
        return f"{minutes}m, {seconds}s"
    else:
        return f"{seconds}s"
