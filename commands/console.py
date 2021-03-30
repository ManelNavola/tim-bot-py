import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

import utils
from commands.command import MockCommand
from data import storage
from db import database


async def execute():
    rie = partial(asyncio.get_event_loop().run_in_executor, ThreadPoolExecutor(1))
    while True:
        print("> ", end='')
        c = await rie(input)
        args = c.split(' ')
        try:
            if args[0] == 'reload':
                print("Reloading bot...")
                os.system("python main.py")
                exit()
            elif args[0] == 'reset':
                for k in database.JSON_DEFAULTS.keys():
                    database.INSTANCE.cursor.execute(f"DELETE FROM {k}")
                database.INSTANCE.commit(True)
                print("Data cleared")
                print("Restarting bot...")
                os.system("python main.py")
                exit()
            elif args[0] == 'clear':
                for k in database.JSON_DEFAULTS.keys():
                    database.INSTANCE.cursor.execute(f"DELETE FROM {k}")
                database.INSTANCE.commit(True)
                print("Data cleared")
            elif args[0] == 'add_money':
                user = storage.get_user(116901729823358977)
                money = int(args[1])
                user.add_money(money)
                user.save()
                database.INSTANCE.commit()
                print(f"Added {utils.print_money(money)} ({utils.print_money(user.get_money())})")
            elif args[0] == 'add_money':
                user = storage.get_user(116901729823358977)
                money = int(args[1])
                user.remove_money(money)
                user.save()
                database.INSTANCE.commit()
                print(f"Removed {utils.print_money(money)} ({utils.print_money(user.get_money())})")
            elif args[0] == 'end_bet':
                mock_cmd = MockCommand()
                guild = storage.get_guild(824723874544746507)
                await guild.bet.end_bet(mock_cmd.ctx)
            elif len(args[0]) > 0:
                print("Unknown command")
        except Exception as e:
            print(f"Could not run command {args[0]}")
            print(e)
