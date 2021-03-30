import utils
from data.bet import Bet
from data.incremental import Incremental, TimeMetric
from data.user import User
from db.row import Row
from utils import DictRef


class Guild(Row):
    TABLE_HYPE_DURATION = 60 * 60
    TABLE_INCREMENT = 3
    TABLE_MIN = 10

    def __init__(self, guild_id: int):
        super().__init__("guilds", dict(id=guild_id))
        self.id = guild_id
        self._table = Incremental(DictRef(self.data, 'table_money'), DictRef(self.data, 'table_money_time'),
                                  TimeMetric.MINUTE, Guild.TABLE_INCREMENT)
        self.bet = Bet(DictRef(self.data, 'ongoing_bet'), TimeMetric.MINUTE, 12)

    def load_defaults(self):
        return {
            'table_money': 0,  # bigint
            'table_money_time': utils.now(),  # bigint
            'ongoing_bet': {}  # json
        }

    def get_table(self) -> int:
        if self.data['table_money'] > 0:
            now = min(utils.now(), self.data['table_money_time'] + Guild.TABLE_HYPE_DURATION)
            return self._table.get(now)
        else:
            return 0

    def place_table(self, user: User, amount: int) -> bool:
        if user.remove_money(amount):
            self._table.change(amount)
            return True
        return False

    def retrieve_table(self, user: User) -> int:
        space = user.get_total_money_space()
        to_retrieve = min(self.get_table(), space)
        if to_retrieve == 0:
            return 0
        self._table.change(-to_retrieve)
        user.add_money(to_retrieve)
        return to_retrieve

    def print_table_rate(self) -> str:
        if utils.now() >= self.data['table_money_time'] + Guild.TABLE_HYPE_DURATION:
            return ""
        else:
            return self._table.print_rate()
