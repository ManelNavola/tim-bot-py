import calendar
import time

def now():
    print('ima return now!')
    return int(calendar.timegm(time.gmtime()))