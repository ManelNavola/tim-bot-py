from typing import Optional

from discord_slash import SlashContext

import utils
from guild_data.battle import Battle
from guild_data.bet import Bet
from common.incremental import Incremental
from guild_data.shop import Shop
from inventory_data.entity import Entity
from user_data.user import User
from db import database
from db.row import Row
from utils import DictRef, TimeSlot, TimeMetric


class Guild(Row):
    TABLE_HYPE = TimeSlot(TimeMetric.MINUTE, 30)
    TABLE_INCREMENT = 2
    TABLE_MIN = 10
    LEADERBOARD_TOP = 5
    SHOP_DURATION = TimeSlot(TimeMetric.HOUR, 1)
    SHOP_ITEMS = 5

    def __init__(self, guild_id: int):
        super().__init__("guilds", dict(id=guild_id))
        self.id: int = guild_id
        self._box: Incremental = Incremental(DictRef(self._data, 'table_money'),
                                             DictRef(self._data, 'table_money_time'),
                                             TimeSlot(TimeMetric.MINUTE, Guild.TABLE_INCREMENT))
        self.bet: Bet = Bet(DictRef(self._data, 'ongoing_bet'))
        self.registered_user_ids: set[int] = set(self._data['user_ids'])
        self.shop: Shop = Shop(DictRef(self._data, 'shop_time'), self.id)
        self.stat_being_to_battle = {}

    def load_defaults(self):
        return {
            'table_money': 0,  # bigint
            'table_money_time': utils.now(),  # bigint
            'ongoing_bet': {},  # json
            'user_ids': [],  # bigint[]
            'shop_time': 0,  # bigint
        }

    def register_user_id(self, user_id: int) -> None:
        if user_id not in self.registered_user_ids:
            self._data['user_ids'] = self._data['user_ids'] + [user_id]
            self.registered_user_ids.add(user_id)

    def print_leaderboard(self) -> str:
        database.INSTANCE.execute(f"SELECT last_name, money FROM users "
                                  f"INNER JOIN guilds ON guilds.id = {self.id} "
                                  f"AND users.id = ANY({database.convert_sql_value(list(self.registered_user_ids))}) "
                                  f"ORDER BY money DESC "
                                  f"LIMIT {Guild.LEADERBOARD_TOP}")
        users = database.INSTANCE.get_cursor().fetchall()
        ld = [f"{utils.Emoji.TROPHY} Top {Guild.LEADERBOARD_TOP} players:"]
        for i in range(len(users)):
            if i == 0:
                ld.append(f"{utils.Emoji.FIRST_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            elif i == 1:
                ld.append(f"{utils.Emoji.SECOND_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            elif i == 2:
                ld.append(f"{utils.Emoji.THIRD_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            else:
                ld.append(f"#{i + 1}: {users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
        return '\n'.join(ld)

    def _get_box_end(self) -> int:
        return self._data['table_money_time'] + Guild.TABLE_HYPE.seconds()

    def get_box(self) -> int:
        if self._data['table_money'] > 0:
            now = min(utils.now(), self._get_box_end())
            return self._box.get(now)
        else:
            return 0

    def place_box(self, user: User, amount: int) -> bool:
        if user.remove_money(amount):
            self._box.set(self.get_box() + amount)
            return True
        return False

    def retrieve_box(self, user: User) -> int:
        space = user.get_total_money_space()
        to_retrieve = min(self.get_box(), space)
        if to_retrieve == 0:
            return 0
        self._box.set(self.get_box() - to_retrieve)
        user.add_money(to_retrieve)
        return to_retrieve

    def print_box_rate(self) -> str:
        diff = self._get_box_end() - utils.now()
        if diff < 0:
            return ""
        else:
            return f"{self._box.print_rate()} for {utils.print_time(diff)}"

    async def start_battle(self, ctx: SlashContext, a: Entity, b: Entity, user_b_id: Optional[int] = None) -> None:
        battle: Battle = Battle(a, b, user_b_id)
        self.stat_being_to_battle[a] = battle
        self.stat_being_to_battle[b] = battle
        log = f"⚔️ Battle between {a.get_name()} and {b.get_name()}!\n" + battle.pop_log()
        if len(log) > 0:
            await ctx.send(log)
            await battle.init(ctx.message)

    def end_battle(self, battle: Battle) -> None:
        a = battle.entity_a
        b = battle.entity_b
        del self.stat_being_to_battle[a]
        del self.stat_being_to_battle[b]

    def get_battle(self, user: User) -> Optional[Battle]:
        return self.stat_being_to_battle.get(user.entity)
