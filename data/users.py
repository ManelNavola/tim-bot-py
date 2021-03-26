from data import database
import utils

cache = {}

def get(user_id: str, create=True):
    if user_id in cache:
        return cache[user_id]
    else:
        data = database.get_row_data("users", user_id)
        if data:
            user = User(user_id, data)
        else:
            if not create:
                return None
            user = User(user_id)
            database.insert_data("users", user.id, user.data)
        try_cleanup()
        cache[user_id] = user
        return user

def try_cleanup():
    pass

class User:
    def __init__(self, user_id, data=None):
        self.id = user_id
        if data:
            self.data = data
            self.changes = set()
        else:
            self.data = {
                'money': 10,
                'money_time': utils.now()
            }
            self.changes = set(self.data.keys())

    def get_money(self):
        return self.data['money'] + (utils.now() - self.data['money_time']) // 60

    def add_money(self, amount):
        new_money = self.get_money() + amount
        if new_money >= 0:
            self.data['money'] = new_money
            self.data['money_time'] = utils.now()
            self.changes.add('money')
            self.changes.add('money_time')
            self.save(['money', 'money_time'])
            return True
        else:
            return False

    def save(self, fields=None):
        if fields:
            database.update_data("users", self.id, {k: self.data[k] for k in fields})
        else:
            database.update_data("users", self.id, self.data)