import json
from data import database

class Table:
    def __init__(self):
        self.data = json.loads(database.get_row_data("global", "table"))

    def place_money(self, amount):
        self.data['money'] += amount

    def retrieve_money(self):
        money = self.data['money']
        self.data['money'] = 0
        database.update_data("global", "table", {
            "money": 0
        })
        database.commit()
        return money