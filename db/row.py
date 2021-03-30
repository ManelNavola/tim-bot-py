from collections import UserDict

from autoslot import Slots

from db import database


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
    def __init__(self, table_name: str, pkey_dict: dict, insert_data: dict = None):
        self.table = table_name
        self.pkey_dict = pkey_dict
        if insert_data:
            self.data = DataChanges(insert_data.copy())
            insert_data.update(pkey_dict)
            database.INSTANCE.insert_data(table_name, insert_data)
        else:
            data = database.INSTANCE.get_row_data(table_name, pkey_dict)
            if not data:
                data = self.load_defaults().copy()
                to_insert = data.copy()
                to_insert.update(pkey_dict)
                database.INSTANCE.insert_data(table_name, to_insert)
            self.data = DataChanges(data)

    def __getitem__(self, key: str):
        return self.data[key]

    def load_defaults(self):
        raise MemoryError('Tried loading missing defaults')

    def save(self):
        change_list = self.data.pop_changes()
        if change_list:
            database.INSTANCE.update_data(self.table, self.pkey_dict,
                                          {k: self.data[k] for k in change_list})
