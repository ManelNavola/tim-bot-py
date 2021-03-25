from utils import utils

class User:
    def __init__(user_id, data):
        self.id = user_id
        if row:
            self.data = data
        else:
            self.data = {
                'money': 10,
                'money_time': utils.now()
            }

    def get_money():
        return self.data['money'] + (self.data['money_time'] - utils.now()) // 60