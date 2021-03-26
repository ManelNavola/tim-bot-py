import calendar
import time

def now():
    return int(calendar.timegm(time.gmtime()))

def print_money(money: int):
    return f"${money:,}"