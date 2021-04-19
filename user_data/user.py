import typing
from typing import Optional

from discord_slash import SlashContext

import utils
from db.database import PostgreSQL
from helpers.dictref import DictRef
from helpers.incremental import Incremental
from db.row import Row
from entities.user_entity import UserEntity
from enums.emoji import Emoji
from item_data.item_classes import Item
from item_data.item_utils import parse_item_data_from_dict
from item_data.stat import StatInstance, Stat
from user_data import upgrades
from user_data.inventory import Inventory
from user_data.user_classes import UserClass
from utils import TimeMetric, TimeSlot

if typing.TYPE_CHECKING:
    from adventure_classes.generic.adventure import Adventure


class User(Row):
    def __init__(self, db: PostgreSQL, user_id: int):
        super().__init__(db, 'users', dict(id=user_id))
        self.id = user_id
        self.upgrades_row = Row(db, 'user_upgrades', dict(user_id=user_id))
        self.upgrades = {
            'bank': upgrades.UpgradeLink(upgrades.BANK_LIMIT,
                                         DictRef(self.upgrades_row._data, 'bank'),
                                         before=self._update_bank_limit),

            'money': upgrades.UpgradeLink(upgrades.MONEY_LIMIT,
                                          DictRef(self.upgrades_row._data, 'money')),

            'garden': upgrades.UpgradeLink(upgrades.GARDEN_PROD,
                                           DictRef(self.upgrades_row._data, 'garden'),
                                           after=self._update_bank_increment),

            'inventory': upgrades.UpgradeLink(upgrades.INVENTORY_LIMIT,
                                              DictRef(self.upgrades_row._data, 'inventory'),
                                              after=self._update_inventory_limit),
        }
        self._bank = Incremental(DictRef(self._data, 'bank'), DictRef(self._data, 'bank_time'),
                                 TimeSlot(TimeMetric.HOUR, self.upgrades['garden'].get_value()))
        self._adventure: Optional[Adventure] = None

        # User entity
        self._persistent_stats: dict[StatInstance, int] = {
            stat: value for stat, value in UserClass.WARRIOR.items() if stat in [Stat.HP, Stat.MP]
        }
        self.user_entity: UserEntity = UserEntity(DictRef(self._data, 'last_name'), UserClass.WARRIOR)

        # Fill inventory
        slots = self.upgrades['inventory'].get_value()
        inv_items: list[Optional[Item]] = [None] * slots
        item_slots = self._db.start_join('users', dict(id=self.id), columns=['slot', 'item_id'],
                                         limit=self.upgrades['inventory'].get_value()) \
            .join('user_items', field_matches=[('user_id', 'id')]) \
            .execute()
        for is_info in item_slots:
            item_data = self._db.get_row_data('items', dict(id=is_info['item_id']))
            inv_items[is_info['slot']] = Item(item_data=parse_item_data_from_dict(item_data['data']),
                                              item_id=item_data['id'])
        if len(item_slots) > slots:
            # Too many item_data... log
            print(f"{user_id} exceeded {slots} items: {len(item_slots)}!")
        self.inventory: Inventory = Inventory(self._db, DictRef(self._data, 'equipment'), slots, inv_items,
                                              self.user_entity)

    def load_defaults(self):
        return {
            'bank_time': utils.now(),  # bigint
        }

    def update(self, name: str):
        if self._data['last_name'] != name:
            self._data['last_name'] = name

    def get_name(self) -> str:
        return self._data['last_name']

    def get_money(self) -> int:
        return self._data['money']

    def get_money_limit(self) -> int:
        return self.upgrades['money'].get_value()

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

    @staticmethod
    def can_adventure():
        return True

    def start_adventure(self, adventure: 'Adventure'):
        assert self.get_adventure() is None, "User is already in an adventure!"
        self._adventure = adventure

    def get_adventure(self) -> Optional['Adventure']:
        if self._adventure is not None:
            if self._adventure.has_finished():
                self._adventure = None
                return None
            else:
                return self._adventure
        return self._adventure

    def end_adventure(self):
        assert self.get_adventure() is not None, "User is not in an adventure!"
        self.user_entity.reset()
        self._adventure = None

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
            to_print.append(f"{Emoji.MONEY} Money: {utils.print_money(self.get_money())} "
                            f"/ {utils.print_money(self.get_money_limit())}")
            to_print.append(f"{Emoji.BANK} Bank: {utils.print_money(self.get_bank())} "
                            f"/ {utils.print_money(self.get_bank_limit())} "
                            f"({self.print_garden_rate()} {Emoji.GARDEN})")
            if checking:
                to_print.append(f"{Emoji.STATS} Equipment Power: {self.user_entity.get_power()}")
            to_print.append(self.inventory.print())
        else:
            to_print.append(f"{Emoji.MONEY} Money: {utils.print_money(self.get_money())}")
            to_print.append(f"{Emoji.SCROLL} Average Level: {self.get_average_level()}")
            to_print.append(f"{Emoji.STATS} Equipment Power: {self.user_entity.get_power()}")
        return '\n'.join(to_print)

    def _update_bank_increment(self) -> None:
        self._bank.set_increment(self.upgrades['garden'].get_value())

    def _update_bank_limit(self) -> None:
        self._bank.set(self.get_bank())

    def _update_inventory_limit(self) -> None:
        self.inventory.set_limit(self.get_inventory_limit())
        if len(self.inventory.items) < self.get_inventory_limit():
            for i in range(self.get_inventory_limit() - len(self.inventory.items)):
                self.inventory.items.append(None)

    def save(self) -> None:
        super().save()
        self.upgrades_row.save()
