from data import database
from data.user import User

cache = {}

def get(ctx):
    user_id = str(ctx.author_id)
    if user_id in cache:
        return cache[user_id]
    else:
        user = load(user_id)
        cache[user_id] = user
        return user

def load(user_id):
    data = database.get_row_data("users", user_id)
    user = User(user_id, data)
    if not data:
        save(user, True)
    try_cleanup()
    return user

def save(user, first_time=False):
    if first_time:
        database.insert_data("users", user.id, user.data)
    else:
        database.update_data("users", user.id, user.data)

def try_cleanup():
    pass