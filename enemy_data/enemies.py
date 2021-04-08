import json
import random
from typing import Any

from entities.bot_entity import BotEntityBuilder
from item_data.stats import Stats

_ENEMIES: list[BotEntityBuilder] = []

with open('game_data/enemies.json', 'r') as f:
    item_dict: dict[str, Any] = json.load(f)
    for id_k, id_v in item_dict.items():
        _ENEMIES.append(BotEntityBuilder(
            id_v['Name'], {
                Stats.get_by_abv(abv): n for abv, n in id_v['Stats'].items()
            }
        ))


def get_random_enemy() -> BotEntityBuilder:
    return random.choice(_ENEMIES)
