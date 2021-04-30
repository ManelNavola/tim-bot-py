import random
import typing
from typing import Optional

import utils
from db.database import PostgreSQL
from enums.emoji import Emoji
from enums.location import Location
from enums.item_rarity import ItemRarity
from helpers.dictref import DictRef
from item_data import item_utils
from item_data.item_classes import Item
from item_data.item_utils import transfer_shop, create_guild_item, RandomItemBuilder
from utils import TimeSlot, TimeMetric
if typing.TYPE_CHECKING:
    from user_data.user import User


class ItemPurchase:
    def __init__(self):
        self.reload_shop: bool = False
        self.item: Optional[Item] = None
        self.price: Optional[int] = None
        self.must_equip: Optional[int] = None


class Shop:
    SHOP_DURATION: TimeSlot = TimeSlot(TimeMetric.HOUR, 1)
    ITEM_AMOUNT: int = 4
    SELL_MULTIPLIER: float = 0.4
    ITEM_BUILDER: RandomItemBuilder = RandomItemBuilder(0).set_location(Location.ANYWHERE).choose_rarity(
        [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC],
        [ItemRarity.UNCOMMON.get_chance(), ItemRarity.RARE.get_chance(),
         ItemRarity.EPIC.get_chance(), ItemRarity.LEGENDARY.get_chance()])

    def __init__(self, db: PostgreSQL, shop_time: DictRef[int], guild_id: int):
        self._db = db
        self._guild_id: int = guild_id
        self._shop_time: DictRef[int] = shop_time
        self._shop_items: list[Optional[Item]] = [None] * Shop.ITEM_AMOUNT
        self._last_valid_checks: list[Optional[bool]] = [False] * Shop.ITEM_AMOUNT

    @staticmethod
    def get_sell_price(item: Item):
        return int(item.get_price() * Shop.SELL_MULTIPLIER)

    def _check_shop(self):
        diff = utils.now() - self._shop_time.get()
        # If must restock
        shop_len: int = len([1 for x in self._shop_items if x is not None])
        if diff > Shop.SHOP_DURATION.seconds():
            # If no item_data in shop
            if shop_len < Shop.ITEM_AMOUNT:
                self._fetch_shop()  # Fetch before clearing
            self._clear_shop()
            self._restock_shop()
            self._shop_time.set(utils.now() - utils.now() % Shop.SHOP_DURATION.seconds())
            return

        # Check for saved item_data
        if shop_len == 0:
            self._fetch_shop()
        if shop_len < Shop.ITEM_AMOUNT:
            self._restock_shop()

    def print(self) -> str:
        self._check_shop()
        diff = utils.now() - self._shop_time.get()
        for i in range(Shop.ITEM_AMOUNT):
            self._last_valid_checks[i] = True
        to_ret = [f"{Emoji.SHOP} Shop (Restocks in "
                  f"{utils.print_time(Shop.SHOP_DURATION.seconds() - diff)}"
                  f"{Emoji.CLOCK})"]
        for i in range(len(self._shop_items)):
            item = self._shop_items[i]
            if item.price_modifier is None:
                to_ret.append(f"{i + 1}: {item.print()}"
                              f" - {utils.print_money(item.get_price())}")
            else:
                if item.price_modifier > 1:
                    to_ret.append(f"{i + 1}: {item.print()}"
                                  f" - {utils.print_money(item.get_price())} {Emoji.INCREASE}")
                else:
                    to_ret.append(f"{i + 1}: {item.print()}"
                                  f" - {utils.print_money(item.get_price())} {Emoji.DECREASE}")
        return '\n'.join(to_ret)

    def purchase_item(self, user: 'User', item_index: int) -> ItemPurchase:
        ip: ItemPurchase = ItemPurchase()
        self._check_shop()

        if not self._last_valid_checks[item_index]:
            ip.reload_shop = True
            return ip

        item = self._shop_items[item_index]
        slot = user.inventory.create_item(item)
        if slot is not None:
            if user.remove_money(item.get_price()):
                was_there_before = (user.inventory.get_first(item.get_description().type) is not None)
                transfer_shop(self._db, self._guild_id, user.id, slot, item)
                self._shop_items[item_index] = None
                item.durability = 100
                self._last_valid_checks[item_index] = False
                self._restock_shop()
                ip.item = item
                if not was_there_before:
                    ip.must_equip = slot
                return ip
            else:
                ip.price = item.get_price()
                return ip
        else:
            return ip

    def _fetch_shop(self):
        found_items = self._db.start_join('guilds', dict(id=self._guild_id), None, Shop.ITEM_AMOUNT)\
            .join('guild_items', [('guild_id', 'id')])\
            .join('items', [('id', 'item_id')])\
            .execute()
        for index in range(len(found_items)):
            self._shop_items[index] = item_utils.from_dict(found_items[index]['data'])

    def _clear_shop(self) -> None:
        shop_items: list[Optional[Item]] = self._shop_items  # PYCHARM WHAT
        shop_len: int = len([1 for x in shop_items if x is not None])
        if shop_len > 0:
            self._db.delete_row("guild_items", dict(guild_id=self._guild_id), shop_len)
        for item in shop_items:
            if item is not None:
                self._db.delete_row("items", dict(id=item.id))
        self._shop_items = [None] * Shop.ITEM_AMOUNT

    def _restock_shop(self) -> bool:
        restocked = False
        for i in range(0, Shop.ITEM_AMOUNT):
            if self._shop_items[i] is None:
                item: Item = Shop.ITEM_BUILDER.build()
                create_guild_item(self._db, self._guild_id, item)
                if random.random() < 0.2:
                    if random.random() < 0.5:
                        item.price_modifier = 0.8
                    else:
                        item.price_modifier = 1.2
                self._last_valid_checks[i] = False
                self._shop_items[i] = item
                restocked = True
        if restocked > 0:
            return True
        return False
