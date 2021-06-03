import random
import typing
from typing import Any

import utils
from db.database import PostgreSQL
from enums.emoji import Emoji
from enums.location import Location
from enums.item_rarity import ItemRarity
from helpers.action_result import ActionResult
from helpers.dictref import DictRef
from item_data import item_utils, item_loader
from item_data.item_classes import Equipment, RandomEquipmentBuilder, Item, Potion
from item_data.item_utils import create_guild_item, transfer_guild_to_user, clone_item, create_user_item
from user_data.inventory import Inventory, SlotType
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
    POTION_AMOUNT: int = 1
    SELL_MULTIPLIER: float = 0.4
    ITEM_BUILDER: RandomEquipmentBuilder = RandomEquipmentBuilder(0).set_location(Location.ANYWHERE).choose_rarity(
        [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC],
        [50, 30, 8, 2])

    def __init__(self, db: PostgreSQL, lang: DictRef[str], shop_time: DictRef[int], guild_id: int):
        self._db = db
        self._lang = lang
        self._guild_id: int = guild_id
        self._shop_time: DictRef[int] = shop_time
        self._shop_items: dict[int, Item] = {}
        self._shop_potions: dict[int, Potion] = {}
        self._last_valid_checks: set[int] = set()

    def get_lang(self) -> str:
        return self._lang.get()

    @staticmethod
    def get_sell_price(item: Item):
        return int(item.get_price() * Shop.SELL_MULTIPLIER)

    def reload(self) -> None:
        self._clear_shop()

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
        for i in range(1, Shop.ITEM_AMOUNT + 1):
            self._last_valid_checks.add(i)
        to_ret = [f"{Emoji.SHOP} Shop (Restocks in "
                  f"{utils.print_time(self.get_lang(), Shop.SHOP_DURATION.seconds() - diff)}"
                  f"{Emoji.CLOCK})"]
        for i in range(1, len(self._shop_items) + 1):
            item = self._shop_items[i]
            if item.get_price_modifier() is None:
                to_ret.append(f"{i}: {item.print()}"
                              f" - {utils.print_money(self.get_lang(), item.get_price())}")
            else:
                if item.get_price_modifier() > 1:
                    to_ret.append(f"{i}: {item.print()}"
                                  f" - {utils.print_money(self.get_lang(), item.get_price())} {Emoji.INCREASE}")
                else:
                    to_ret.append(f"{i}: {item.print()}"
                                  f" - {utils.print_money(self.get_lang(), item.get_price())} {Emoji.DECREASE}")
        item = self._shop_potions[0]
        if item.get_price_modifier() is None:
            to_ret.append(f"p: {item.print()}"
                          f" - {utils.print_money(self.get_lang(), item.get_price())}")
        else:
            if item.get_price_modifier() > 1:
                to_ret.append(f"p: {item.print()}"
                              f" - {utils.print_money(self.get_lang(), item.get_price())} {Emoji.INCREASE}")
            else:
                to_ret.append(f"p: {item.print()}"
                              f" - {utils.print_money(self.get_lang(), item.get_price())} {Emoji.DECREASE}")
        return '\n'.join(to_ret)

    @staticmethod
    def _get_slot_type(slot: str) -> SlotType:
        if slot.isnumeric():
            # Items
            if 0 < int(slot) <= Shop.ITEM_AMOUNT:
                return SlotType.ITEMS
        elif slot.lower() == 'p':
            # Potion
            return SlotType.POTION_BAG
        return SlotType.INVALID

    def buy(self, user: 'User', slot: str) -> ActionResult:
        self._check_shop()

        slot_type: SlotType = Shop._get_slot_type(slot)
        if slot_type == SlotType.INVALID:
            return ActionResult(message='INVENTORY.INVALID_SLOT_TYPE')

        item_index: int = -1
        item: Item = self._get_dict_ref(slot).get()
        if slot_type == SlotType.ITEMS:
            item_index = int(slot)
            if item_index not in self._last_valid_checks:
                return ActionResult(reload_shop=True)

        auto_equip: bool = False
        if user.has_money(item.get_price()):
            user_slot: str = user.inventory.get_empty_slot(slot_type)
            if isinstance(item, Equipment) and (user.inventory.get_equipment().get(item.get_desc().subtype) is None):
                # Equip directly
                user_slot = Inventory.EQUIPMENT_TYPE_TO_CHAR[item.get_desc().subtype]
                auto_equip = True
            if user_slot is not None:
                user.remove_money(item.get_price())
                if slot_type == SlotType.ITEMS:
                    user.inventory.add_item(item, user_slot)
                    transfer_guild_to_user(self._db, self._guild_id, item, user.id, user_slot)
                    del self._shop_items[item_index]
                    self._last_valid_checks.remove(item_index)
                elif slot_type == SlotType.POTION_BAG:
                    new_item: Item = clone_item(self._db, item)
                    create_user_item(self._db, user.id, new_item, user_slot)
                    user.inventory.add_item(new_item, user_slot)
                self._restock_shop()
                if auto_equip:
                    user.inventory.update_equipment()
                    return ActionResult(message='SHOP.PURCHASE', success=True,
                                        EMOJI_PURCHASE=Emoji.PURCHASE, name=user.get_name(), item=item.print(),
                                        must_equip=True)
                else:
                    return ActionResult(message='SHOP.PURCHASE', success=True,
                                        EMOJI_PURCHASE=Emoji.PURCHASE, name=user.get_name(), item=item.print())
            return ActionResult(message='INVENTORY.FULL')
        else:
            return ActionResult(message='SHOP.LACK', money=utils.print_money(self.get_lang(), item.get_price()))

    def _get_dict_ref(self, slot: str) -> DictRef[Item]:
        if slot.isnumeric():
            # Inventory item
            return DictRef(self._shop_items, int(slot))
        elif slot.lower()[0] == 'p':
            # Potion bag
            return DictRef(self._shop_potions, 0)
        raise ValueError(f"Unknown shop slot >{slot}<")

    def _fetch_shop(self):
        items_data = self._db.start_join('guilds', dict(id=self._guild_id), columns=['slot', 'item_id'],
                                         limit=Shop.ITEM_AMOUNT + Shop.POTION_AMOUNT) \
            .join('guild_items', field_matches=[('guild_id', 'id')]) \
            .execute()
        for isd in items_data:
            slot: str = isd['slot'].strip()
            item_id: int = isd['item_id']
            item_dict: dict[str, Any] = self._db.get_row_data('items', dict(id=item_id))
            item: Item = item_utils.get_from_dict(item_id, item_dict['desc_id'], item_dict['data'])
            self._get_dict_ref(slot).set(item)

    def _clear_shop(self) -> None:
        shop_items: list[Optional[Item]] = self._shop_items
        shop_len: int = len([1 for x in shop_items if x is not None])
        if shop_len > 0:
            self._db.delete_row("guild_items", dict(guild_id=self._guild_id), shop_len)
        for item in shop_items.values():
            if item is not None:
                self._db.delete_row("items", dict(id=item.get_id()))
        self._shop_items.clear()

    def _restock_shop(self) -> bool:
        restocked = False
        for i in range(1, Shop.ITEM_AMOUNT + 1):
            if i not in self._shop_items:
                equipment: Equipment = Shop.ITEM_BUILDER.build()
                create_guild_item(self._db, self._guild_id, equipment, str(i))
                if random.random() < 0.2:
                    if random.random() < 0.5:
                        equipment.price_modifier = 0.8
                    else:
                        equipment.price_modifier = 1.2
                self._last_valid_checks.add(i)
                self._shop_items[i] = equipment
                restocked = True
        if 0 not in self._shop_potions:
            potion: Potion = Potion()
            potion.build(random.choice(item_loader.get_potion_list()).id)
            create_guild_item(self._db, self._guild_id, potion, f"p")
            self._shop_potions[0] = potion
            restocked = True
        if restocked > 0:
            return True
        return False
