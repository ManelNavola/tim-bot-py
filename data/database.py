import os
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require', cursor_factory=RealDictCursor)
cur = conn.cursor()

def commit():
    conn.commit()

def cursor():
    return cur

def convert_value(v):
    if type(v) == str:
        return "'" + v + "'"
    return str(v)

def parse_set(d):
    ts = []
    for k, v in d.items():
        ts.append(k + ' = ' + convert_value(v))
    return ', '.join(ts)

def parse_insert(d, add_more = {}):
    keys = []
    values = []
    for k, v in d.items():
        keys.append(k)
        values.append(convert_value(v))
    for k, v in add_more.items():
        keys.append(k)
        values.append(convert_value(v))
    return '(' + ', '.join(keys) + ')', '(' + ','.join(values) + ')'