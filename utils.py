import os, calendar, time

def now():
    return int(calendar.timegm(time.gmtime()))

def print_money(money: int, decimals: int=0):
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