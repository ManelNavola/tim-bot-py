import os
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require', cursor_factory=RealDictCursor)
cur = conn.cursor()

def cursor():
    return cur

def convert_value(v):
    if type(v) == str:
        return "'" + v + "'"
    return str(v)

def get_row_data(table_name, row_id):
    print("""SELECT * from {table_name} WHERE id = '{row_id}'""")
    cur.execute(f"""SELECT * from {table_name} WHERE id = '{row_id}'""")
    return cur.fetchone()

def update_data(table_name, row_id, data):
    ts = []
    for k, v in data.items():
        ts.append(k + ' = ' + convert_value(v))
    ts = ', '.join(ts)
    cur.execute(f"""UPDATE {table_name} SET {ts} WHERE id = {row_id}""")

def commit():
    conn.commit()

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