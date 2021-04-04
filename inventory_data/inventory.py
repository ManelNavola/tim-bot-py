from typing import Optional, Any

import utils
from inventory_data import items
from utils import DictRef
from inventory_data.items import Item


class Inventory:
    def __init__(self, equipped_ref: DictRef, inv_limit: int, item_list: list[Item]):
        self.items: list[Item] = item_list
        self._equipped_ref: DictRef = equipped_ref
        self.limit: int = inv_limit

    def sell(self, index: int, user_id: int) -> tuple[bool, Any]:
        if index < 0 or index >= len(self.items):
            return False, True
        if index in self._equipped_ref.get():
            return False, False
        item = self.items[index]
        items.delete_user_item(user_id, item.id)
        return True, item

    def equip(self, index: int) -> Optional[str]:
        if 0 <= index < len(self.items):
            item = self.items[index]
            if index not in self._equipped_ref.get():
                item_type = item.data.get_description().type
                for other_index in range(len(self.items)):
                    if other_index != index and self.items[other_index].data.get_description().type == item_type:
                        self.unequip(other_index)
                        break
                self._equipped_ref.get().append(index)
                self._equipped_ref.update()
            return item.print()
        return None

    def unequip(self, index: int) -> Optional[str]:
        if 0 <= index < len(self.items):
            if index in self._equipped_ref:
                self._equipped_ref.get().remove(index)
                self._equipped_ref.update()
                return self.items[index].print()
        return None

    def set_limit(self, inv_limit: int):
        self.limit = inv_limit

    def get_empty_slots(self):
        return self.limit - len(self.items)

    def add_item(self, item: Item):
        self.items.append(item)

    def set_items(self, item_list: list) -> None:
        self.items = item_list[:self.limit]

    def get_equipment(self) -> list[Item]:
        return [self.items[i] for i in range(len(self.items)) if i in self._equipped_ref.get()]

    def print(self) -> str:
        il = len(self.items)
        tr = [f"{utils.Emoji.BAG} Inventory: {il}/{self.limit}"]
        for i in range(il):
            index = i + 1
            item_str = self.items[i].print()
            if i in self._equipped_ref.get():
                tr.append(f"{index}: {item_str} {utils.Emoji.EQUIPPED} ({self.items[i].durability}%)")
            else:
                tr.append(f"{index}: {item_str} ({self.items[i].durability}%)")
        return '\n'.join(tr)
