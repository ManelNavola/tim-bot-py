from db.row import Row
from data.items import Item

class Inventory:
    def __init__(self, inv_limit: int, items: list):
        self.set_limit(inv_limit)
        self.items = items

    def set_limit(self, inv_limit: int):
        self.limit = inv_limit

    def get_empty_slots(self):
        return len(self.items) - self.limit

    def add_item(self, item: Item):
        self.items.append(item)

    def set_items(self, items: list):
        self.items = items[:self.limit]

    def print(self):
        il = len(self.items)
        tr = [f"Inventory: {il}/{self.limit}"]
        for i in range(il):
            index = i + 1
            item_str = self.items[i].print()
            tr.append(f"{index}: {item_str}")
        return '\n'.join(tr)