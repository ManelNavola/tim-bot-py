from utils import utils
from data import database

class Table:
    def __init__(self):
        self.data = database.get_row_data("global", "table")['json']

    def get_money(self):
        if self.data['money'] == 0:
            return 0
        return self.data['money'] + (utils.now() - self.data['money_time']) // 15

    def place_money(self, amount):
        if self.data['money'] == 0:
            self.data['money_time'] = utils.now()
        self.data['money'] += amount

    def retrieve_money(self):
        money = self.get_money()
        if money == 0:
            return money
        self.data['money'] = 0
        database.update_data("global", "table", {
            "money": 0
        })
        database.commit()
        return money