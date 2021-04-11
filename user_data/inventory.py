from typing import Optional, Any

from entities.user_entity import UserEntity
from enums.emoji import Emoji
from item_data import items
from item_data.items import Item
from enums.item_type import ItemType
from utils import DictRef


class Inventory:
    def __init__(self, equipped_ref: DictRef, inv_limit: int, item_list: list[Item], user_entity: UserEntity):
        self.items: list[Item] = item_list
        self._equipped_ref: DictRef = equipped_ref
        self.limit: int = inv_limit
        self.user_entity: UserEntity = user_entity
        self.user_entity.update_equipment(self.get_equipment())

    def get_first(self, item_type: ItemType) -> Optional[Item]:
        for i in range(len(self.items)):
            item: Item = self.items[i]
            if item.data.get_description().type == item_type:
                return item
        return None

    def sell(self, index: int, user_id: int) -> tuple[bool, Any]:
        if index < 0 or index >= len(self.items):
            return False, True
        item = self.items[index]
        if self._is_equipped(item):
            return False, False
        items.delete_user_item(user_id, item.id)
        del self.items[index]
        return True, item

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
        if 0 <= index < len(self.items):
            item = self.items[index]
            if item.id not in self._equipped_ref.get():
                item_type = item.data.get_description().type
                for other_index in range(len(self.items)):
                    if other_index != index and self.items[other_index].id in self._equipped_ref.get() \
                            and self.items[other_index].data.get_description().type == item_type:
                        self._unequip(self.items[other_index], False)
                        break
                self._equip(item)
            return item.print()
        return None

    def equip_best(self) -> None:
        self.unequip_all()
        best: dict[ItemType, tuple[Item, int]] = {}
        for index in range(len(self.items)):
            item = self.items[index]
            item_type = item.data.get_description().type
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
            item: Item = self.items[index]
            if item.id in self._equipped_ref.get():
                self._unequip(item)
                return item.print()
        return None

    def unequip_all(self) -> None:
        self._equipped_ref.set([])
        self.user_entity.update_equipment([])

    def set_limit(self, inv_limit: int) -> None:
        self.limit = inv_limit

    def get_empty_slots(self) -> int:
        return self.limit - len(self.items)

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def set_items(self, item_list: list) -> None:
        self.items = item_list[:self.limit]

    def get_equipment(self) -> list[Item]:
        return [item for item in self.items if item.id in self._equipped_ref.get()]

    def print(self) -> str:
        il = len(self.items)
        tr = [f"{Emoji.BAG} Inventory: {il}/{self.limit}"]
        for i in range(il):
            index = i + 1
            item_str = self.items[i].print()
            if self.items[i].id in self._equipped_ref.get():
                tr.append(f"{index}: {item_str} {Emoji.EQUIPPED} ({self.items[i].durability}%)")
            else:
                tr.append(f"{index}: {item_str} ({self.items[i].durability}%)")
        return '\n'.join(tr)
