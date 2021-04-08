import calendar
import os
import time
from enum import unique, Enum
from typing import Generic, TypeVar

from autoslot import Slots

T = TypeVar("T")


class DictRef(Generic[T], Slots):
    def __init__(self, dictionary: dict, key: str):
        self.dictionary = dictionary
        self.key = key

    def get(self) -> T:
        return self.dictionary[self.key]

    def get_update(self):
        self._update()
        return self.dictionary[self.key]

    def __getitem__(self, key):
        return self.dictionary[self.key][key]

    def set(self, value: T):
        self.dictionary[self.key] = value

    def __setitem__(self, key, value):
        self.dictionary[self.key][key] = value
        self._update()

    def _update(self):
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

    def metric_abbreviation(self):
        return self.metric.abbreviation()

    def seconds(self):
        return self.metric.seconds(self.amount)


class Emoji:
    # User profile
    MONEY = r'\💵'
    BANK = r'\💰'
    GARDEN = r'\🌲'
    SCROLL = r'\📜'

    # Betting
    ROBOT = r'\🤖'
    COWBOY = r'\🤠'
    SUNGLASSES = r'\😎'
    SPARKLE = r'\✨'
    MONEY_FLY = r'\💸'
    INCREASE = r'\🔺'
    DECREASE = r'\🔻'

    # Commands
    ERROR = r'\⛔'

    # Crate
    BOX = r'\📦'
    CLOCK = r'\🕓'

    # Inventory
    EQUIPPED = r'\✔️'
    SHOP = r'\🛒'
    PURCHASE = r'\🛍️'
    STATS = r'\🧮'
    BAG = r'\🎒'
    WEAPON = r'\🗡️'
    SHIELD = r'\🛡️'
    HELMET = r'\⛑️'
    CHEST_PLATE = r'\👕'
    LEGGINGS = r'\👖'
    BOOTS = r'\👢'
    ARROW_RIGHT = r'➜'

    # Leaderboard
    TROPHY = r'\🏆'
    FIRST_PLACE = r'\🥇'
    SECOND_PLACE = r'\🥈'
    THIRD_PLACE = r'\🥉'

    # Stats
    HP = r'\💉'
    MP = r'\⚗️'
    STR = r'\💪'
    DEF = r'\🛡️'
    SPD = r'\🏃'
    EVA = r'\💨'
    CONT = r'\👊'
    CRIT = r'\🌟'
    STUN = r'\🛑'
    VAMP = r'\🧛'

    # Adventure
    COLISEUM = r'\🔱'
    BATTLE = r'\⚔️'


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
