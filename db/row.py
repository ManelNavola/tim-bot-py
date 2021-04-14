import copy
from collections import UserDict
from typing import Any

from autoslot import Slots

from db.database import PostgreSQL, SQLDict


class DataChanges(UserDict):
    def __init__(self, d=None):
        self._changes = set()
        super().__init__(d)

    def __setitem__(self, key: str, value: object):
        super().__setitem__(key, value)
        self._changes.add(key)

    def pop_changes(self):
        pop = list(self._changes)
        self._changes.clear()
        return pop


class Row(Slots):
    def __init__(self, db: PostgreSQL, table_name: str, pkey_dict: SQLDict, insert_data: SQLDict = None):
        self._db = db
        self._table_name = table_name
        self._pkey_dict = pkey_dict
        if insert_data:
            insert_data.update(pkey_dict)
            self._data = DataChanges(self._db.insert_data(table_name, insert_data, returns=True))
        else:
            data = self._db.get_row_data(table_name, pkey_dict)
            if not data:
                data = self._db.insert_data(table_name, pkey_dict.copy(), returns=True)
                data.update(copy.deepcopy(self.load_defaults()))
            self._data = DataChanges(data)

    def __getitem__(self, key: str):
        return self._data[key]

    def load_defaults(self) -> dict[str, Any]:
        return {}

    def save(self) -> None:
        change_list = self._data.pop_changes()
        if change_list:
            self._db.update_data(self._table_name, self._pkey_dict, {str(k): self._data[k] for k in change_list})
