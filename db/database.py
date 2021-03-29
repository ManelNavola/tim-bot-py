import psycopg2
import json
from psycopg2.extras import RealDictCursor
from abc import abstractmethod, ABC


class Database:
    @abstractmethod
    def get_row_data(self, table_name: str, match_columns: dict, columns: list = [], limit: int = 1):
        pass

    @abstractmethod
    def insert_data(self, table_name: str, column_data: dict):
        pass

    @abstractmethod
    def update_data(self, table_name: str, match_columns: dict, column_data: dict):
        pass

    @abstractmethod
    def delete_row(self, table_name: str, match_columns: dict):
        pass

    @abstractmethod
    def commit(self):
        pass


INSTANCE: Database = None


def convert_sql_value(value: object):
    t = type(value)
    if t == str:
        return "'" + value + "'"
    if t == dict:
        return "'" + json.dumps(value) + "'"
    return str(value)


def get_where_info(match_columns: dict):
    return ' AND '.join(map(lambda x: x[0] + " = " + convert_sql_value(x[1]),
                            match_columns.items()))


def load_test_database():
    global INSTANCE
    with open('../local/b.txt', 'r') as f:
        INSTANCE = PostgreSQL(host="localhost", user="postgres", password=f.readline(), database='testing')
        return INSTANCE


def load_database(url: str):
    global INSTANCE
    INSTANCE = PostgreSQL(url, sslmode='require')
    return INSTANCE


class PostgreSQL(Database):
    def __init__(self, *args, **kwargs):
        self.connection = psycopg2.connect(*args, **kwargs, cursor_factory=RealDictCursor)
        self.cursor = self.connection.cursor()
        self.pending_commit = False

    def get_row_data(self, table_name: str, match_columns: dict, columns: list = [], limit: int = 1):
        column_names = None
        if columns:
            column_names = ', '.join(columns)
        else:
            column_names = '*'
        where_info = get_where_info(match_columns)
        self.cursor.execute(f"SELECT {column_names} from {table_name} WHERE {where_info}")
        if limit == 1:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchmany(limit)

    def insert_data(self, table_name: str, column_data: dict):
        keys = '(' + ', '.join(list(column_data.keys())) + ')'
        values = '(' + ', '.join(map(convert_sql_value, column_data.values())) + ')'
        self.cursor.execute(f"INSERT INTO {table_name} {keys} VALUES {values}")
        self.pending_commit = True

    def update_data(self, table_name: str, match_columns: dict, column_data: dict):
        where_info = get_where_info(match_columns)
        set_values = ', '.join(map(lambda x: x[0] + ' = ' + convert_sql_value(x[1]), column_data.items()))
        self.cursor.execute(f"UPDATE {table_name} SET {set_values} WHERE {where_info}")
        self.pending_commit = True

    def delete_row(self, table_name: str, match_columns: dict):
        where_info = get_where_info(match_columns)
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {where_info}")
        self.pending_commit = True

    def commit(self):
        if self.pending_commit:
            self.connection.commit()
            self.pending_commit = False


JSON_DEFAULTS = {
    "users": [],
    "guilds": [],
    "items": [],
    "user_items": [],
    "guild_items": []
}


def columns_match(row: dict, match_columns: dict):
    for k in match_columns.keys():
        if match_columns[k] != row[k]:
            return False
    return True


class JSONDatabase(Database):
    """
        Deprecated. Use local server
    """
    def __init__(self, file_name: str):
        # Horrible
        self.file_name = file_name
        import win32api

        def on_exit(signal_type):
            self.save()

        win32api.SetConsoleCtrlHandler(on_exit, True)
        import sys
        with open(file_name, 'r') as f:
            try:
                self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = JSON_DEFAULTS.copy()

    def reset(self):
        self.data = JSON_DEFAULTS.copy()

    def save(self):
        with open(self.file_name, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_row_data(self, table_name: str, match_columns: dict, columns: list = [], limit: int = 1):
        rows = self.data[table_name]
        found = []
        for i in range(len(rows)):
            row = rows[i]
            if columns_match(row, match_columns):
                if columns:
                    found.append({k: row[k] for k in columns})
                else:
                    found.append(row)
                if len(found) == limit:
                    break
        if limit == 1:
            if len(found) > 0:
                return found[0]
            else:
                return None
        else:
            return found

    def insert_data(self, table_name: str, column_data: dict):
        self.data[table_name].append(column_data)

    def update_data(self, table_name: str, match_columns: dict, column_data: dict):
        rows = self.data[table_name]
        for i in range(len(rows)):
            row = rows[i]
            if columns_match(row, match_columns):
                row.update(column_data)

    def delete_row(self, table_name: str, match_columns: dict):
        rows = self.data[table_name]
        for i in range(len(rows) - 1, -1, -1):
            if columns_match(rows[i], match_columns):
                del rows[i]
                return

    def commit(self):
        pass
