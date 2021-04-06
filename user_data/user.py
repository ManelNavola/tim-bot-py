import utils
from inventory_data.entity import UserEntity
from inventory_data.stats import Stats
from user_data import upgrades
from common.incremental import Incremental
from inventory_data.inventory import Inventory
from db import database
from db.row import Row
from inventory_data import items
from inventory_data.items import Item
from utils import DictRef, TimeMetric, TimeSlot


class User(Row):
    def __init__(self, user_id: int):
        super().__init__("users", dict(id=user_id))
        self.id = user_id
        self.upgrades = {
            'bank': upgrades.UpgradeLink(upgrades.BANK_LIMIT,
                                         DictRef(self._data, 'bank_lvl'), before=self._update_bank_limit),
            'money_limit': upgrades.UpgradeLink(upgrades.MONEY_LIMIT,
                                                DictRef(self._data, 'money_limit_lvl')),
            'garden': upgrades.UpgradeLink(upgrades.GARDEN_PROD,
                                           DictRef(self._data, 'garden_lvl'), after=self._update_bank_increment),
            'inventory': upgrades.UpgradeLink(upgrades.INVENTORY_LIMIT,
                                              DictRef(self._data, 'inventory_lvl'), after=self._update_inventory_limit)
        }
        self._bank = Incremental(DictRef(self._data, 'bank'), DictRef(self._data, 'bank_time'),
                                 TimeSlot(TimeMetric.HOUR, self.upgrades['garden'].get_value()))

        # Fill inventory
        slots = self.upgrades['inventory'].get_value()
        database.INSTANCE.execute(f"SELECT I.* FROM users U "
                                  f"INNER JOIN user_items UI ON UI.user_id = U.id "
                                  f"INNER JOIN items I ON I.id = UI.item_id "
                                  f"WHERE U.id = {self.id} "
                                  f"LIMIT {self.upgrades['inventory'].get_value()}")
        fetched_items = database.INSTANCE.get_cursor().fetchall()
        if len(fetched_items) > slots:
            # Too many item_data... log
            print(f"{user_id} exceeded {slots} items: {len(fetched_items)}!")
        self.user_entity: UserEntity = UserEntity(DictRef(self._data, 'last_name'),
                                                  DictRef(self._data['persistent_stats'], Stats.HP.abv),
                                                  DictRef(self._data['persistent_stats'], Stats.MP.abv))
        self.inventory: Inventory = Inventory(DictRef(self._data, 'equipped'), slots, [
            Item(item_data=items.parse_item_data_from_dict(item['data']), item_id=item['id']) for item in fetched_items
        ], self.user_entity)

    def load_defaults(self):
        return {
            'money': 10,  # bigint
            'last_name': 'Unknown',  # text

            'bank': 0,  # bigint
            'bank_time': utils.now(),  # bigint

            'bank_lvl': 1,  # smallint
            'money_limit_lvl': 1,  # smallint
            'garden_lvl': 1,  # smallint
            'inventory_lvl': 1,  # smallint

            'equipped': [],  # smallint[]
            'persistent_stats': {  # json
                Stats.HP.abv: Stats.HP.base,
                Stats.MP.abv: Stats.MP.base
            }
        }

    def update_name(self, name: str):
        if self._data['last_name'] != name:
            self._data['last_name'] = name

    def get_name(self) -> str:
        return self._data['last_name']

    def get_money(self) -> int:
        return self._data['money']

    def get_money_limit(self) -> int:
        return self.upgrades['money_limit'].get_value()

    def get_money_space(self) -> int:
        return max(0, self.get_money_limit() - self.get_money())

    def set_money(self, amount: int) -> None:
        self._data['money'] = amount

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
            self._bank.set(bank + amount)
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
        self._bank.set(bank - need)
        self.add_money(need)
        return need

    def get_inventory_limit(self) -> int:
        return self.upgrades['inventory'].get_value()

    def print_garden_rate(self) -> str:
        return self._bank.print_rate()

    def get_total_money_space(self) -> int:
        return self.get_money_space() + self.get_bank_space()

    def get_average_level(self) -> int:
        return round(sum([x.get_level() + 1 for x in self.upgrades.values()]) / len(self.upgrades.values()))

    def print(self, private=True, checking=False) -> str:
        to_print = []
        if checking:
            to_print.append(f"{self.get_name()} User Profile:")
        if private:
            to_print.append(f"{utils.Emoji.MONEY} Money: {utils.print_money(self.get_money())} "
                            f"/ {utils.print_money(self.get_money_limit())}")
            to_print.append(f"{utils.Emoji.BANK} Bank: {utils.print_money(self.get_bank())} "
                            f"/ {utils.print_money(self.get_bank_limit())} "
                            f"({self.print_garden_rate()} {utils.Emoji.GARDEN})")
            if checking:
                to_print.append(f"{utils.Emoji.STATS} Equipment Power: {self.user_entity.get_power()}")
            to_print.append(self.inventory.print())
        else:
            to_print.append(f"{utils.Emoji.MONEY} Money: {utils.print_money(self.get_money())}")
            to_print.append(f"{utils.Emoji.SCROLL} Average Level: {self.get_average_level()}")
            to_print.append(f"{utils.Emoji.STATS} Equipment Power: {self.user_entity.get_power()}")
        return '\n'.join(to_print)

    def _update_bank_increment(self) -> None:
        self._bank.set_increment(self.upgrades['garden'].get_value())

    def _update_bank_limit(self) -> None:
        self._bank.set(self.get_bank())

    def _update_inventory_limit(self) -> None:
        self.inventory.set_limit(self.get_inventory_limit())
