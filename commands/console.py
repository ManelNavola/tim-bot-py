import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

from db import database


async def execute():
    rie = partial(asyncio.get_event_loop().run_in_executor, ThreadPoolExecutor(1))
    while True:
        print("> ", end='')
        c = await rie(input)
        args: list[str] = c.split(' ')
        try:
            if args[0].startswith('rel'):
                print("Reloading bot...")
                os.system("python main.py")
                exit()
            elif args[0].startswith('res'):
                for k in ['guild_items', 'user_items', 'items', 'guilds', 'users']:
                    database.INSTANCE.get_cursor().execute(f"DELETE FROM {k}")
                database.INSTANCE.commit()
                print("Data cleared")
                print("Restarting bot...")
                os.system("python main.py")
                exit()
            elif args[0].startswith('cl'):
                for k in ['guild_items', 'user_items', 'items', 'guilds', 'users']:
                    database.INSTANCE.get_cursor().execute(f"DELETE FROM {k}")
                database.INSTANCE.commit()
                print("Data cleared")
            elif len(args[0]) > 0:
                print("Unknown command")
        except Exception as e:
            print(f"Could not run command {args[0]}")
            print(e)
