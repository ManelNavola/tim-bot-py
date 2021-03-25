from data import database

cache = {}

def get(user_id):
    if user_id in cache:
        print('cached')
        return cache[user_id]
    else:
        print('miss')
        user = load(user_id)
        cache[user_id] = user
        

def load(user_id):
    print('Try loading')
    cur = connection.cursor()  
    cur.execute(f"""SELECT * from users WHERE id = {user_id}""")
    data = cur.fetchone()
    user = User(user_id, data)
    if not data:
        save(user, True)
    try_cleanup()
    return user

def save(user, first_time=False):
    if first_time:
        print('Try saving (first time)')
        a, b = parse_insert(user.data, {'id': user.id})
        cur.execute(f"""INSERT INTO users {a} VALUES {b}""")
    else:
        print('Try saving')
        to_save = parse_set(user.data)
        cur.execute(f"""UPDATE users SET {to_save} WHERE id = {user_id}""")

def try_cleanup():
    pass