from enemy_data import enemy_utils
from helpers import translate
from item_data import item_utils


def load():
    translate.load()
    item_utils.load()
    enemy_utils.load()
