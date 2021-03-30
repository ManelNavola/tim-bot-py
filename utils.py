import calendar
import os
import time

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
        self.set(self.get())


EMOJI_DICT = {
    'money': '💵',
    'bank': '💰',
    'garden': '🌲',
    'scroll': '📜',
    'robot': '🤖',
    'forbidden': '⛔',
    'increase': '🔺',
    'poor': '💸',
    'sparkle': '✨',
    'cowboy': '🤠',
    'sunglasses': '😎'
}


def emoji(emoji_name: str, no_back: bool = False):
    if no_back:
        return f"{EMOJI_DICT[emoji_name]}"
    else:
        return f"\\{EMOJI_DICT[emoji_name]}"


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
