from collections import UserDict
from typing import Optional

import utils
from guild_data.guild import Guild
from user_data.user import User
from db import database


class Cache(UserDict):
    REMOVE_PCT: float = 0.2

    def __init__(self, d=None, limit: int = 100):
        super().__init__(d)
        self.limit = limit

    def clean(self):
        k_v = list(self.data.items())
        k_v.sort(key=lambda x: x[1][1])
        for k in range(int(self.limit * Cache.REMOVE_PCT)):
            del self.data[k]

    def clear_all(self):
        self.data.clear()

    def __setitem__(self, key: object, value: object):
        super().__setitem__(key, (value, utils.now()))
        if len(self.data) > self.limit:
            self.clean()

    def __getitem__(self, key: object):
        cached_item = super().__getitem__(key)
        if cached_item:
            cached_item = (cached_item[0], utils.now())
            return cached_item[0]
        return cached_item

    def get(self, key: object, default_value=None):
        return self.data.get(key, (default_value,))[0]


USER_CACHE = Cache()
GUILD_CACHE = Cache()


def get_user(user_id: int, create: bool = True) -> Optional[User]:
    user = USER_CACHE.get(user_id)
    if not user:
        if create or database.INSTANCE.get_row_data("users", {
            'id': user_id
        }):
            user = User(user_id)
            USER_CACHE[user_id] = user
        else:
            return None
    return user


def get_guild(guild_id: int, create=True) -> Optional[Guild]:
    guild = GUILD_CACHE.get(guild_id)
    if not guild:
        if create or database.INSTANCE.get_row_data("users", {
            'id': guild_id
        }):
            guild = Guild(guild_id)
            GUILD_CACHE[guild_id] = guild
        else:
            return None
    return guild
