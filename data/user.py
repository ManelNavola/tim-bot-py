from utils import utils

class User:
    def __init__(self, user_id, data):
        print('create')
        self.id = user_id
        if row:
            print('there is row')
            self.data = data
        else:
            print('there is no row')
            self.data = {
                'money': 10,
                'money_time': utils.now()
            }
            print('aight done')

    def get_money():
        return self.data['money'] + (self.data['money_time'] - utils.now()) // 60