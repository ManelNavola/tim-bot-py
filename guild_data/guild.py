import utils
from db.database import PostgreSQL
from helpers.dictref import DictRef
from helpers.incremental import Incremental
from db import database
from db.row import Row
from enums.emoji import Emoji
from guild_data.bet import Bet
from guild_data.shop import Shop
from user_data.user import User
from utils import TimeSlot, TimeMetric


class Guild(Row):
    TABLE_MIN: int = 10
    TABLE_HYPE: TimeSlot = TimeSlot(TimeMetric.MINUTE, 30)
    TABLE_INCREMENT: TimeSlot = TimeSlot(TimeMetric.MINUTE, 1)
    LEADERBOARD_TOP: int = 5
    SHOP_DURATION: TimeSlot = TimeSlot(TimeMetric.HOUR, 1)

    def __init__(self, db: PostgreSQL, guild_id: int):
        super().__init__(db, "guilds", dict(id=guild_id))
        self.id: int = guild_id
        self._box: Incremental = Incremental(DictRef(self._data, 'table_money'),
                                             DictRef(self._data, 'table_money_time'),
                                             Guild.TABLE_INCREMENT)
        self._lang: DictRef[str] = DictRef(self._data, 'lang')
        self.bet: Bet = Bet(db, DictRef(self._data, 'ongoing_bet'))
        self.registered_user_ids: set[int] = set(self._data['user_ids'])
        self.shop: Shop = Shop(db, DictRef(self._data, 'shop_time'), self.id)

    def get_lang(self) -> str:
        return self._lang.get()

    def set_lang(self, lang: str) -> None:
        self._lang.set(lang)

    def register_user_id(self, user_id: int) -> None:
        if user_id not in self.registered_user_ids:
            self._data['user_ids'] = self._data['user_ids'] + [user_id]
            self.registered_user_ids.add(user_id)

    def print_leaderboard(self) -> str:
        self._db.execute(f"SELECT last_name, money FROM users "
                         f"INNER JOIN guilds ON guilds.id = {self.id} "
                         f"AND users.id = ANY({database.convert_sql_value(list(self.registered_user_ids))}) "
                         f"ORDER BY money DESC "
                         f"LIMIT {Guild.LEADERBOARD_TOP}")
        users = self._db.get_cursor().fetchall()
        ld = [f"{Emoji.TROPHY} Top {Guild.LEADERBOARD_TOP} players:"]
        for i in range(len(users)):
            if i == 0:
                ld.append(f"{Emoji.FIRST_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            elif i == 1:
                ld.append(f"{Emoji.SECOND_PLACE} #{i + 1}: "
                          f"{users[i]['last_name']} - {utils.print_money(users[i]['money'])}")
            elif i == 2:
                ld.append(f"{Emoji.THIRD_PLACE} #{i + 1}: "
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

    # async def start_battle(self, ctx: SlashContext, user: User,
    #                        opponent_bot: Optional[BotEntity] = None, opponent_user: Optional[User] = None) -> None:
    #     assert (opponent_user is not None) or (opponent_bot is not None), "A battle must have an opponent!"
    #     ul: list[int] = [user.id]
    #     a: UserEntity = user.user_entity
    #     b: Entity
    #     if opponent_bot is not None:
    #         b = opponent_bot
    #     else:
    #         b = opponent_user.user_entity
    #         ul.append(opponent_user.id)
    #     battle: BattleInstance = BattleInstance(a, b)
    #     self.stat_being_to_battle[a] = battle
    #     self.stat_being_to_battle[b] = battle
    #     await ctx.send("BATTLE START!")
    #     await battle.init(self, ctx.message, ul)
    #
    # def end_battle(self, battle: BattleInstance) -> None:
    #     a = battle.battle_entity_a.entity
    #     b = battle.battle_entity_b.entity
    #     del self.stat_being_to_battle[a]
    #     del self.stat_being_to_battle[b]
    #
    # def get_battle(self, user: User) -> Optional[BattleInstance]:
    #     return self.stat_being_to_battle.get(user.user_entity)
