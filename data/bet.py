import asyncio
import math
import random

from discord_slash import SlashContext

import utils
from data import storage
from data.incremental import TimeMetric
from data.user import User
from utils import DictRef


def create_bot(bot_name: str, limit: int):
    if bot_name == 'sunglasses':
        return Sunglasses(limit)
    elif bot_name == 'cowboy':
        return Cowboy(limit)
    elif bot_name == 'robot':
        return Robot(limit)


class Bet:
    DURATION = TimeMetric.MINUTE.seconds() * 10
    INFO_DELAY = 30
    MIN_BET = 50
    MIN_INCR = 10
    BOT_POOL = [
        (1000, ['sunglasses', 'cowboy', 'robot']),
        (10000, ['robot', 'sunglasses', 'cowboy']),
        (999999999999, ['robot', 'sunglasses', 'cowboy'])
    ]

    def __init__(self, bet_ref: DictRef, metric: TimeMetric, duration: int):
        self._bet_ref = bet_ref
        self._duration = metric.seconds() * duration
        self._info_changed = False
        self._stored_info = None
        self._bot: BetBot
        self._limit: int = 0
        if self.is_active():
            for user_id, bet_data in self._bet_ref['bets'].items():
                # USER ID AS A KEY IN JSON IS SAVED AS A STRING! CAREFUL
                user = storage.get_user(int(user_id))
                user.add_money(bet_data[1])
            self._bet_ref.set({})

    def _start(self, ctx: SlashContext, limit: int=1000):
        self._info_changed = True
        finish_time = utils.now() + Bet.DURATION
        pool = []
        for x in Bet.BOT_POOL:
            if limit <= x[0]:
                pool = x[1]
                break
        found = None
        i = 0
        while not found:
            if random.random() < 0.5:
                break
            i += 1
            if i == len(pool):
                i = 0
        self._bot = create_bot(pool[i], limit)
        self._limit = limit
        self._bet_ref.set({
            'bets': {},
            'finish_time': finish_time
        })
        asyncio.create_task(self._start_loop(ctx, finish_time))

    async def _start_loop(self, ctx: SlashContext, finish_time: int):
        await asyncio.sleep(Bet.DURATION - 120)  # X - 2 minutes
        if self.is_active() and self._bet_ref['finish_time'] == finish_time:
            await ctx.send(self.print())
        else:
            return
        await asyncio.sleep(120)  # 2 minutes

        if self.is_active() and self._bet_ref['finish_time'] == finish_time:
            await self.end_bet(ctx)

    def update_bet(self) -> None:
        self._bet_ref.set(self._bet_ref.get())

    async def end_bet(self, ctx: SlashContext) -> None:
        assert self.is_active(), "Cannot stop an inactive bet"
        user_ids = []
        weights = []
        for user_id, single_bet in self._bet_ref['bets'].items():
            user_ids.append(user_id)
            weights.append(single_bet[1])
        user_ids.append('BOT')
        weights.append(self._bot.get_bet())
        winner_id = random.choices(user_ids, weights=weights, k=1)[0]
        result = [f"~ Bet finished! ~"]
        total_bet = self.get_bet_sum() + self._bot.get_bet()
        money_str = utils.print_money(total_bet)
        if winner_id == 'BOT':
            result.append(f"{utils.emoji(self._bot.icon)} won the jackpot ({money_str}), bad luck!")
        else:
            name = self._bet_ref['bets'][winner_id][0]
            result.append(f"{name} won the jackpot! ({money_str})")
            user = storage.get_user(winner_id)
            user.add_money(total_bet)
        await ctx.send('\n'.join(result))
        self._bet_ref.set({})
        self._stored_info = None

    def print(self) -> str:
        s = max(self._bet_ref['finish_time'] - utils.now(), 0)
        time_remaining_str = utils.print_time(s)
        lines = [f"Bet finishes in {time_remaining_str}"]
        if self._info_changed:
            self._stored_info = []
            # Sort bet data
            total_bet = self.get_bet_sum() + self._bot.get_bet()
            bets = list(self._bet_ref['bets'].values())
            bets.append((utils.emoji(self._bot.icon), self._bot.get_bet()))
            bets.sort(key=lambda x: x[1], reverse=True)
            total_bet_str = utils.print_money(total_bet)
            # Jackpot
            self._stored_info.append(f"{utils.emoji('sparkle')} **Jackpot** {total_bet_str} {utils.emoji('sparkle')} "
                                     f"(Max. bet {utils.print_money(self._limit)})")
            # Player+bot bets
            for single_bet in bets:
                money_str = utils.print_money(single_bet[1])
                pct = single_bet[1] / total_bet
                self._stored_info.append(f"{single_bet[0]}: {money_str} ({pct:.0%})")

            self._info_changed = False
        return '\n'.join(lines + self._stored_info)

    def is_active(self) -> bool:
        return bool(self._bet_ref.get())

    def get_bet(self, user_id: int) -> int:
        assert self.is_active(), "Cannot get bet of an inactive bet"
        return self._bet_ref['bets'].get(user_id, ('', 0))[1]

    def get_bet_sum(self):
        assert self.is_active(), "Cannot get bet sum of an inactive bet"
        return sum([x[1] for x in self._bet_ref['bets'].values()])

    def get_bet_count(self):
        return len(self._bet_ref['bets'])

    def get_bet_max(self):
        return max([x[1] for x in self._bet_ref['bets'].values()])

    def add_bet(self, user: User, amount: int, ctx: SlashContext) -> tuple:
        if user.get_money() >= amount:
            if not self.is_active():
                self._start(ctx, amount * 10)
            self._info_changed = True
            single_bet = self._bet_ref['bets'].get(user.id)
            if single_bet:
                single_bet = (user.get_name(), single_bet[1] + amount, single_bet[2])
            else:
                single_bet = (user.get_name(), amount, amount)
            if single_bet[1] > self._limit:
                return False, self._limit
            user.remove_money(amount)
            self._bet_ref['bets'][user.id] = single_bet

            # Bot time B)
            old_bet = self._bot.data['bet']
            self._bot.on_bet(amount, single_bet[1], single_bet[2], self)

            self.update_bet()
            if old_bet != self._bot.data['bet']:
                return True, (self._bot.data['bet'], utils.emoji(self._bot.icon))
            else:
                return True, None
        return False, None


class BetBot:
    def __init__(self, icon: str, limit: int):
        self.icon = icon
        self.limit = limit
        self.data = {
            'bet': 0
        }

    def increase_bet(self, amount: int) -> None:
        self.data['bet'] += amount

    def increase_bet_to(self, amount: int) -> None:
        if self.data['bet'] < amount:
            self.data['bet'] = amount

    def get_bet(self) -> int:
        return self.data['bet']

    def on_bet(self, increment: int, total: int, first_bet: int, bet: Bet) -> None:
        pass


class Cowboy(BetBot):
    def __init__(self, limit: int):
        super().__init__('cowboy', limit)
        self.brave = 0
        self.limit = limit

    def on_bet(self, increment: int, total: int, first_bet: int, bet: Bet) -> None:
        if total == first_bet:
            if random.randint(0, 1) == 0:
                self.brave += 1
        increase_to = int(bet.get_bet_sum() * math.sqrt(bet.get_bet_count()) * (0.8 + random.random() / 5))
        limit_pct = min((0.75 + 0.1 * self.brave), 2)
        limit = int(self.limit * limit_pct)
        if increment < (total - increment) * 0.5:
            increase_to = max(increase_to, bet.get_bet_sum() + increment * (0.8 + random.random() / 3))
        self.increase_bet_to(min(increase_to, limit))


class Sunglasses(BetBot):
    def __init__(self, limit: int):
        super().__init__('sunglasses', limit)
        self.scared = 0
        self.limit = limit

    def on_bet(self, increment: int, total: int, first_bet: int, bet: Bet) -> None:
        if total == first_bet:
            if random.randint(0, 1) == 0:
                self.scared += 1
        increase_to = int((bet.get_bet_sum() * (0.9 + random.random() * 0.2)) / (float(self.scared) / 2 + 1))
        limit_pct = 2
        limit = int(self.limit * limit_pct)
        if increment < bet.get_bet_max() * 0.5:
            increase_to = max(increase_to, bet.get_bet_sum() + increment * (1.5 + random.random() / 0.5))
        elif increment < bet.get_bet_max() * 0.75:
            if random.randint(0, 1) == 0:
                increase_to = max(increase_to, bet.get_bet_sum() + increment * (1 + random.random()))
        self.increase_bet_to(min(increase_to, limit))


class Robot(BetBot):
    def __init__(self, limit: int):
        super().__init__('robot', limit)
        self.scared = 0
        self.limit = limit
        self.limit_pct = 1
        self.happened = 0

    def on_bet(self, increment: int, total: int, first_bet: int, bet: Bet) -> None:
        if total == first_bet:
            if random.randint(0, 1) == 0:
                self.scared += 1
        increase_to = int(bet.get_bet_max() * (1.9 + random.random() * 0.2))
        if total > first_bet * 5:
            self.limit_pct += 0.5 / (self.happened + 1)
            self.happened += 1
        limit = int(self.limit * self.limit_pct)

        self.increase_bet_to(min(increase_to, limit))
