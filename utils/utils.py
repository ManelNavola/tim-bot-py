import calendar
import time

def now():
    return int(calendar.timegm(time.gmtime()))