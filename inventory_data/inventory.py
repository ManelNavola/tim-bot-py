from typing import Optional

import utils
from utils import DictRef
from inventory_data.items import Item
from inventory_data.stats import Stats, StatInstance


class Inventory:
    def __init__(self, equipped_ref: DictRef, inv_limit: int, items: list[Item]):
        self.items: list[Item] = items
        self._equipped_ref: DictRef = equipped_ref
        self.limit: int = inv_limit
        self.stats: dict[Stats, int] = {}
        self._stats_print: str = ""
        self._calculate_stats()

    def _calculate_stats(self):
        self.stats: dict[StatInstance, int] = {
            stat_instance: 0 for stat_instance in Stats.get_all().values() if stat_instance.base > 0
        }
        tp = []
        for index in self._equipped_ref.get():
            item = self.items[index]
            for stat, value in item.data.stats.items():
                self.stats[stat] = self.stats.get(stat, 0) + value
        for stat, value in self.stats.items():
            tp.append(stat.print(value))
        self._stats_print = '\n'.join(tp)

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
                self._calculate_stats()
            return item.print()
        return None

    def unequip(self, index: int) -> Optional[str]:
        if 0 <= index < len(self.items):
            if index in self._equipped_ref:
                self._equipped_ref.get().remove(index)
                self._equipped_ref.update()
                self._calculate_stats()
                return self.items[index].print()
        return None

    def set_limit(self, inv_limit: int):
        self.limit = inv_limit

    def get_empty_slots(self):
        return self.limit - len(self.items)

    def add_item(self, item: Item):
        self.items.append(item)

    def set_items(self, items: list) -> None:
        self.items = items[:self.limit]

    def print_inventory(self) -> str:
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

    def print_stats(self) -> str:
        tr = [f"{utils.Emoji.STATS} Player Stats:", self._stats_print]
        return '\n'.join(tr)
