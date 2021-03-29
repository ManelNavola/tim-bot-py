from db import database
from functools import wraps

def changes(*changes_args):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            self.register_changes(*changes_args)
            return result
        return wrapper
    return decorator

class Row:
    def __init__(self, table_name: str, match_columns: dict, data: dict=None):
        self.table = table_name
        self.id = match_columns
        self.changes = set()
        if not data:
            data = database.instance.get_row_data(table_name, match_columns)
            if not data:
                data = self.load_defaults().copy()
                to_insert = data.copy()
                to_insert.update(match_columns)
                database.instance.insert_data(table_name, to_insert)
        self.data = data

    def load_defaults(self):
        raise MemoryError('Tried loading missing defaults')

    def register_changes(self, *change_args):
        for change in change_args:
            self.changes.add(change)

    def save(self):
        if len(self.changes) > 0:
            database.instance.update_data(self.table, self.id, {k:self.data[k] for k in self.changes})
            self.changes.clear()