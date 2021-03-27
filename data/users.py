from db.row import Row
from db import database
from data.helpers import IncrementalHelper
import utils

cache = {}

def get(user_id: int, create=True):
    if user_id in cache:
        return cache[user_id]
    else:
        if create or database.instance.get_row_data("users", user_id):
            user = User(user_id)
            cache[user_id] = user
            try_cleanup()
        else:
            return None
        return user

def try_cleanup():
    pass

class User(Row):
    def __init__(self, user_id: int):
        super().__init__("users", user_id)
        self.money = IncrementalHelper(self.data, 'money', 'money_time', 60)

    def load_defaults(self):
        return {
            'money': 10, # bigint
            'money_time': utils.now(), # bigint
            'money_limit': 1500, # bigint
            'bank': 0, # bigint
            'bank_time': utils.now(), # bigint
            'bank_limit': 0 # bigint
        }

    def get_pocket_limit(self):
        return self.data['money_limit']

    def get_money(self):
        return self.money.get()
        #return min(self.money.get(), self.get_pocket_limit())

    def change_money(self, amount: int):
        result = self.get_money() + amount
        if result < 0:
            return False
        self.money.set(result)
        self.register_changes('money', 'money_time')
        return True

    def print_inventory(self, checking=None, private=False):
        lines = []
        money_str = utils.print_money(self.get_money())
        if checking:
            lines.append(f"{checking}'s profile:")
        if private:
            #limit_str = utils.print_money(self.data['money_limit'])
            rate_str = utils.print_money(self.money.rate, decimals=2)
            #lines.append(f"**Money**: {money_str} / {limit_str} (+{rate_str}/minute)")
            lines.append(f"**Money**: {money_str} (+{rate_str}/minute)")
        else:
            lines.append(f"**Money**: {money_str}")
        return '\n'.join(lines)