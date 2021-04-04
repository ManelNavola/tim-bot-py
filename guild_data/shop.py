import math
import random
from typing import Optional

import utils
from user_data.user import User
from db import database
from inventory_data import items
from inventory_data.items import Item
from utils import DictRef, TimeSlot, TimeMetric


class Shop:
    SHOP_DURATION = TimeSlot(TimeMetric.HOUR, 1)
    SHOP_ITEMS = 4
    SELL_MULTIPLIER = 0.5

    def __init__(self, shop_time: DictRef, guild_id: int):
        self._guild_id: int = guild_id
        self._shop_time: DictRef = shop_time
        self._shop_items: list[Item] = []
        self.last_valid_check: Optional[int] = None

    def _check_shop(self):
        diff = utils.now() - self._shop_time.get()
        # If must restock
        if diff > Shop.SHOP_DURATION.seconds():
            # If no item_data in shop
            if len(self._shop_items) == 0:
                self._fetch_shop()  # Fetch before clearing
            self._clear_shop()
            self._restock_shop()
            self._shop_time.set(utils.now() - utils.now() % Shop.SHOP_DURATION.seconds())

        # If no item_data in shop
        if len(self._shop_items) == 0:
            # Check for saved item_data
            self._fetch_shop()
            self._restock_shop()  # Restock just in case

    def print(self) -> str:
        self._check_shop()
        diff = utils.now() - self._shop_time.get()
        self.last_valid_check = utils.now()
        to_ret = [f"{utils.Emoji.SHOP} Shop item_data (Restocks in "
                  f"{utils.print_time(Shop.SHOP_DURATION.seconds() - diff)}"
                  f"{utils.Emoji.CLOCK})"]
        for i in range(len(self._shop_items)):
            item = self._shop_items[i]
            if math.isclose(item.data.price_modifier, 1):
                to_ret.append(f"{i + 1}: {item.print()}"
                              f" - {utils.print_money(item.get_price())}")
            else:
                if item.data.price_modifier > 1:
                    to_ret.append(f"{i + 1}: {item.print()}"
                                  f" - {utils.print_money(item.get_price())} {utils.Emoji.INCREASE}")
                else:
                    to_ret.append(f"{i + 1}: {item.print()}"
                                  f" - {utils.print_money(item.get_price())} {utils.Emoji.DECREASE}")
        return '\n'.join(to_ret)

    def purchase_item(self, user: User, item_index: int) -> (bool, Optional[int]):
        self._check_shop()

        if not self.last_valid_check:
            return False, -1

        item = self._shop_items[item_index - 1]
        if user.inventory.get_empty_slots() > 0:
            if user.remove_money(item.get_price()):
                items.transfer(self._guild_id, user.id, item.id)
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
                                  f"LIMIT {Shop.SHOP_ITEMS}")
        found_items = database.INSTANCE.get_cursor().fetchall()
        self._shop_items = [
            Item(item_data=items.parse_item_data_from_dict(item['data']), item_id=item['id']) for item in found_items
        ]

    def _clear_shop(self):
        if len(self._shop_items) > 0:
            database.INSTANCE.delete_row("guild_items", dict(guild_id=self._guild_id), len(self._shop_items))
        for item in self._shop_items:
            database.INSTANCE.delete_row("items", dict(id=item.id))
        self._shop_items.clear()

    def _restock_shop(self) -> bool:
        restocked = 0
        for i in range(len(self._shop_items), Shop.SHOP_ITEMS):
            item: Item = items.create_guild_item(self._guild_id, items.get_random_item())
            if random.random() < 0.2:
                if random.random() < 0.5:
                    item.data.price_modifier = 0.75
                else:
                    item.data.price_modifier = 1.25
            self._shop_items.append(item)
            restocked += 1
        if restocked > 0:
            return True
        return False
