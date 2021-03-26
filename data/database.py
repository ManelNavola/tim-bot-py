import os
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require', cursor_factory=RealDictCursor)
cur = conn.cursor()

pending_commit = False

def cursor():
    return cur

def convert_value(v):
    if type(v) == str:
        return "'" + v + "'"
    return str(v)

def get_row_data(table_name, row_id):
    print(f"""SELECT * from {table_name} WHERE id = '{row_id}'""")
    cur.execute(f"""SELECT * from {table_name} WHERE id = '{row_id}'""")
    return cur.fetchone()

def insert_data(table_name, row_id, data):
    global pending_commit
    keys = ['id']
    values = [row_id]
    for k, v in data.items():
        keys.append(k)
        values.append(convert_value(v))
    keys = '(' + ','.join(keys) + ')'
    values = '(' + ','.join(values) + ')'
    cur.execute(f"""INSERT INTO {table_name} {keys} VALUES {values}""")
    pending_commit = True

def update_data(table_name, row_id, data):
    global pending_commit
    ts = []
    for k, v in data.items():
        ts.append(k + ' = ' + convert_value(v))
    ts = ', '.join(ts)
    cur.execute(f"""UPDATE {table_name} SET {ts} WHERE id = {row_id}""")
    pending_commit = True

def commit(force = False):
    global pending_commit
    if force or pending_commit:
        conn.commit()