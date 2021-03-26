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