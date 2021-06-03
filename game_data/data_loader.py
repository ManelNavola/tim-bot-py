from enemy_data import enemy_utils
from helpers import translate
from item_data import item_loader


def load():
    translate.load()
    item_loader.load()
    enemy_utils.load()
