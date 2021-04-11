import json
import random
from typing import Any, Optional

from entities.bot_entity import BotEntityBuilder
from item_data.stats import Stats, StatInstance

_ENEMIES: list[BotEntityBuilder] = []
_STAT_RANGE_TO_ENEMY: dict[int, list[BotEntityBuilder]] = {}

with open('game_data/enemies.json', 'r') as f:
    item_dict: dict[str, Any] = json.load(f)
    for id_k, id_v in item_dict.items():
        stat_sum: int = 0
        stat_dict: dict[StatInstance, int] = {}
        for abv, v in id_v['Stats'].items():
            stat_dict[Stats.get_by_abv(abv)] = v
            stat_sum += v
        beb: BotEntityBuilder = BotEntityBuilder(
            id_v['Name'], stat_dict
        )
        _ENEMIES.append(beb)
        k: int = stat_sum // 15
        if stat_sum < 0:
            k = -1
        li = _STAT_RANGE_TO_ENEMY.get(k, [])
        if not li:
            _STAT_RANGE_TO_ENEMY[k] = li
        li.append(beb)


for k, v in _STAT_RANGE_TO_ENEMY.items():
    print(str(k) + ':', '/'.join([x.name for x in v]))


def get_random_enemy(stat_range: int) -> Optional[BotEntityBuilder]:
    if stat_range not in _STAT_RANGE_TO_ENEMY:
        return None
    return random.choice(_STAT_RANGE_TO_ENEMY[stat_range])
