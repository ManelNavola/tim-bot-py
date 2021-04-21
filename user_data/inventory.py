from typing import Optional, Any

from db.database import PostgreSQL
from entities.user_entity import UserEntity
from enums.emoji import Emoji
from guild_data.shop import Shop
from helpers.dictref import DictRef
from enums.item_type import ItemType
from item_data.item_classes import Item
from item_data.item_utils import delete_user_item


class Inventory:
    def __init__(self, db: PostgreSQL, equipped_ref: DictRef[list[int]], inv_limit: int, item_list: list[Item],
                 user_entity: UserEntity):
        self._db = db
        self.items: list[Optional[Item]] = item_list
        self._equipped_ref: DictRef[list[int]] = equipped_ref
        self.limit: int = inv_limit
        self.user_entity: UserEntity = user_entity
        self.user_entity.update_equipment(self.get_equipment())

    def _get_item_indices(self):
        return [i for i, j in enumerate(self.items) if j is not None]

    def get_first(self, item_type: ItemType) -> Optional[Item]:
        for i in self._get_item_indices():
            item: Item = self.items[i]
            if item.get_description().type == item_type:
                return item
        return None

    def get_empty_slot(self) -> Optional[int]:
        for i in range(len(self.items)):
            if self.items[i] is None:
                return i
        return None

    def sell(self, index: int, user_id: int) -> tuple[bool, Any]:
        if index < 0 or index >= len(self.items):
            return False, True
        item = self.items[index]
        if item is None:
            return False, True
        if self._is_equipped(item):
            return False, False
        delete_user_item(self._db, user_id, item)
        self.items[index] = None
        return True, item

    def sell_all(self, user_id: int) -> tuple[int, int]:
        total_items: int = 0
        total_price: int = 0
        for i in self._get_item_indices():
            if self.items[i].id not in self._equipped_ref.get():
                success, result = self.sell(i, user_id)
                if success:
                    item: Item = result
                    price = int(item.get_price() * Shop.SELL_MULTIPLIER)
                    total_price += price
                    total_items += 1
                else:
                    if result:
                        break
        return total_items, total_price

    def _is_equipped(self, item: Item) -> bool:
        return item.id in self._equipped_ref.get()

    def _equip(self, item: Item, update: bool = True) -> None:
        self._equipped_ref.get_update().append(item.id)
        if update:
            self.user_entity.update_equipment(self.get_equipment())

    def _unequip(self, item: Item, update: bool = True) -> None:
        self._equipped_ref.get_update().remove(item.id)
        if update:
            self.user_entity.update_equipment(self.get_equipment())

    def equip(self, index: int) -> Optional[str]:
        if index in self._get_item_indices():
            item = self.items[index]
            if item.id not in self._equipped_ref.get():
                item_type = item.get_description().type
                for other_index in self._get_item_indices():
                    if other_index != index and self.items[other_index].id in self._equipped_ref.get() \
                            and self.items[other_index].get_description().type == item_type:
                        self._unequip(self.items[other_index], False)
                        break
                self._equip(item)
            return item.print()
        return None

    def equip_best(self) -> None:
        self.unequip_all()
        best: dict[ItemType, tuple[Item, int]] = {}
        for index in self._get_item_indices():
            item = self.items[index]
            item_type = item.get_description().type
            other_item: Optional[tuple[Item, int]] = best.get(item_type)
            if other_item is not None:
                item_price: int = item.get_price(ignore_modifier=True)
                if other_item[1] < item_price:
                    best[item_type] = (item, item_price)
            else:
                best[item_type] = (item, item.get_price(ignore_modifier=True))

        if best:
            for item, _ in best.values():
                self._equip(item, update=False)
            self.user_entity.update_equipment(self.get_equipment())

    def unequip(self, index: int) -> Optional[str]:
        if 0 <= index < len(self.items):
            item: Optional[Item] = self.items[index]
            if item is None:
                return None
            if item.id in self._equipped_ref.get():
                self._unequip(item)
                return item.print()
        return None

    def unequip_all(self) -> None:
        self._equipped_ref.set([])
        self.user_entity.update_equipment([])

    def set_limit(self, inv_limit: int) -> None:
        self.limit = inv_limit

    def get_free_count(self) -> int:
        return self.limit - sum(x is not None for x in self.items)

    def add_item(self, item: Item) -> Optional[int]:
        slot = self.get_empty_slot()
        if slot is None:
            return None
        self.items[slot] = item
        return slot

    def set_items(self, item_list: list) -> None:
        self.items = item_list[:self.limit]

    def get_equipment(self) -> list[Item]:
        return [self.items[index] for index in self._get_item_indices()
                if self.items[index].id in self._equipped_ref.get()]

    def print(self) -> str:
        il = self.limit - self.get_free_count()
        if il == 0:
            return f"{Emoji.BAG} Inventory empty {il} / {self.limit}"
        tr = [f"{Emoji.BAG} Inventory: {il} / {self.limit}"]
        for i in self._get_item_indices():
            index = i + 1
            item_str = self.items[i].print()
            equipped: str = ''
            if self.items[i].id in self._equipped_ref.get():
                equipped = f' {Emoji.EQUIPPED}'
            tr.append(f"{index}: {item_str}{equipped}")  # TODO: durability broken stuff
        return '\n'.join(tr)
