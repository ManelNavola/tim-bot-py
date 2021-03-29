import os, calendar, time
from enum import Enum

class TimeMetric(Enum):
    SECOND = 1,
    MINUTE = 2,
    HOUR = 3,
    DAY = 4

def metric_to_seconds(metric: TimeMetric):
    if metric == TimeMetric.SECOND:
        return 1
    elif metric == TimeMetric.MINUTE:
        return 60
    elif metric == TimeMetric.HOUR:
        return 3600
    else:
        return 86400

def metric_to_abv(metric: TimeMetric):
    if metric == TimeMetric.SECOND:
        return 'sec'
    elif metric == TimeMetric.MINUTE:
        return 'min'
    elif metric == TimeMetric.HOUR:
        return 'hour'
    else:
        return 'day'

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