from db.row import Row
from data.helpers import IncrementalHelper
from commands.command import Command
from data import users
import utils, asyncio, random

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
        super().__init__("guilds", guild_id)
        self.table_money = IncrementalHelper(self.data, 'table_money', 'table_money_time', 15)
        self.bet_info_timestamp = 0

    def load_defaults(self):
        return {
            'table_money': 0, # bigint
            'table_money_time': utils.now(), # bigint
            'ongoing_bet': {} # json
        }

    def get_table_money(self):
        if self.data['table_money'] == 0:
            return 0
        return self.table_money.get()

    def place_table_money(self, amount: int):
        self.table_money.set(self.get_table_money() + amount)

    def take_table_money(self):
        self.table_money.set(0)

    def get_bet_info(self):
        if self.data['ongoing_bet']:
            s = self.data['ongoing_bet']['finish_time'] - utils.now()
            if s < 0:
                s = 0
            time_remaining_str = utils.print_time(s)
            lines = [f"Bet finishes in {time_remaining_str}"]
            bets = []
            total_bet = 0
            max_bet = 0
            for _, bet_data in self.data['ongoing_bet']['bets'].items():
                bets.append((bet_data[0], bet_data[1]))
                max_bet = max(max_bet, bet_data[1])
                total_bet += bet_data[1]
            bets.sort(key=lambda x: x[1], reverse=True)
            bot_bet = max_bet * 2
            total_bet += bot_bet
            total_bet_str = utils.print_money(total_bet)
            lines.append(f"**Jackpot**: {total_bet_str}")
            money_str = utils.print_money(bot_bet)
            lines.append(f"Bot: {money_str}")
            for b in bets:
                name = b[0]
                money_str = utils.print_money(b[1])
                lines.append(f"{name}: {money_str}")
            return '\n'.join(lines)
        else:
            return 'No ongoing bet currently'

    def start_bet(self):
        self.data['ongoing_bet'] = {
            'bets': {},
            'finish_time': utils.now() + 600
        }
        
    async def run_bet(self, cmd: Command):
        # 10 minute bet
        await asyncio.sleep(5 * 60)
        await cmd.send(self.get_bet_info())
        await asyncio.sleep(4 * 60)
        await cmd.send(self.get_bet_info())
        await asyncio.sleep(1 * 60)
        # Calculate result
        total_bet = 0
        user_ids = []
        weights = []
        max_bet = 0
        for user_id, bet_data in self.data['ongoing_bet']['bets'].items():
            user_ids.append(user_id)
            weights.append(bet_data[1])
            max_bet = max(max_bet, bet_data[1])
            total_bet += bet_data[1]
        user_ids.append('BOT')
        weights.append(max_bet * 2)
        winner_id = random.choices(user_ids, weights=weights, k=1)[0]
        result = [f"Bet finished!"]
        total_bet += max_bet * 2
        money_str = utils.print_money(total_bet)
        if winner_id == 'BOT':
            result.append(f"The bot won the jackpot! ({money_str}) Bad luck")
        else:
            name = self.data['ongoing_bet']['bets'][winner_id][0]
            result.append(f"{name} won the jackpot! ({money_str})")
            user = users.get(winner_id)
            user.change_money(total_bet)
        await cmd.send('\n'.join(result))
        self.data['ongoing_bet'] = {}

    def update_last_bet_info(self):
        if utils.now() - self.bet_info_timestamp > 10:
            self.bet_info_timestamp = utils.now()
            return True
        return False

    def check_bet(self):
        return bool(self.data['ongoing_bet'])

    def set_bet(self, user_id: int, user_name: str, amount: int):
        self.data['ongoing_bet']['bets'][user_id] = (user_name, amount)

    def get_bet(self, user_id: int):
        bets = self.data['ongoing_bet']['bets']
        return bets.get(user_id, (0,0))[1]