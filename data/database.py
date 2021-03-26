import os
import psycopg2
import json
from psycopg2.extras import RealDictCursor

conn = None
cur = None
mock_db = None
if os.environ.get('DATABASE_URL'):
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require', cursor_factory=RealDictCursor)
    cur = conn.cursor()
else:
    mock_db = {
        "users": {},
        "global": {}
    }

pending_commit = False

def cursor():
    return cur

def convert_value(v):
    if type(v) == str:
        return "'" + v + "'"
    if type(v) == dict:
        return "'" + json.dumps(v) + "'"
    return str(v)

def get_row_data(table_name, row_id):
    if cur:
        cur.execute(f"""SELECT * from {table_name} WHERE id = '{row_id}'""")
        return cur.fetchone()
    else:
        if row_id in mock_db[table_name]:
            return mock_db[table_name].get(row_id)
        else:
            return None

def insert_data(table_name, row_id, data):
    global pending_commit
    if cur:
        keys = ['id']
        values = [row_id]
        for k, v in data.items():
            keys.append(k)
            values.append(convert_value(v))
        keys = '(' + ','.join(keys) + ')'
        values = '(' + ','.join(values) + ')'
        cur.execute(f"""INSERT INTO {table_name} {keys} VALUES {values}""")
        pending_commit = True
    else:
        mock_db[table_name][row_id] = data

def update_data(table_name, row_id, data):
    global pending_commit
    if cur:
        ts = []
        for k, v in data.items():
            ts.append(k + ' = ' + convert_value(v))
        ts = ', '.join(ts)
        cur.execute(f"""UPDATE {table_name} SET {ts} WHERE id = '{row_id}'""")
        pending_commit = True
    else:
        row = mock_db[table_name][row_id]
        for k, v in data.items():
            row[k] = v

def commit(force = False):
    global pending_commit
    if cur and (force or pending_commit):
        conn.commit()