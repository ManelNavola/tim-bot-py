import utils
from data import upgrades
from data.incremental import Incremental, TimeMetric
from db.row import Row
from utils import DictRef


class User(Row):
    VERSION = 1

    def __init__(self, user_id: int):
        super().__init__("users", dict(id=user_id))
        self.id = user_id
        self.upgrades = {
            'bank': upgrades.Bank(DictRef(self.data, 'bank_lvl'), self._update_bank_limit),
            'money_limit': upgrades.MoneyLimit(DictRef(self.data, 'money_limit_lvl')),
            'garden': upgrades.Garden(DictRef(self.data, 'garden_lvl'), self._update_bank_increment)
        }
        self._bank = Incremental(DictRef(self.data, 'bank'), DictRef(self.data, 'bank_time'),
                                 TimeMetric.HOUR, self.upgrades['garden'].get_value())

        print("TODO: Fetch inventory")

    def load_defaults(self):
        return {
            'money': 10,  # bigint
            'last_name': 'Unknown',  # text

            'bank': 0,  # bigint
            'bank_time': utils.now(),  # bigint

            'bank_lvl': 0,  # smallint
            'money_limit_lvl': 0,  # smallint
            'garden_lvl': 0,  # smallint
            'inventory_lvl': 0,  # smallint

            'version': User.VERSION  # int
        }

    def update_name(self, name: str):
        self.data['last_name'] = name

    def get_name(self) -> str:
        return self.data['last_name']

    def get_money(self) -> int:
        return self.data['money']

    def get_money_limit(self) -> int:
        return self.upgrades['money_limit'].get_value()

    def get_money_space(self) -> int:
        return max(0, self.get_money_limit() - self.get_money())

    def set_money(self, amount: int) -> None:
        self.data['money'] = amount

    def add_money(self, amount: int) -> int:
        assert amount >= 0, "Cannot add negative money"
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
        assert amount >= 0, "Cannot remove negative money"
        money = self.get_money()
        new_money = money - amount
        if new_money >= 0:
            self.set_money(new_money)
            return True
        return False

    def get_bank_limit(self) -> int:
        return self.upgrades['bank'].get_value()

    def get_bank_space(self) -> int:
        return max(0, self.get_bank_limit() - self.get_bank())

    def get_bank(self) -> int:
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
            withdraw = self.get_bank()
            self._bank.set(0)
            self.add_money(withdraw)
            return withdraw
        self._bank.change(-need)
        self.add_money(need)
        return need

    def print_garden_rate(self) -> str:
        return self._bank.print_rate()

    def get_total_money_space(self) -> int:
        return self.get_money_space() + self.get_bank_space()

    def print(self, private=True, checking=False) -> str:
        to_print = []
        if checking:
            to_print.append(f"{self.get_name()} User Profile:")
        if private:
            to_print.append(f"{utils.emoji('money')} Money: {utils.print_money(self.get_money())} "
                            f"/ {utils.print_money(self.get_money_limit())}")
            to_print.append(f"{utils.emoji('bank')} Bank: {utils.print_money(self.get_bank())} "
                            f"/ {utils.print_money(self.get_bank_limit())} "
                            f"({self.print_garden_rate()} {utils.emoji('garden')})")
        else:
            upgrade_levels = int(sum([x.get_level() + 1 for x in self.upgrades.values()]) / len(self.upgrades.values()))
            to_print.append(f"{utils.emoji('money')} Money: {utils.print_money(self.get_money())}")
            to_print.append(f"{utils.emoji('scroll')} Avg level: {upgrade_levels}")
        return '\n'.join(to_print)

    def _update_bank_increment(self) -> None:
        self._bank.set_increment(self.upgrades['garden'].get_value())

    def _update_bank_limit(self) -> None:
        self._bank.set(self._bank.get())
