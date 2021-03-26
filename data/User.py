from utils import utils

class User:
    def __init__(self, user_id, data):
        self.id = user_id
        if data:
            self.data = data
        else:
            self.data = {
                'money': 10,
                'money_time': utils.now()
            }

    def get_money(self):
        return self.data['money'] + (utils.now() - self.data['money_time']) // 60

    def add_money(self, amount):
        new_money = self.get_money() + amount
        if new_money >= 0:
            self.data['money'] = new_money
            self.data['money_time'] = utils.now()
            return True
        else:
            return False