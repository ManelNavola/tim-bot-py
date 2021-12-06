import json
import random
import typing
from typing import Any, Optional, List, Dict

from enums.location import Location
from item_data.stat import Stat

if typing.TYPE_CHECKING:
    from enemy_data.bot_entity_builder import BotEntityBuilder

_ENEMIES: Dict[Location, Dict[str, List['BotEntityBuilder']]] = {
    x: {} for x in Location
}

_ENEMY_IDS: Dict[int, 'BotEntityBuilder'] = {}


def load():
    from enemy_data.bot_entity_builder import BotEntityBuilder
    enemy_count: int = 0
    with open('game_data/enemies.json', 'r') as f:
        item_dict: Dict[str, Any] = json.load(f)
        for id_k, id_v in item_dict.items():
            if id_k.startswith('X'):
                print(f"JSON not consolidated: {id_v['Name']}")
                continue
            stat_sum: int = 0
            stat_dict: Dict[Stat, int] = {}
            for abv, v in id_v['Stats'].items():
                stat_dict[Stat.get_by_abv(abv)] = v
                stat_sum += v
            beb: BotEntityBuilder = BotEntityBuilder(
                id_v['Name'], stat_dict, enemy_id=int(id_k)
            )
            _ENEMY_IDS[int(id_k)] = beb

            location = Location.from_id(id_v['Location'])
            pool = id_v.get('Pool', '')
            to_pool = _ENEMIES[location].get(pool)
            if to_pool is None:
                to_pool = []
                _ENEMIES[location][pool] = to_pool
            to_pool.append(beb)
            enemy_count += 1
    _ENEMY_IDS[-1] = BotEntityBuilder('MissingNo, please contact the developer', {
        Stat.HP: 10
    })
    print(f"Loaded {enemy_count} enemies")


def get_enemy(enemy_id: int) -> 'BotEntityBuilder':
    return _ENEMY_IDS[enemy_id]


def get_random_enemy(location: Location, pool: str = '', last_chosen_id: Optional[int] = None) \
        -> 'BotEntityBuilder':
    possible_enemies: List['BotEntityBuilder'] = _ENEMIES[location][pool]
    if len(possible_enemies) == 0:
        return get_enemy(-1)
    if len(possible_enemies) == 1:
        return possible_enemies[0]
    elif len(possible_enemies) == 2 and (last_chosen_id is not None):
        for i in range(2):
            if possible_enemies[i].enemy_id != last_chosen_id:
                return possible_enemies[i]
    for i in range(50):
        chosen = random.choice(possible_enemies)
        if chosen.enemy_id != last_chosen_id:
            return chosen
    return random.choice(possible_enemies)
