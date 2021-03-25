import os
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require', cursor_factory=RealDictCursor)
cur = psycopg2.cursor()

def cursor():
    cur

def parse_set(d):
    ts = []
    for k, v in d.items():
        ts.append(k + ' = ' + str(v))
    return ', '.join(ts)

def parse_insert(d, add_more = {}):
    keys = []
    values = []
    for k, v in d.items():
        keys.append(k)
        values.append(str(v))
    for k, v in add_more.items():
        keys.append(k)
        values.append(str(v))
    return '(' + ', '.join(keys) + ')', '(' + ','.join(values) + ')'