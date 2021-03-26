from utils import utils
from data import database

global_cache = {}

def register_global(guild_id):
    data = {
        "money": 0,
        "money_time": 0
    }
    return data

def get_global(guild_id):
    guild_id = str(guild_id)
    if guild_id in global_cache:
        return global_cache[guild_id]
    else:
        data = database.get_row_data("global", guild_id)
        if data:
            global_cache[guild_id] = data["json"]
            return data["json"]
        else:
            data = {
                "table_money": 0
            }
            database.insert_data("global", guild_id, {"json": data})
            global_cache[guild_id] = data
        try_cleanup()
        return data

def update_global(guild_id):
    guild_id = str(guild_id)
    glb = get_global(guild_id)
    database.update_data("global", guild_id, {"json": glb})

def try_cleanup():
    pass

class Table:
    @staticmethod
    def get_money(ctx):
        glb = get_global(ctx.guild_id)
        if glb['table_money'] == 0:
            return 0
        return glb['table_money'] + (utils.now() - glb['table_money_time']) // 15

    @staticmethod
    def place_money(ctx, amount):
        glb = get_global(ctx.guild_id)
        if glb['table_money'] == 0:
            glb['table_money_time'] = utils.now()
            glb['table_money'] += amount
        else:
            glb['table_money'] += amount
        update_global(ctx.guild_id)

    @staticmethod
    def retrieve_money(ctx):
        glb = get_global(ctx.guild_id)
        money = glb['table_money']
        if money == 0:
            return money
        glb['table_money'] = 0
        update_global(ctx.guild_id)
        return money