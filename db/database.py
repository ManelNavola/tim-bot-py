import os
import psycopg2
import json
from psycopg2.extras import RealDictCursor

class Database():
    def get_row_data(self, table_name: str, row_id: int):
        pass

    def insert_data(self, table_name: str, row_id: int, data: dict):
        pass

    def update_data(self, table_name: str, row_id: int, data: dict):
        pass

    def commit(self):
        pass

instance: Database = None

class PostgreSQL(Database):
    def __init__(self, url: str):
        self.connection = psycopg2.connect(url, sslmode='require', cursor_factory=RealDictCursor)
        self.cursor = self.connection.cursor()
        self.pending_commit = False

    def convert_sql_value(self, value: object):
        t = type(value)
        if t == str:
            return "'" + value + "'"
        if t == dict:
            return "'" + json.dumps(value) + "'"
        return str(value)

    def get_row_data(self, table_name: str, row_id: int):
        self.cursor.execute(f"""SELECT * from {table_name} WHERE id = {row_id}""")
        return self.cursor.fetchone()

    def insert_data(self, table_name: str, row_id: int, data: dict):
        keys = ['id']
        values = [str(row_id)]
        for k, v in data.items():
            keys.append(k)
            values.append(self.convert_sql_value(v))
        keys = '(' + ','.join(keys) + ')'
        values = '(' + ','.join(values) + ')'
        self.cursor.execute(f"""INSERT INTO {table_name} {keys} VALUES {values}""")
        self.pending_commit = True

    def update_data(self, table_name: str, row_id: int, data: dict):
        ts = []
        for k, v in data.items():
            ts.append(k + ' = ' + self.convert_sql_value(v))
        ts = ', '.join(ts)
        self.cursor.execute(f"""UPDATE {table_name} SET {ts} WHERE id = {row_id}""")
        self.pending_commit = True

    def commit(self):
        if self.pending_commit:
            self.connection.commit()
            self.pending_commit = False

class JSONDatabase(Database):
    def __init__(self, file_name: str):
        # Horrible
        import win32api
        def on_exit(signal_type):
            with open(file_name, 'w') as f:
                json.dump(self.data, f)
        
        win32api.SetConsoleCtrlHandler(on_exit, True)
        import sys
        with open(file_name, 'r') as f:
            if len(f.readline()) == 0 or len(sys.argv) > 1:
                print('Cleared data')
                self.data = {
                    "users": {},
                    "guilds": {}
                }
            else:
                f.seek(0)
                self.data = json.load(f)
    
    def get_row_data(self, table_name: str, row_id: int):
        if str(row_id) in self.data[table_name]:
            return self.data[table_name].get(str(row_id))
        else:
            return None

    def insert_data(self, table_name: str, row_id: int, data: dict):
        self.data[table_name][str(row_id)] = data

    def update_data(self, table_name: str, row_id: int, data: dict):
        self.data[table_name][str(row_id)].update(data)