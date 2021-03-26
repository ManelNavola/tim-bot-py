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
    cur = database.cursor()
    if first_time:
        keys, values = database.parse_insert(user.data, {'id': user.id})
        cur.execute(f"""INSERT INTO users {keys} VALUES {values}""")
        database.commit()
    else:
        user_id = user.id
        to_save = database.parse_set(user.data)
        cur.execute(f"""UPDATE users SET {to_save} WHERE id = '{user_id}'""")
        database.commit()

def try_cleanup():
    pass