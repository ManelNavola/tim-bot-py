from typing import Optional

from discord import Client
from discord.utils import get

import utils
from db.database import PostgreSQL
from guild_data.guild import Guild
from helpers.cache import Cache
from user_data.user import User

USER_CACHE = Cache()
GUILD_CACHE = Cache()


def clear_cache():
    USER_CACHE.clear_all()
    GUILD_CACHE.clear_all()


def get_user(db: PostgreSQL, user_id: int, create: bool = True) -> Optional[User]:
    user = USER_CACHE.get(user_id)
    if not user:
        if create or db.get_row_data("users", {
            'id': user_id
        }):
            user = User(db, user_id)
            USER_CACHE[user_id] = user
        else:
            return None
    return user


def get_guild(db: PostgreSQL, guild_id: int, create=True) -> Optional[Guild]:
    guild = GUILD_CACHE.get(guild_id)
    if not guild:
        if create or db.get_row_data("users", {
            'id': guild_id
        }):
            guild = Guild(db, guild_id)
            GUILD_CACHE[guild_id] = guild
        else:
            return None
    return guild
