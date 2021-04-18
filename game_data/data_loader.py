from enemy_data import enemy_utils
from item_data.item_classes import ItemDescription


def load():
    ItemDescription.load()
    enemy_utils.load()
