from db.row import Row, changes
from db import database
from data.helpers import IncrementalHelper, UpgradeHelper
from data.inventory import Inventory
import utils
from utils import TimeMetric
from commands.command import Command

cache = {}

MONEY_LIMIT = UpgradeHelper('Money Limit', {
    0: (5000, 0),
    1: (20000, 4000),
    2: (35000, 16000),
    3: (95000, 28000),
    4: (200000, 76000),
    5: (485000, 160000),
    6: (1085000, 388000),
    7: (2540000, 868000)
})

GARDEN = UpgradeHelper('Garden Production', {
    0: (50, 0),
    1: (80, 2000),
    2: (125, 4000),
    3: (150, 8000),
    4: (200, 16000),
    5: (300, 32000),
    6: (425, 64000),
    7: (575, 128000),
    8: (750, 256000),
    9: (950, 512000),
    10: (1175, 1024000)
})

BANK = UpgradeHelper('Bank Limit', {
    0: (500, 0),
    1: (1000, 3000),
    2: (3500, 7500),
    3: (7000, 12500),
    4: (12000, 25000),
    5: (25000, 125000),
    6: (50000, 250000),
    7: (100000, 500000)
})

INVENTORY = UpgradeHelper('Inventory Capacity', {
    0: (5, 0)
})

CURRENT_VERSION = 1

def get(user_id: int, create=True):
    if user_id in cache:
        return cache[user_id]
    else:
        if create or database.instance.get_row_data("users", user_id):
            user = User(user_id)
            cache[user_id] = user
            try_cleanup()
        else:
            return None
        return user

def try_cleanup():
    pass

class User(Row):
    def __init__(self, user_id: int):
        super().__init__("users", dict(id=user_id))
        self.upgrade_log = None
        self.check_upgrade(self.data['version'])
        self.user_id = user_id
        self.upgrades = {
            'garden': GARDEN.clone(self.data['garden_lvl']),
            'bank': BANK.clone(self.data['bank_lvl']),
            'money_limit': MONEY_LIMIT.clone(self.data['money_limit_lvl']),
            #'inventory': INVENTORY.clone(self.data['inventory_lvl'])
        }
        self.storage = IncrementalHelper(self.data, 'bank', 'bank_time',
            TimeMetric.HOUR, self.upgrades['garden'].get_value())
        
        # Fill inventory
        #slots = self.upgrades['inventory'].get_value()
        slots = 5
        items = None
        if utils.is_test():
            # DIRTY
            item_ids = set()
            for row in database.instance.data['user_items']:
                if row['user_id'] == user_id:
                    item_ids.add(row['item_id'])
            items = []
            for row in database.instance.data['items']:
                if row['id'] in item_ids:
                    items.append(row)
        else:
            database.instance.cursor.execute(f"SELECT I.* FROM users U INNER JOIN user_items UI ON U.id = UI.user_id INNER JOIN items I ON I.id = UI.item_id")
            items = database.instance.cursor.fetchmany(slots)
        self.inventory = Inventory(slots, items)

    def load_defaults(self):
        return {
            'money': 10, # bigint
            'last_name': 'Unknown', # text

            'bank': 0, # bigint
            'bank_time': utils.now(), # bigint

            'bank_lvl': 0, # smallint
            'money_limit_lvl': 0, # smallint
            'garden_lvl': 0, # smallint
            'inventory_lvl': 0, # smallint

            'version': CURRENT_VERSION # int
        }

    def get_name(self):
        return self.data['last_name']

    def get_money_limit(self):
        return self.upgrades['money_limit'].get_value()

    def get_bank_limit(self):
        return self.upgrades['bank'].get_value()

    def get_money(self):
        return self.data['money']
    
    def get_bank(self):
        return min(self.storage.get(), self.get_bank_limit())

    def transfer(self):
        if self.get_money_limit() >= self.get_money():
            return 'You cannot hold more money!'
        if self.get_bank() == 0:
            return 'Your bank is empty'
        needs = self.get_money_limit() - self.get_money()
        needs = min(needs, self.get_bank())
        self.change_money(needs)
        self.change_bank(-needs)
        bank_str = utils.print_money(needs)
        money_str = utils.print_money(self.get_money())
        return f"You took {bank_str} from the bank, and now have {money_str}"

    @changes('money')
    def change_money(self, amount: int):
        result = self.get_money() + amount
        if result < 0:
            return False
        if result > self.get_money_limit():
            if self.get_money() >= self.get_money_limit():
                # Overflow
                if amount > 0: # Add
                    result = self.get_money()
                    self.change_bank(amount)
                else: # Sub
                    result = self.get_money() + amount
            else:
                to_dep = result - self.get_money_limit()
                self.change_bank(to_dep)
            # Allow overflow if set from code
            result = max(self.get_money_limit(), result)
        self.data['money'] = result
        return True

    @changes('bank', 'bank_time')
    def change_bank(self, amount: int):
        result = self.get_bank() + amount
        if result < 0:
            return False
        if result > self.get_bank_limit():
            result = self.get_bank_limit()
        self.storage.set(result)
        return True

    def print_inventory(self, checking=None, private=False):
        lines = []
        money_str = utils.print_money(self.get_money())
        if checking:
            lines.append(f"{checking}'s profile:")
        if private:
            # Money
            limit_str = utils.print_money(self.upgrades['money_limit'].get_value())
            lines.append(f"**Money**: {money_str} / {limit_str}")
            # Bank
            money_str = utils.print_money(self.get_bank())
            limit_str = utils.print_money(self.upgrades['bank'].get_value())
            if self.get_bank() == self.get_bank_limit():
                lines.append(f"**Bank**: {money_str} / {limit_str}")
            else:
                lines.append(f"**Bank**: {money_str} / {limit_str} ({self.storage.rate_str})")
            # Inventory
            #lines.append(self.inventory.print())
        else:
            lines.append(f"**Money**: {money_str}")
            avg_lvl = sum([x.level for x in self.upgrades.values()]) + len(self.upgrades)
            avg_lvl /= len(self.upgrades)
            avg_lvl = int(avg_lvl)
            lines.append(f"**Average level**: {avg_lvl}")
        return '\n'.join(lines)

    @changes('version')
    def check_upgrade(self, current_version: int):
        self.upgrade_log = ["~ Upgraded Player ~"]
        if current_version == 0:
            # Upgrade to upgrade system
            current_money = self.data['money'] + (utils.now() - self.data['bank_time']) // 60
            real_money = self.data['money'] + (utils.now() - self.data['bank_time']) // 60
            real_money *= 0.8
            real_money = int(real_money)
            cut = MONEY_LIMIT.get_value(0)
            if real_money > cut:
                real_money = cut + (min(real_money, 10000) - cut)
            money_str = utils.print_money(current_money)
            new_money_str = utils.print_money(real_money)
            self.upgrade_log.append(f"Upgraded to version 1: {money_str} => {new_money_str}")
            self.data['money'] = real_money
            self.data['bank_time'] = utils.now()
            self.register_changes('money', 'bank_time')
        if len(self.upgrade_log) < 2:
            self.upgrade_log = None
        self.data['version'] = CURRENT_VERSION