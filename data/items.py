from db.row import Row


class Item(Row):
    def __init__(self, item_id: int):
        super().__init__("items", dict(id=item_id))
