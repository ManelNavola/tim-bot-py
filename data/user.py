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
        return self.data['money'] + (self.data['money_time'] - utils.now()) // 60