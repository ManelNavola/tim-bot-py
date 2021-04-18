import json
import random
from typing import Any, Optional

import utils
from entities.bot_entity import BotEntityBuilder
from enums.location import Location
from item_data.stats import Stats, StatInstance

_ENEMIES: dict[Location, dict[str, list[BotEntityBuilder]]] = {
    x: {} for x in Location
}


def load():
    with open('game_data/enemies.json', 'r') as f:
        item_dict: dict[str, Any] = json.load(f)
        for id_k, id_v in item_dict.items():
            if id_k.startswith('X'):
                print(f"JSON not consolidated: {id_v['Name']}")
                continue
            stat_sum: int = 0
            stat_dict: dict[StatInstance, int] = {}
            for abv, v in id_v['Stats'].items():
                stat_dict[Stats.get_by_abv(abv)] = v
                stat_sum += v
            beb: BotEntityBuilder = BotEntityBuilder(
                id_v['Name'], stat_dict, enemy_id=int(id_k)
            )

            location = Location.get_from_name(id_v['Location'])
            pool = id_v.get('Pool', '')
            to_pool = _ENEMIES[location].get(pool)
            if to_pool is None:
                to_pool = []
                _ENEMIES[location][pool] = to_pool
            to_pool.append(beb)


def get_random_enemy(location: Location, pool: str = '', last_chosen_id: Optional[int] = None) \
        -> BotEntityBuilder:
    possible_enemies: list[BotEntityBuilder] = _ENEMIES[location][pool]
    if len(possible_enemies) == 0:
        return BotEntityBuilder('MissingNo, please contact the developer', {
            Stats.HP: 10
        })
    if len(possible_enemies) == 1:
        return possible_enemies[0]
    elif len(possible_enemies) == 2 and (last_chosen_id is not None):
        for i in range(2):
            if possible_enemies[i].enemy_id != last_chosen_id:
                return possible_enemies[i]
    for i in range(50):
        chosen = random.choice(possible_enemies)
        if chosen != last_chosen_id:
            return chosen
    return random.choice(possible_enemies)
