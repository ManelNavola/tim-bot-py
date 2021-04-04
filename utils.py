import calendar
import os
import time
from enum import unique, Enum

from autoslot import Slots


class DictRef(Slots):
    def __init__(self, dictionary: dict, key: object):
        self.dictionary = dictionary
        self.key = key

    def get(self):
        return self.dictionary[self.key]

    def __getitem__(self, key):
        return self.dictionary[self.key][key]

    def set(self, value: object):
        self.dictionary[self.key] = value

    def __setitem__(self, key, value):
        self.dictionary[self.key][key] = value
        self.update()

    def update(self):
        self.set(self.get())


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

    def metric_seconds(self):
        return self.metric.seconds()

    def metric_abbreviation(self):
        return self.metric.abbreviation()

    def seconds(self):
        return self.metric.seconds(self.amount)


# @unique
# class Emoji(Enum):
class Emoji:
    # User profile
    MONEY = '\💵'
    BANK = '\💰'
    GARDEN = '\🌲'
    SCROLL = '\📜'

    # Betting
    ROBOT = '\🤖'
    COWBOY = '\🤠'
    SUNGLASSES = '\😎'
    SPARKLE = '\✨'
    MONEY_FLY = '\💸'
    INCREASE = '\🔺'
    DECREASE = '\🔻'

    # Commands
    ERROR = '\⛔'

    # Crate
    BOX = '\📦'
    CLOCK = '\🕓'

    # Inventory
    EQUIPPED = '\✔️'
    SHOP = '\🛒'
    PURCHASE = '\🛍️'
    STATS = '\🧮'
    BAG = '\🎒'
    WEAPON = '\🗡️'
    SHIELD = '\🛡️'
    HELMET = '\⛑️'
    CHEST_PLATE = '\👕'
    LEGGINGS = '\👖'
    BOOTS = '\👢'

    # Leaderboard
    TROPHY = '\🏆'
    FIRST_PLACE = '\🥇'
    SECOND_PLACE = '\🥈'
    THIRD_PLACE = '\🥉'

    # Stats
    HP = '\💉'
    MP = '\⚗️'
    STR = '\💪'
    DEF = '\🛡️'
    SPD = '\🏃'
    EVA = '\💨'
    CONT = '\👊'
    CRIT = '\🌟'
    STUN = '\🛑'
    VAMP = '\🧛'


def now():
    return int(calendar.timegm(time.gmtime()))


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
