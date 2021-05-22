import typing
from typing import Optional, Any

from discord import Member

import utils
from db.database import PostgreSQL
from helpers.dictref import DictRef
from helpers.incremental import Incremental
from db.row import Row
from entities.user_entity import UserEntity
from enums.emoji import Emoji
from helpers.translate import tr
from item_data import item_utils
from item_data.item_classes import Item
from item_data.stat import StatInstance
from user_data import upgrades
from user_data.inventory import Inventory
from enums.user_class import UserClass
from utils import TimeMetric, TimeSlot

if typing.TYPE_CHECKING:
    from adventure_classes.generic.adventure import Adventure


class User(Row):
    def __init__(self, db: PostgreSQL, user_id: int):
        super().__init__(db, 'users', dict(id=user_id))
        self.id = user_id
        self.member = None
        self._tutorial_stage: DictRef[int] = DictRef(self._data, 'tutorial')
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
        self._tokens = Incremental(DictRef(self._data, 'tokens'), DictRef(self._data, 'tokens_time'),
                                   TimeSlot(TimeMetric.DAY, 12))
        self._adventure: Optional[Adventure] = None
        self._lang: DictRef[str] = DictRef(self._data, 'lang')

        # User entity
        self.user_entity: UserEntity = UserEntity(DictRef(self._data, 'last_name'))
        self._user_class: DictRef[int] = DictRef(self._data, 'class')
        self._persistent_stats: dict[StatInstance, int] = {}
        if self._user_class.get() != -1:
            uc: UserClass = UserClass.get_from_id(self._user_class.get())
            self.user_entity.set_class(uc)
            self._persistent_stats: dict[StatInstance, int] = {
                stat: value for stat, value in uc.get_stats().items() if stat.is_persistent()
            }

        # Fill inventory
        slots = self.upgrades['inventory'].get_value()
        inv_items: list[Optional[Item]] = [None] * slots
        item_slots = self._db.start_join('users', dict(id=self.id), columns=['slot', 'item_id'],
                                         limit=self.upgrades['inventory'].get_value()) \
            .join('user_items', field_matches=[('user_id', 'id')]) \
            .execute()
        for is_info in item_slots:
            item_dict: dict[str, Any] = self._db.get_row_data('items', dict(id=is_info['item_id']))
            item: Item = item_utils.from_dict(item_dict['data'])
            item.id = item_dict['id']
            inv_items[is_info['slot']] = item
        if len(item_slots) > slots:
            # Too many item_data... log
            print(f"{user_id} exceeded {slots} items: {len(item_slots)}!")
        self.inventory: Inventory = Inventory(self._db, DictRef(self._data, 'equipment'), slots, inv_items,
                                              self.user_entity, self.id)

    def set_tokens(self, amount: int) -> None:
        self._tokens.set(amount)

    def get_lang(self) -> str:
        return self._lang.get()

    def set_lang(self, lang: str) -> None:
        self._lang.set(lang)

    def get_class_index(self) -> int:
        return self._user_class.get()

    def load_defaults(self):
        return {
            'bank_time': utils.now(),  # bigint
        }

    def update(self, name: str, member: Optional[Member] = None):
        if self._data['last_name'] != name:
            self._data['last_name'] = name
        if member:
            self.member = member

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

    def get_tokens(self) -> int:
        if self._tokens.get_base() > self.get_token_limit():
            # Overflow
            return self._tokens.get_base()
        return min(self._tokens.get(), self.get_token_limit())

    def remove_tokens(self, tokens: int) -> bool:
        if self.get_tokens() >= tokens:
            self._tokens.set(self.get_tokens() - tokens)
            return True
        return False

    def get_tutorial_stage(self) -> int:
        return self._tutorial_stage.get()

    def set_tutorial_stage(self, stage: int) -> None:
        self._tutorial_stage.set(stage)

    @staticmethod
    def get_token_limit() -> int:
        return 5

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

    def set_class(self, uc: UserClass):
        self._user_class.set(uc.get_id())
        self.user_entity.set_class(uc)

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
        return self._adventure

    def end_adventure(self):
        assert self.get_adventure() is not None, "User is not in an adventure!"
        self.user_entity.reset()
        self._adventure = None

    def get_inventory_limit(self) -> int:
        return self.upgrades['inventory'].get_value()

    def print_garden_rate(self) -> str:
        return self._bank.print_rate(self.get_lang())

    def get_total_money_space(self) -> int:
        return self.get_money_space() + self.get_bank_space()

    def get_average_level(self) -> int:
        return round(sum([x.get_level() + 1 for x in self.upgrades.values()]) / len(self.upgrades.values()))

    def print(self, lang: str, private=True, checking=False) -> str:
        to_print = []
        if checking:
            to_print.append(tr(lang, 'USER.PROFILE', name=self.get_name()))
        if private:
            to_print.append(f"{Emoji.MONEY} Money: {utils.print_money(lang, self.get_money())} "
                            f"/ {utils.print_money(lang, self.get_money_limit())}")
            to_print.append(f"{Emoji.BANK} Bank: {utils.print_money(lang, self.get_bank())} "
                            f"/ {utils.print_money(lang, self.get_bank_limit())} "
                            f"({self.print_garden_rate()} {Emoji.GARDEN})")
            if self.get_tokens() >= self.get_token_limit():
                to_print.append(f"{Emoji.TOKEN} Tokens: {self.get_tokens()} / {self.get_token_limit()}")
            else:
                to_print.append(f"{Emoji.TOKEN} Tokens: {self.get_tokens()} / {self.get_token_limit()} "
                                f"(Next in "
                                f"{utils.print_time(self.get_lang(), self._tokens.get_until(self.get_tokens() + 1))})")
            if checking:
                to_print.append(f"{Emoji.STATS} Equipment Power: {self.user_entity.get_power()}")
            to_print.append(self.inventory.print())
        else:
            to_print.append(f"{Emoji.MONEY} Money: {utils.print_money(lang, self.get_money())}")
            to_print.append(f"{Emoji.SCROLL} Average Level: {self.get_average_level()}")
            to_print.append(f"{Emoji.STATS} Equipment Power: {self.user_entity.get_power()}")
        return '\n'.join(to_print)

    def _update_bank_increment(self) -> None:
        self._bank.set_increment(self.upgrades['garden'].get_value())

    def _update_bank_limit(self) -> None:
        self._bank.set(self.get_bank())

    def _update_inventory_limit(self) -> None:
        self.inventory.set_limit(self.get_inventory_limit())

    def save(self) -> None:
        super().save()
        self.upgrades_row.save()
