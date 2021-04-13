import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

from db import database
from helpers import storage


def clear():
    for k in ['guild_items', 'user_items', 'items', 'guilds', 'users']:
        database.INSTANCE.get_cursor().execute(f"DELETE FROM {k}")
    database.INSTANCE.commit(True)
    storage.clear_cache()
    print("Data cleared")


def reload():
    print("Reloading bot...")
    os.system("python main.py")
    exit()


async def execute():
    rie = partial(asyncio.get_event_loop().run_in_executor, ThreadPoolExecutor(1))
    while True:
        print("> ", end='')
        c = await rie(input)
        args: list[str] = c.split(' ')
        try:
            if args[0].startswith('rel'):
                reload()
            elif args[0].startswith('res'):
                clear()
                reload()
            elif args[0].startswith('cl'):
                clear()
            elif len(args[0]) > 0:
                print("Unknown command")
        except Exception as e:
            print(f"Could not run command {args[0]}")
            print(e)
