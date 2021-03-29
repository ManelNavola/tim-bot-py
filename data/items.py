class Item(Row):
    def __init__(self, item_id: int):
        super().__init__("items", dict(id=item_id))

    def print(self):
        return "Item"