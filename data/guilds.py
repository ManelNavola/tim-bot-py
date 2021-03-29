from db.row import Row, changes
from data.helpers import IncrementalHelper
from commands.command import Command
from data import users
import utils, asyncio, random
from utils import TimeMetric
from collections import namedtuple

HYPE_DURATION = 60 * 60
TABLE_INCREMENT = 3

cache = {}

def get(guild_id: int, create=True):
    if guild_id in cache:
        return cache[guild_id]
    else:
        user = Guild(guild_id)
        cache[guild_id] = user
        try_cleanup()
        return user

def try_cleanup():
    pass

class Guild(Row):
    def __init__(self, guild_id: int):
        super().__init__("guilds", dict(id=guild_id))
        self.table_money = IncrementalHelper(self.data, 'table_money', 'table_money_time',
            TimeMetric.MINUTE, TABLE_INCREMENT)
        self.bet_info_timestamp = 0
        self.rollback_check()
        if utils.is_test():
            if self.data['ongoing_bet']:
                self.data['ongoing_bet']['bets'] = {int(k): v for k, v in self.data['ongoing_bet']['bets'].items()}

    @changes('ongoing_bet')
    def rollback_check(self):
        if self.data['ongoing_bet']:
            if self.data['ongoing_bet']['finish_time'] < utils.now():
                for user_id, bet_data in self.data['ongoing_bet']['bets'].items():
                    user = users.get(user_id)
                    user.change_money(bet_data[1])
                self.data['ongoing_bet'] = {}

    def load_defaults(self):
        return {
            'table_money': 0, # bigint
            'table_money_time': 0, # bigint
            'ongoing_bet': {} # json
        }

    def get_table_money(self):
        if self.data['table_money'] == 0:
            return 0
        return self.table_money.get()

    @changes('table_money', 'table_money_time')
    def place_table_money(self, amount: int):
        self.table_money.set(self.get_table_money() + amount)
        self.table_money.set_limit(utils.now() + HYPE_DURATION)

    @changes('table_money')
    def take_table_money(self):
        self.table_money.set(0)

    def get_table_rate(self):
        if utils.now() > self.data['table_money_time'] + HYPE_DURATION:
            return None
        else:
            return self.table_money.rate_str

    def get_bet_info(self):
        if self.data['ongoing_bet']:
            s = self.data['ongoing_bet']['finish_time'] - utils.now()
            if s < 0:
                s = 0
            total_bet = self.data['ongoing_bet']['total_bet']
            bot_bet = self.data['ongoing_bet']['bot_bet']
            time_remaining_str = utils.print_time(s)
            lines = [f"Bet finishes in {time_remaining_str}"]
            bets = list(self.data['ongoing_bet']['bets'].values())
            bets.sort(key=lambda x: x[1], reverse=True)
            total_bet_str = utils.print_money(total_bet)
            lines.append(f"**Jackpot**: {total_bet_str}")
            money_str = utils.print_money(bot_bet)
            bot_bet_perc = bot_bet / total_bet
            lines.append(f"<Bot>: {money_str} ({bot_bet_perc:.0%})")
            for bet in bets:
                money_str = utils.print_money(bet[1])
                perc = bet[1] / total_bet
                lines.append(f"{bet[0]}: {money_str} ({perc:.0%})")
            return '\n'.join(lines)
        else:
            return 'No ongoing bet at the moment'

    @changes('ongoing_bet')
    def start_bet(self):
        self.data['ongoing_bet'] = {
            'bets': {},
            'finish_time': utils.now() + 60 * 10,
            'bot_bet': 0,
            'total_bet': 0
        }
        
    async def run_bet(self, cmd: Command):
        # 10 minute bet
        await asyncio.sleep(8 * 60) # 8 minutes
        await cmd.send(self.get_bet_info())
        await asyncio.sleep(2 * 60) # 2 minutes

        # Calculate result
        user_ids = []
        weights = []
        for user_id, bet_data in self.data['ongoing_bet']['bets'].items():
            user_ids.append(user_id)
            weights.append(bet_data[1])
        user_ids.append('<Bot>')
        weights.append(self.data['ongoing_bet']['bot_bet'])
        winner_id = random.choices(user_ids, weights=weights, k=1)[0]
        result = [f"~ Bet finished! ~"]
        total_bet = self.data['ongoing_bet']['total_bet']
        money_str = utils.print_money(total_bet)
        if winner_id == '<Bot>':
            result.append(f"<Bot> won the jackpot ({money_str}), bad luck!")
        else:
            name = self.data['ongoing_bet']['bets'][winner_id][0]
            result.append(f"{name} won the jackpot! ({money_str})")
            user = users.get(winner_id)
            user.change_money(total_bet)
        self.data['ongoing_bet'] = {}
        self.register_changes('ongoing_bet')
        await cmd.send('\n'.join(result))

    def update_last_bet_info(self):
        if utils.now() - self.bet_info_timestamp > 10:
            self.bet_info_timestamp = utils.now()
            return True
        return False

    def check_ongoing_bet(self):
        return bool(self.data['ongoing_bet'])

    @changes('ongoing_bet')
    def add_bet(self, user_id: int, user_name: str, amount: int):
        print(user_id, user_name, amount)
        new_bet = self.get_bet(user_id) + amount
        self.data['ongoing_bet']['bets'][user_id] = (user_name, new_bet)
        self.data['ongoing_bet']['total_bet'] += amount
        if self.data['ongoing_bet']['bot_bet'] < new_bet * 2:
            self.data['ongoing_bet']['total_bet'] += new_bet * 2 - self.data['ongoing_bet']['bot_bet']
            self.data['ongoing_bet']['bot_bet'] = new_bet * 2
            return new_bet * 2
        return None

    def get_bet(self, user_id: int):
        bets = self.data['ongoing_bet']['bets']
        return bets.get(user_id, (None, 0))[1]