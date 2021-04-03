from typing import Optional

import utils
from data.bet import Bet
from data.incremental import Incremental
from data.user import User
from db import database
from db.row import Row
from inventory_data import items
from inventory_data.items import Item
from utils import DictRef, TimeSlot, TimeMetric


class Guild(Row):
    TABLE_HYPE = TimeSlot(TimeMetric.MINUTE, 30)
    TABLE_INCREMENT = 2
    TABLE_MIN = 10
    LEADERBOARD_TOP = 5
    SHOP_DURATION = TimeSlot(TimeMetric.HOUR, 1)
    SHOP_ITEMS = 5

    def __init__(self, guild_id: int):
        super().__init__("guilds", dict(id=guild_id))
        self.id: int = guild_id
        self._box: Incremental = Incremental(DictRef(self._data, 'table_money'),
                                             DictRef(self._data, 'table_money_time'),
                                             TimeSlot(TimeMetric.MINUTE, Guild.TABLE_INCREMENT))
        self.bet: Bet = Bet(DictRef(self._data, 'ongoing_bet'))
        self.registered_user_ids: set[int] = set(self._data['user_ids'])
        self._shop_items: list[Item] = []
        self.last_valid_check: Optional[int] = None

    def load_defaults(self):
        return {
            'table_money': 0,  # bigint
            'table_money_time': utils.now(),  # bigint
            'ongoing_bet': {},  # json
            'user_ids': [],  # bigint[]
            'shop_time': 0,  # bigint
        }

    def register_user_id(self, user_id: int) -> None:
        if user_id not in self.registered_user_ids:
            self._data['user_ids'] = self._data['user_ids'] + [user_id]
            self.registered_user_ids.add(user_id)

    def print_leaderboard(self) -> str:
        database.INSTANCE.execute(f"SELECT last_name, money FROM users "
                                  f"INNER JOIN guilds ON guilds.id = {self.id} "
                                  f"AND users.id = ANY({database.convert_sql_value(list(self.registered_user_ids))}) "
                                  f"ORDER BY money DESC "
                                  f"LIMIT {Guild.LEADERBOARD_TOP}")
        users = database.INSTANCE.get_cursor().fetchall()
        ld = [f"{utils.Emoji.TROPHY} Top {Guild.LEADERBOARD_TOP} players:"]
        for i in range(len(users)):
            if i == 0:
                ld.append(f"{utils.Emoji.FIRST_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            elif i == 1:
                ld.append(f"{utils.Emoji.SECOND_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            elif i == 2:
                ld.append(f"{utils.Emoji.THIRD_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            else:
                ld.append(f"#{i + 1}: {users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
        return '\n'.join(ld)

    def _get_box_end(self) -> int:
        return self._data['table_money_time'] + Guild.TABLE_HYPE.seconds()

    def get_box(self) -> int:
        if self._data['table_money'] > 0:
            now = min(utils.now(), self._get_box_end())
            return self._box.get(now)
        else:
            return 0

    def place_box(self, user: User, amount: int) -> bool:
        if user.remove_money(amount):
            self._box.set_absolute(self.get_box() + amount)
            return True
        return False

    def retrieve_box(self, user: User) -> int:
        space = user.get_total_money_space()
        to_retrieve = min(self.get_box(), space)
        if to_retrieve == 0:
            return 0
        self._box.change(-to_retrieve)
        user.add_money(to_retrieve)
        return to_retrieve

    def print_box_rate(self) -> str:
        diff = self._get_box_end() - utils.now()
        if diff < 0:
            return ""
        else:
            return f"{self._box.print_rate()} for {utils.print_time(diff)}"

    def _check_shop(self):
        diff = utils.now() - self._data["shop_time"]
        # If must restock
        if diff > Guild.SHOP_DURATION.seconds():
            print("Wrong time: restock")
            # If no item_data in shop
            if len(self._shop_items) == 0:
                self._fetch_shop()  # Fetch before clearing
            self._clear_shop()
            self._restock_shop()
            self._data["shop_time"] = utils.now() - utils.now() % Guild.SHOP_DURATION.seconds()

        # If no item_data in shop
        if len(self._shop_items) == 0:
            # Check for saved item_data
            self._fetch_shop()
            self._restock_shop()  # Restock just in case

    def print_shop(self) -> str:
        self._check_shop()
        diff = utils.now() - self._data["shop_time"]
        self.last_valid_check = utils.now()
        to_ret = [f"{utils.Emoji.SHOP} Shop item_data (Restocks in "
                  f"{utils.print_time(Guild.SHOP_DURATION.seconds() - diff)}"
                  f"{utils.Emoji.CLOCK})"]
        for i in range(len(self._shop_items)):
            to_ret.append(f"{i + 1}: {self._shop_items[i].print()}"
                          f" - {utils.print_money(self._shop_items[i].get_price())}")
        return '\n'.join(to_ret)

    def purchase_item(self, user: User, item_index: int) -> (bool, Optional[int]):
        self._check_shop()

        if not self.last_valid_check:
            return False, -1

        item = self._shop_items[item_index - 1]
        if user.inventory.get_empty_slots() > 0:
            if user.remove_money(item.get_price()):
                items.transfer(self.id, user.id, item.id)
                user.inventory.add_item(item)
                self.last_valid_check = None
                self._restock_shop()
                return True, item.print()
            else:
                return False, item.get_price()
        else:
            return False, None

    def _fetch_shop(self):
        database.INSTANCE.execute(f"SELECT I.* FROM guilds G "
                                  f"INNER JOIN guild_items GI ON G.id = GI.guild_id "
                                  f"INNER JOIN items I ON I.id = GI.item_id "
                                  f"LIMIT {Guild.SHOP_ITEMS}")
        found_items = database.INSTANCE.get_cursor().fetchall()
        print(f"fetched {len(found_items)} items")
        self._shop_items = [
            Item(item_data=items.parse_item_data_from_dict(item['data']), item_id=item['id']) for item in found_items
        ]
        print("---")

    def _clear_shop(self):
        if len(self._shop_items) > 0:
            database.INSTANCE.delete_row("guild_items", dict(guild_id=self.id), len(self._shop_items))
        for item in self._shop_items:
            database.INSTANCE.delete_row("items", dict(id=item.id))
        print(f"cleared {len(self._shop_items)}")
        self._shop_items.clear()

    def _restock_shop(self) -> bool:
        restocked = 0
        for i in range(len(self._shop_items), Guild.SHOP_ITEMS):
            item = items.create_guild_item(self.id, items.get_random_item())
            self._shop_items.append(item)
            restocked += 1
        print(f"restocked {restocked}")
        if restocked > 0:
            return True
        return False
