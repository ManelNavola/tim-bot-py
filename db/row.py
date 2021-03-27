from db import database

class Row:
    def __init__(self, table_name: str, row_id: str):
        self.table = table_name
        self.id = row_id
        self.data = database.instance.get_row_data(table_name, row_id)
        self.changes = set()
        if not self.data:
            self.data = self.load_defaults()
            database.instance.insert_data(table_name, row_id, self.data)

    def load_defaults(self):
        return {}

    def register_changes(self, *change_args):
        for change in change_args:
            self.changes.add(change)

    def save(self):
        if len(self.changes) > 0:
            database.instance.update_data(self.table, self.id, {k:self.data[k] for k in self.changes})
            self.changes.clear()