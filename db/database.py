import json
import os
from typing import Optional, Any

import psycopg2
from psycopg2.extras import RealDictCursor


class PostgreSQL:
    def __init__(self, *args, **kwargs):
        self._connection = psycopg2.connect(*args, **kwargs, cursor_factory=RealDictCursor)
        self._cursor = self._connection.cursor()
        self._pending_commit = False

    # noinspection PyDefaultArgument
    def get_row_data(self, table_name: str, match_columns: dict, columns: list = [], limit: int = 1) -> dict:
        if columns:
            column_names = ', '.join(columns)
        else:
            column_names = '*'
        where_info = get_where_info(match_columns)
        self._cursor.execute(f"SELECT {column_names} FROM {table_name} WHERE {where_info}")
        if limit == 1:
            return self._cursor.fetchone()
        else:
            return self._cursor.fetchmany(limit)

    def insert_data(self, table_name: str, column_data: dict, must_return: list = None) -> Optional[dict]:
        keys = '(' + ', '.join(column_data.keys()) + ')'
        values = '(' + ', '.join(map(convert_sql_value, column_data.values())) + ')'
        if must_return:
            must_return = '(' + ', '.join(must_return) + ')'
            self._cursor.execute(f"INSERT INTO {table_name} {keys} VALUES {values} RETURNING {must_return}")
            self._pending_commit = True
            return self._cursor.fetchone()
        else:
            self._cursor.execute(f"INSERT INTO {table_name} {keys} VALUES {values}")
            self._pending_commit = True

    def update_data(self, table_name: str, match_columns: dict, column_data: dict) -> None:
        where_info = get_where_info(match_columns)
        set_values = ', '.join(map(lambda x: x[0] + ' = ' + convert_sql_value(x[1]), column_data.items()))
        self._cursor.execute(f"UPDATE {table_name} SET {set_values} WHERE {where_info}")
        self._pending_commit = True

    def delete_row(self, table_name: str, match_columns: dict, limit: int = 1) -> None:
        where_info = get_where_info(match_columns)
        if limit is None:
            self._cursor.execute(f"DELETE FROM {table_name} WHERE {where_info}")
        else:
            column_match = ', '.join(match_columns.keys())
            self._cursor.execute(f"DELETE FROM {table_name} WHERE ({column_match}) IN "
                                 f"(SELECT {column_match} FROM {table_name} "
                                 f"WHERE {where_info} LIMIT {limit})")
        self._pending_commit = True

    def get_connection(self) -> Any:
        return self._connection

    def get_cursor(self) -> RealDictCursor:
        return self._cursor

    def execute(self, query: str) -> None:
        self._cursor.execute(query)

    def rollback(self) -> None:
        if self._pending_commit:
            self._connection.rollback()
            self._pending_commit = False

    def commit(self) -> None:
        if self._pending_commit:
            self._connection.commit()
            self._pending_commit = False


INSTANCE: PostgreSQL


def convert_sql_value(value):
    t = type(value)
    if t == str:
        return "'" + value + "'"
    if t == dict:
        return "'" + json.dumps(value) + "'"
    if t == list:
        return "'{" + ', '.join([str(x) for x in value]) + "}'"
    return str(value)


def get_where_info(match_columns: dict):
    return ' AND '.join(map(lambda x: x[0] + " = " + convert_sql_value(x[1]),
                            match_columns.items()))


def load_test_database():
    global INSTANCE
    with open('C:/Users/Manel/git/tim-bot-py/local/b.txt', 'r') as f:
        INSTANCE = PostgreSQL(host="localhost", user="postgres", password=f.readline(), database='testing')
        return INSTANCE


def load_database():
    global INSTANCE
    INSTANCE = PostgreSQL(os.environ['DATABASE_URL'], sslmode='require')
    return INSTANCE


def columns_match(row: dict, match_columns: dict):
    for k in match_columns.keys():
        if match_columns[k] != row[k]:
            return False
    return True


# class JSONDatabase(Database):
#     """
#         Deprecated. Use local server
#     """
#     def __init__(self, file_name: str):
#         # Horrible
#         self.file_name = file_name
#         import win32api
#
#         def on_exit(signal_type):
#             self.save()
#
#         win32api.SetConsoleCtrlHandler(on_exit, True)
#         with open(file_name, 'r') as f:
#             try:
#                 self.data = json.load(f)
#             except json.JSONDecodeError:
#                 self.data = JSON_DEFAULTS.copy()
#         pass
#
#     def reset(self):
#         self.data = JSON_DEFAULTS.copy()
#
#     def save(self):
#         with open(self.file_name, 'w') as f:
#             json.dump(self.data, f, indent=2)
#
#     # noinspection PyDefaultArgument
#     def get_row_data(self, table_name: str, match_columns: dict, columns: list = [], limit: int = 1):
#         rows = self.data[table_name]
#         found = []
#         for i in range(len(rows)):
#             row = rows[i]
#             if columns_match(row, match_columns):
#                 if columns:
#                     found.append({k: row[k] for k in columns})
#                 else:
#                     found.append(row)
#                 if len(found) == limit:
#                     break
#         if limit == 1:
#             if len(found) > 0:
#                 return found[0]
#             else:
#                 return None
#         else:
#             return found
#
#     def insert_data(self, table_name: str, column_data: dict):
#         self.data[table_name].append(column_data)
#
#     def update_data(self, table_name: str, match_columns: dict, column_data: dict):
#         rows = self.data[table_name]
#         for i in range(len(rows)):
#             row = rows[i]
#             if columns_match(row, match_columns):
#                 row.update(column_data)
#
#     def delete_row(self, table_name: str, match_columns: dict):
#         rows = self.data[table_name]
#         for i in range(len(rows) - 1, -1, -1):
#             if columns_match(rows[i], match_columns):
#                 del rows[i]
#                 return
#
#     def commit(self):
#         pass
