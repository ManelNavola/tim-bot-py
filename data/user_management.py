from data import database
from data.user import User

cache = {}

def get(user_id):
    if user_id in cache:
        print('cached')
        return cache[user_id]
    else:
        print('miss')
        user = load(user_id)
        cache[user_id] = user
        return user

def load(user_id):
    cur = database.cursor()
    cur.execute(f"""SELECT * from users WHERE id = {user_id}""")
    data = cur.fetchone()
    print(data)
    user = User(user_id, data)
    if not data:
        save(user, True)
    try_cleanup()
    return user

def save(user, first_time=False):
    cur = database.cursor()
    if first_time:
        print('Try saving (first time)')
        a, b = database.parse_insert(user.data, {'id': user.id})
        print(a, b)
        cur.execute(f"""INSERT INTO users {a} VALUES {b}""")
    else:
        print('Try saving')
        to_save = database.parse_set(user.data)
        print(to_save)
        cur.execute(f"""UPDATE users SET {to_save} WHERE id = {user_id}""")

def try_cleanup():
    pass