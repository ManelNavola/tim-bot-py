from data.cache import Cache
from data.incremental import Incremental, TimeMetric
from db import database
from db.row import Row
import upgrades
from utils import DictRef

USER_VERSION = 1
USER_CACHE = Cache()


def get(user_id: int, create: bool = True):
    user = USER_CACHE.get(user_id)
    if not user:
        if create or database.INSTANCE.get_row_data("users", {
            'id': user_id
        }):
            user = User(user_id)
            USER_CACHE[user_id] = user
        else:
            return None
    return user


class User(Row):
    def __init__(self, user_id: int):
        super().__init__("users", dict(id=user_id))
        self.id = user_id
        self.upgrades = {
            'bank': upgrades.Bank(DictRef(self.data, 'bank_lvl'), self._update_bank_limit),
            'money_limit': upgrades.MoneyLimit(DictRef(self.data, 'money_limit_lvl')),
            'garden': upgrades.Garden(DictRef(self.data, 'garden_lvl'), self._update_bank_increment)
        }
        self._bank = Incremental(DictRef(self.data, 'bank'), DictRef(self.data, 'bank_time'),
                                 TimeMetric.HOUR, self.upgrades['bank'].get_value())

        print("TODO: Fetch inventory")

    def get_name(self):
        return self.data['last_name']

    def get_money(self):
        return self.data['money']

    def get_money_limit(self):
        return self.upgrades['money_limit'].get_value()

    def set_money(self, amount: int):
        self.data['money'] = amount

    def add_money(self, amount: int) -> int:
        money = self.get_money()
        money_limit = self.get_money_limit()
        excess = 0
        if money >= money_limit:
            excess = self.add_bank(amount)
        else:
            new_money = money + amount
            if new_money > money_limit:
                to_bank = new_money - money_limit
                new_money = money_limit
                excess = self.add_bank(to_bank)
            self.set_money(new_money)
        return excess

    def remove_money(self, amount: int) -> bool:
        money = self.get_money()
        new_money = money - amount
        if new_money >= 0:
            self.set_money(new_money)
            return True
        return False

    def get_bank_limit(self):
        return self.upgrades['bank'].get_value()

    def get_bank(self):
        return min(self._bank.get(), self.get_bank_limit())

    def add_bank(self, amount: int) -> int:
        bank = self._bank.get()
        bank_limit = self.get_bank_limit()
        new_bank = bank + amount
        if new_bank > bank_limit:
            excess = new_bank - bank_limit
            self._bank.set(bank_limit)
            return excess
        else:
            self._bank.change(amount)
            return 0

    def withdraw_bank(self) -> int:
        money = self.get_money()
        money_limit = self.get_money_limit()
        if money >= money_limit:
            return 0
        bank = self.get_bank()
        need = money_limit - money
        if need > bank:
            withdraw = self._bank.get()
            self._bank.set(0)
            self.add_money(withdraw)
            return withdraw
        self._bank.change(-need)
        self.add_money(need)
        return need

    def print(self, private=True, checking=False):
        print("TODO: Print")

    def _update_bank_increment(self):
        self._bank.set_increment(self.upgrades['bank'].get_value())

    def _update_bank_limit(self):
        self._bank.set(self._bank.get())
