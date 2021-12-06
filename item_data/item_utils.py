from typing import Any, Dict

from db.database import PostgreSQL
from enums.item_type import ItemType
from item_data import item_loader
from item_data.item_classes import Equipment, Item, Potion
from item_data.item_descriptions import ItemDescription


def create_guild_item(db: PostgreSQL, guild_id: int, item: 'Item', slot: str) -> None:
    fetch_data = db.insert_data("items", {
        'data': item.to_dict(),
        'desc_id': item.get_desc().id
    }, returns=True, return_columns=['id'])
    item._id = fetch_data['id']
    db.insert_data("guild_items", {
        'guild_id': guild_id,
        'slot': slot,
        'item_id': item.get_id()
    })


def create_user_item(db: PostgreSQL, user_id: int, item: 'Item', slot: str) -> None:
    fetch_data = db.insert_data('items', {
        'data': item.to_dict(),
        'desc_id': item.get_desc().id
    }, returns=True, return_columns=['id'])
    item._id = fetch_data['id']
    db.insert_data('user_items', {
        'user_id': user_id,
        'item_id': item.get_id(),
        'slot': slot
    })


def move_user_item_slot(db: PostgreSQL, user_id: int, item: 'Item', new_slot: str):
    db.update_data('user_items', dict(user_id=user_id, item_id=item.get_id()), dict(slot=new_slot))


def swap_user_items(db: PostgreSQL, user_id: int, from_slot: str, to_slot: str, from_item: 'Item', to_item: 'Item'):
    db.update_data('user_items', dict(user_id=user_id, slot=from_slot), dict(item_id=from_item.get_id()))
    db.update_data('user_items', dict(user_id=user_id, slot=to_slot),   dict(item_id=to_item.get_id()))


def delete_user_item(db: PostgreSQL, user_id: int, item: 'Item') -> None:
    db.delete_row("user_items", dict(user_id=user_id, item_id=item.get_id()))
    db.delete_row("items", dict(id=item.get_id()))
    item._id = -1


def transfer_guild_to_user(db: PostgreSQL, guild_id: int, item: 'Item', user_id: int, slot: str) -> None:
    db.delete_row("guild_items", dict(guild_id=guild_id, item_id=item.get_id()))
    db.insert_data('user_items', {
        'user_id': user_id,
        'item_id': item.get_id(),
        'slot': slot
    })
    item._id = -1


def clone_item(db: PostgreSQL, item: 'Item') -> Item:
    fetch_data = db.insert_data('items', {
        'data': item.to_dict(),
        'desc_id': item.get_desc().id
    }, returns=True, return_columns=['id'])
    return get_from_dict(fetch_data['id'], item.get_desc().id, item.to_dict())


def get_from_dict(item_id: int, desc_id: int, data_dict: Dict[str, Any]) -> 'Item':
    description: ItemDescription = item_loader.get_description(desc_id)
    it: ItemType = description.type
    item: Item
    if it == ItemType.EQUIPMENT:
        item = Equipment(item_id)
    elif it == ItemType.POTION:
        item = Potion(item_id)
    else:
        raise KeyError("Unknown item type")
    item.from_dict(desc_id, data_dict)
    return item
