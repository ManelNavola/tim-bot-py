import json
import os
import string
from typing import Optional, Any, Union

import psycopg2
from psycopg2.extras import RealDictCursor

SQLColumns = Optional[list[str]]
SQLDict = dict[str, Any]
SQLResult = Union[SQLDict, list[SQLDict]]


def get_column_names(columns: SQLColumns, as_name: str = ''):
    if columns:
        if as_name:
            return ', '.join([f"{as_name}.{x}" for x in columns])
        else:
            return ', '.join(columns)
    else:
        return '*'


def convert_sql_value(value):
    t = type(value)
    if t == str:
        return "'" + value + "'"
    if t == dict:
        return "'" + json.dumps(value) + "'"
    if t == list:
        return "'{" + ', '.join([str(x) for x in value]) + "}'"
    return str(value)


def get_where_info(match_columns: dict, as_name: str = ''):
    if as_name:
        return ' AND '.join(map(lambda x: f"{as_name}.{x[0]}" + " = " + convert_sql_value(x[1]),
                                match_columns.items()))
    else:
        return ' AND '.join(map(lambda x: x[0] + " = " + convert_sql_value(x[1]),
                                match_columns.items()))


class PostgreSQL:
    def __init__(self, *args, **kwargs):
        self._connection = psycopg2.connect(*args, **kwargs, cursor_factory=RealDictCursor)
        self._cursor = self._connection.cursor()
        self._pending_commit = False

    def get_row_data(self, table_name: str, match_columns: SQLDict, columns: SQLColumns = None, limit: int = 1) \
            -> SQLResult:
        column_names = get_column_names(columns)
        where_info = get_where_info(match_columns)
        if limit == 1:
            self._cursor.execute(f"SELECT {column_names} FROM {table_name} WHERE {where_info}")
            return self._cursor.fetchone()
        else:
            self._cursor.execute(f"SELECT {column_names} FROM {table_name} WHERE {where_info} LIMIT {limit}")
            return self._cursor.fetchall()

    def start_join(self, table_from: str, match_columns: SQLDict, columns: SQLColumns = None, limit: int = 1) -> 'Join':
        return Join(self, table_from, match_columns, columns, limit)
        # column_names = get_column_names(columns)
        # self._cursor.execute(f"SELECT I.* FROM users U "
        #                           f"INNER JOIN user_items UI ON UI.user_id = U.id "
        #                           f"INNER JOIN items I ON I.id = UI.item_id "
        #                           f"WHERE U.id = {self.id} "
        #                           f"LIMIT {self.upgrades['inventory'].get_value()}")

    def insert_data(self, table_name: str, column_data: SQLDict, returns: bool = False,
                    return_columns: SQLColumns = None) -> Optional[SQLDict]:
        keys = '(' + ', '.join(column_data.keys()) + ')'
        values = '(' + ', '.join(map(convert_sql_value, column_data.values())) + ')'
        if returns:
            column_names = get_column_names(return_columns)
            self._cursor.execute(f"INSERT INTO {table_name} {keys} VALUES {values} RETURNING {column_names}")
            self._pending_commit = True
            return self._cursor.fetchone()
        else:
            self._cursor.execute(f"INSERT INTO {table_name} {keys} VALUES {values}")
            self._pending_commit = True

    def update_data(self, table_name: str, match_columns: SQLDict, column_data: SQLDict) -> None:
        where_info = get_where_info(match_columns)
        set_values = ', '.join(map(lambda x: x[0] + ' = ' + convert_sql_value(x[1]), column_data.items()))
        self._cursor.execute(f"UPDATE {table_name} SET {set_values} WHERE {where_info}")
        self._pending_commit = True

    def delete_row(self, table_name: str, match_columns: SQLDict, limit: int = 1) -> None:
        where_info = get_where_info(match_columns)
        if limit is None:
            self._cursor.execute(f"DELETE FROM {table_name} WHERE {where_info}")
        else:
            column_match = ', '.join(match_columns.keys())
            self._cursor.execute(f"DELETE FROM {table_name} WHERE ({column_match}) IN "
                                 f"(SELECT {column_match} FROM {table_name} "
                                 f"WHERE {where_info} LIMIT {limit})")
        self._pending_commit = True

    def get_cursor(self) -> RealDictCursor:
        return self._cursor

    def execute(self, query: str) -> None:
        self._cursor.execute(query)

    def rollback(self, force: bool = False) -> None:
        if self._pending_commit or force:
            self._connection.rollback()
            self._pending_commit = False

    def commit(self, force: bool = False) -> None:
        if self._pending_commit or force:
            self._connection.commit()
            self._pending_commit = False


class JoinOn:
    def __init__(self, table_name: str, field_matches: Optional[list[tuple[str, str]]],
                 value_matches: Optional[list[tuple[str, Any]]]):
        self.table_name: str = table_name
        self.field_matches: Optional[list[tuple[str, str]]] = field_matches
        self.value_matches: Optional[list[tuple[str, Any]]] = value_matches

    def print_matches(self, a: str, b: str) -> str:
        tp = []
        if self.field_matches:
            tp.append(' AND '.join([f"{a}.{x} = {b}.{y}" for (x, y) in self.field_matches]))
        if self.value_matches:
            tp.append(' AND '.join([f"{a}.{x} = {convert_sql_value(y)}" for (x, y) in self.value_matches]))
        return ' AND '.join(tp)


class Join:
    def __init__(self, db: PostgreSQL, table_from: str, match_columns: SQLDict, columns: SQLColumns = None,
                 limit: int = 1):
        self._db = db
        self._table_from: str = table_from
        self._match_columns: SQLDict = match_columns
        self._columns: SQLColumns = columns
        self._limit: int = limit
        self._join_on: list[JoinOn] = []

    def join(self, table_name: str, field_matches: Optional[list[tuple[str, str]]] = None,
             value_matches: Optional[list[tuple[str, Any]]] = None) -> 'Join':
        self._join_on.append(JoinOn(table_name, field_matches, value_matches))
        return self

    def execute(self) -> SQLResult:
        letters: str = string.ascii_uppercase
        to_execute: list[str] = []
        i = 0
        for join_on in self._join_on:
            i += 1
            to_execute.append(f"INNER JOIN {join_on.table_name} {letters[i]} "
                              f"ON {join_on.print_matches(letters[i], letters[i - 1])}")
        if self._match_columns:
            to_execute.append(f"WHERE {get_where_info(self._match_columns, letters[0])}")
        to_execute.insert(0, f"SELECT {get_column_names(self._columns, letters[i])} "
                             f"FROM {self._table_from} {letters[0]}")
        if self._limit == 1:
            self._db.execute(' '.join(to_execute))
            return self._db.get_cursor().fetchone()
        else:
            to_execute.append(f"LIMIT {self._limit}")
            self._db.execute(' '.join(to_execute))
            return self._db.get_cursor().fetchall()


def load_test_database():
    with open('C:/Users/Manel/git/tim-bot-py/local/b.txt', 'r') as f:  # TODO please
        return PostgreSQL(host="localhost", user="postgres", password=f.readline(), database='testing')


def load_database():
    return PostgreSQL(os.environ['DATABASE_URL'], sslmode='require')
