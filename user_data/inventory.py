from enum import unique, Enum
from typing import Optional, Any

import utils
from db.database import PostgreSQL
from entities.user_entity import UserEntity
from enums.emoji import Emoji
from helpers.action_result import ActionResult
from helpers.dictref import DictRef
from enums.item_type import ItemType
from item_data import item_utils
from item_data.item_classes import Item
from item_data.item_utils import delete_user_item


class Inventory:
    def __init__(self, db: PostgreSQL, equipped_ref: DictRef[list[int]], inv_limit: int, item_list: list[Item],
                 user_entity: UserEntity, user_id: int):
        self._db: PostgreSQL = db
        self._user_id: int = user_id
        self._items: list[Optional[Item]] = item_list
        self._equipped_ref: DictRef[list[int]] = equipped_ref
        self._limit: int = inv_limit
        self._user_entity: UserEntity = user_entity
        self._user_entity.update_equipment(self.get_equipment())

    def _get_item_indices(self):
        return [i for i, j in enumerate(self._items) if j is not None]

    def get_first(self, item_type: ItemType) -> Optional[Item]:
        for i in self._get_item_indices():
            item: Item = self._items[i]
            if item.get_description().type == item_type:
                return item
        return None

    def get_empty_slot(self) -> Optional[int]:
        for i in range(len(self._items)):
            if self._items[i] is None:
                return i
        return None

    def _move(self, from_slot: str, to_slot: str) -> None:
        if from_slot == to_slot:
            return
        item: Item = self._get_dict_ref(from_slot).get()
        other_item: Optional[Item] = self._get_dict_ref(to_slot).try_get()
        self._get_dict_ref(to_slot).set(item)

        if other_item is None:
            move_user_item_slot(self._db, self._user_id, item, to_slot)
            self._get_dict_ref(from_slot).delete()
        else:
            # Swap
            swap_user_items(self._db, self._user_id, from_slot, to_slot, item, other_item)
            self._get_dict_ref(from_slot).set(other_item)

    def _delete(self, slot: str) -> None:
        item: Item = self._get_dict_ref(slot).get()
        self._get_dict_ref(slot).delete()
        delete_user_item(self._db, self._user_id, item)

    def add_item(self, item: Item, slot: str) -> None:
        self._get_dict_ref(slot).set(item)

    def sell(self, lang: str, slot: str) -> ActionResult:
        if self._get_slot_type(slot) == SlotType.INVALID:
            return ActionResult(message='INVENTORY.INVALID_SLOT_TYPE')
        item: Optional[Item] = self._get_dict_ref(slot).try_get()
        if item is None:
            return ActionResult(message='INVENTORY.MISSING_ITEM')
        if self._get_slot_type(slot) == SlotType.EQUIPMENT:
            return ActionResult(message='INVENTORY.CANNOT_SELL_EQUIPPED')
        self._delete(slot)
        price: int = round(item.get_price() * Inventory.SELL_MULTIPLIER)
        return ActionResult(message='INVENTORY.SOLD', success=True, item=item.print(),
                            price=price, money=utils.print_money(lang, price))

    def equip(self, slot: str) -> ActionResult:
        if self._get_slot_type(slot) != SlotType.ITEMS:
            return ActionResult(message='INVENTORY.INVALID_SLOT_TYPE')
        item: Optional[Item] = self._get_dict_ref(slot).try_get()
        if item is None:
            return ActionResult(message='INVENTORY.MISSING_ITEM')
        if isinstance(item, Equipment):
            equipment_slot: str = Inventory.EQUIPMENT_TYPE_TO_CHAR[item.get_desc().subtype]
            self._move(slot, equipment_slot)
            self.update_equipment()
            return ActionResult(message='INVENTORY.EQUIPPED', success=True, item=item.print())
        else:
            return ActionResult(message='INVENTORY.ITEM_NOT_EQUIPMENT')

    def equip_best(self) -> ActionResult:
        inventory_equipment: dict[EquipmentType, tuple[str, Equipment]] = {}
        for et in EquipmentType:
            equipment: Optional[Equipment] = self._equipment.get(et)
            if equipment is not None:
                inventory_equipment[et] = (Inventory.EQUIPMENT_TYPE_TO_CHAR[et], equipment)
        for slot_int, item in self._items.items():
            if isinstance(item, Equipment):
                other_equipment: Optional[tuple[str, Equipment]] = inventory_equipment.get(item.get_desc().subtype)
                if other_equipment is None:
                    inventory_equipment[item.get_desc().subtype] = (str(slot_int), item)
                else:
                    if other_equipment[1].get_price(True) < item.get_price(True):
                        inventory_equipment[item.get_desc().subtype] = (str(slot_int), item)
        item_list: list[str] = []
        for et, tup in inventory_equipment.items():
            self._move(tup[0], Inventory.EQUIPMENT_TYPE_TO_CHAR[tup[1].get_desc().subtype])
            item_list.append(tup[1].print())
        self.update_equipment()
        if item_list:
            return ActionResult(message='INVENTORY.EQUIPPED', success=True, item='\n' + '\n'.join(item_list))
        else:
            return ActionResult(message='INVENTORY.MISSING_EQUIPMENT')

    def unequip(self, slot: str) -> ActionResult:
        if self._get_slot_type(slot) != SlotType.EQUIPMENT:
            return ActionResult(message='INVENTORY.INVALID_SLOT_TYPE')
        item: Optional[Item] = self._get_dict_ref(slot).try_get()
        if item is None:
            return ActionResult(message='INVENTORY.MISSING_ITEM')
        new_slot: Optional[str] = self.get_empty_slot(SlotType.ITEMS)
        if new_slot is None:
            return ActionResult(message='INVENTORY.FULL')
        self._move(slot, new_slot)
        self.update_equipment()
        return ActionResult(message='INVENTORY.UNEQUIPPED', success=True, item=item.print())

    def get_equipment(self) -> dict[EquipmentType, Equipment]:
        return self._equipment

    def print(self, lang: str) -> str:
        ta: list[str] = []
        # Equipment
        if self._equipment:
            ta.append(tr(lang, 'INVENTORY.EQUIPMENT', EMOJI_EQUIPMENT=Emoji.SHIELD))
            for char, et in Inventory.CHAR_TO_EQUIPMENT_TYPE.items():
                equipment: Optional[Equipment] = self._equipment.get(et)
                if equipment is not None:
                    ta.append(f"{char}: {equipment.print()}")
        else:
            ta.append(tr(lang, 'INVENTORY.NO_EQUIPMENT', EMOJI_EQUIPMENT=Emoji.SHIELD))
        # Inventory
        ta.append(tr(lang, 'INVENTORY.INVENTORY', EMOJI_INVENTORY=Emoji.BAG,
                     busy=len(self._items), total=self._item_slots))
        for i in range(1, self._item_slots + 1):
            item: Optional[Item] = self._items.get(i)
            if item is not None:
                ta.append(f"{i}: {item.print()}")
        # Potions
        ta.append(tr(lang, 'INVENTORY.POTIONS', EMOJI_POTION=Emoji.POTION,
                     busy=len(self._potions), total=self._potion_slots))
        for i in range(1, self._potion_slots + 1):
            item: Optional[Item] = self._potions.get(i)
            if item is not None:
                ta.append(f"p{i}: {item.print()}")
        return '\n'.join(ta)

    # def _get_item_indices(self):
    #     return [i for i, j in enumerate(self._items) if j is not None]
    #
    # def get_first(self, item_type: EquipmentType) -> Optional[Equipment]:
    #     for i in self._get_item_indices():
    #         item: Equipment = self._items[i]
    #         if item.get_description().type == item_type:
    #             return item
    #     return None
    #
    # def get_empty_slot(self) -> Optional[int]:
    #     for i in range(len(self._items)):
    #         if self._items[i] is None:
    #             return i
    #     return None
    #
    # def sell(self, index: int, user_id: int) -> tuple[bool, Any]:
    #     if index < 0 or index >= len(self._items):
    #         return False, True
    #     item = self._items[index]
    #     if item is None:
    #         return False, True
    #     if self._is_equipped(item):
    #         return False, False
    #     delete_user_item(self._db, user_id, item)
    #     self._items[index] = None
    #     return True, item
    #
    # def sell_all(self) -> tuple[int, int]:
    #     total_items: int = 0
    #     total_price: int = 0
    #     for i in self._get_item_indices():
    #         if self._items[i].id not in self._equipped_ref.get():
    #             success, result = self.sell(i, self._user_id)
    #             if success:
    #                 item: Equipment = result
    #                 price = int(item.get_price() * Shop.SELL_MULTIPLIER)
    #                 total_price += price
    #                 total_items += 1
    #             else:
    #                 if result:
    #                     break
    #     return total_items, total_price
    #
    # def _is_equipped(self, item: Equipment) -> bool:
    #     return item.id in self._equipped_ref.get()
    #
    # def _equip(self, item: Equipment, update: bool = True) -> None:
    #     self._equipped_ref.get_update().append(item.id)
    #     if update:
    #         self._user_entity.update_equipment(self.get_equipment())
    #
    # def _unequip(self, item: Equipment, update: bool = True) -> None:
    #     self._equipped_ref.get_update().remove(item.id)
    #     if update:
    #         self._user_entity.update_equipment(self.get_equipment())
    #
    # def equip(self, index: int) -> Optional[str]:
    #     if index in self._get_item_indices():
    #         item = self._items[index]
    #         if item.id not in self._equipped_ref.get():
    #             item_type = item.get_description().type
    #             for other_index in self._get_item_indices():
    #                 if other_index != index and self._items[other_index].id in self._equipped_ref.get() \
    #                         and self._items[other_index].get_description().type == item_type:
    #                     self._unequip(self._items[other_index], False)
    #                     break
    #             self._equip(item)
    #         return item.print()
    #     return None
    #
    # def equip_best(self) -> None:
    #     self.unequip_all()
    #     best: dict[EquipmentType, tuple[Equipment, int]] = {}
    #     for index in self._get_item_indices():
    #         item = self._items[index]
    #         item_type = item.get_description().type
    #         other_item: Optional[tuple[Equipment, int]] = best.get(item_type)
    #         if other_item is not None:
    #             item_price: int = item.get_price(ignore_modifier=True)
    #             if other_item[1] < item_price:
    #                 best[item_type] = (item, item_price)
    #         else:
    #             best[item_type] = (item, item.get_price(ignore_modifier=True))
    #
    #     if best:
    #         for item, _ in best.values():
    #             self._equip(item, update=False)
    #         self._user_entity.update_equipment(self.get_equipment())
    #
    # def unequip(self, index: int) -> Optional[str]:
    #     if 0 <= index < len(self._items):
    #         item: Optional[Equipment] = self._items[index]
    #         if item is None:
    #             return None
    #         if item.id in self._equipped_ref.get():
    #             self._unequip(item)
    #             return item.print()
    #     return None
    #
    # def unequip_all(self) -> None:
    #     self._equipped_ref.set([])
    #     self._user_entity.update_equipment([])
    #
    # def set_limit(self, inv_limit: int) -> None:
    #     self._limit = inv_limit
    #     if len(self._items) < self._limit:
    #         self._items += [None] * (self._limit - len(self._items))
    #
    # def get_free_count(self) -> int:
    #     return self._limit - sum(x is not None for x in self._items)
    #
    # def create_item(self, item: Equipment) -> Optional[int]:
    #     slot = self.get_empty_slot()
    #     if slot is None:
    #         return None
    #     item_utils.create_user_item(self._db, self._user_id, item, slot)
    #     self._items[slot] = item
    #     return slot
    #
    # def set_items(self, item_list: list) -> None:
    #     self._items = item_list[:self._limit]
    #
    # def get_equipment(self) -> list[Equipment]:
    #     return [self._items[index] for index in self._get_item_indices()
    #             if self._items[index].id in self._equipped_ref.get()]
    #
    # def print(self) -> str:
    #     il = self._limit - self.get_free_count()
    #     if il == 0:
    #         return f"{Emoji.BAG} Inventory empty {il} / {self._limit}"
    #     tr = [f"{Emoji.BAG} Inventory: {il} / {self._limit}"]
    #     for i in self._get_item_indices():
    #         index = i + 1
    #         item_str = self._items[i].print()
    #         equipped: str = ''
    #         if self._items[i].id in self._equipped_ref.get():
    #             equipped = f' {Emoji.EQUIPPED}'
    #         tr.append(f"{index}: {item_str}{equipped}")
    #     return '\n'.join(tr)
