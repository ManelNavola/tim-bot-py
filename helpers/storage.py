from typing import Optional

from db import database
from guild_data.guild import Guild
from helpers.cache import Cache
from user_data.user import User

USER_CACHE = Cache()
GUILD_CACHE = Cache()


def clear_cache():
    USER_CACHE.clear_all()
    GUILD_CACHE.clear_all()


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
