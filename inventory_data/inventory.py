from typing import Optional, Any

import utils
from inventory_data import items
from inventory_data.entity import UserEntity
from utils import DictRef
from inventory_data.items import Item, ItemType


class Inventory:
    def __init__(self, equipped_ref: DictRef, inv_limit: int, item_list: list[Item], user_entity: UserEntity):
        self.items: list[Item] = item_list
        self._equipped_ref: DictRef = equipped_ref
        self.limit: int = inv_limit
        self.user_entity: UserEntity = user_entity
        self.user_entity.update_items(self.get_equipment())

    def get_first(self, item_type: ItemType) -> Optional[Item]:
        for i in range(len(self.items)):
            item: Item = self.items[i]
            if item.data.get_description().type == item_type:
                return item
        return None

    def sell(self, index: int, user_id: int) -> tuple[bool, Any]:
        if index < 0 or index >= len(self.items):
            return False, True
        if index in self._equipped_ref.get():
            return False, False
        item = self.items[index]
        items.delete_user_item(user_id, item.id)
        del self.items[index]
        return True, item

    def equip(self, index: int) -> Optional[str]:
        if 0 <= index < len(self.items):
            item = self.items[index]
            if item.id not in self._equipped_ref.get():
                item_type = item.data.get_description().type
                for other_index in range(len(self.items)):
                    if other_index != index and self.items[other_index].id in self._equipped_ref.get() \
                            and self.items[other_index].data.get_description().type == item_type:
                        self.unequip(other_index, False)
                        break
                # Equip
                self._equipped_ref.get_update().append(item.id)
                self.user_entity.update_items(self.get_equipment())
            return item.print()
        return None

    def unequip(self, index: int, update: bool = True) -> Optional[str]:
        if 0 <= index < len(self.items):
            item: Item = self.items[index]
            if item.id in self._equipped_ref.get():
                # Unequip
                self._equipped_ref.get_update().remove(item.id)
                if update:
                    self.user_entity.update_items(self.get_equipment())
                return item.print()
        return None

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
        tr = [f"{utils.Emoji.BAG} Inventory: {il}/{self.limit}"]
        for i in range(il):
            index = i + 1
            item_str = self.items[i].print()
            if self.items[i].id in self._equipped_ref.get():
                tr.append(f"{index}: {item_str} {utils.Emoji.EQUIPPED} ({self.items[i].durability}%)")
            else:
                tr.append(f"{index}: {item_str} ({self.items[i].durability}%)")
        return '\n'.join(tr)
