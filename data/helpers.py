import utils, math
from utils import TimeMetric
from db.row import Row

"""
(value, cost)
"""

class UpgradeHelper():
    # Help me
    def __init__(self, name:str, upgrades: dict, current_level: int=0):
        self.name = name
        self.upgrades = upgrades
        self.level = current_level

    def get_value(self, override_level: int=None):
        if not override_level:
            override_level = self.level
        return self.upgrades[override_level][0]

    def get_next_value(self):
        if self.level + 1 in self.upgrades:
            return self.upgrades[self.level + 1][0]
        else:
            return None
    
    def get_cost(self):
        if self.level + 1 in self.upgrades:
            return self.upgrades[self.level + 1][1]
        else:
            return None

    def clone(self, level:int):
        return UpgradeHelper(self.name, self.upgrades, level)

class IncrementalHelper():
    def __init__(self, d: dict, base_field: str, time_field: str, every: TimeMetric, amount: int):
        self.dictionary = d
        self.base_field = base_field
        self.time_field = time_field
        self.second_increment = math.ceil(utils.metric_to_seconds(every) / amount)
        amount_str = utils.print_money(amount)
        metric_str = utils.metric_to_abv(every)
        self.rate_str = f"+{amount_str}/{metric_str}"
        self.limit = None
        self.every = every

    def get(self):
        diff = None
        if self.limit:
            diff = (min(self.limit, utils.now()) - self.dictionary[self.time_field])
        else:
            diff = (utils.now() - self.dictionary[self.time_field])
        if diff < 0:
            diff = 0
        return self.dictionary[self.base_field] + diff // self.second_increment

    def set(self, value: int):
        self.dictionary[self.base_field] = value
        self.dictionary[self.time_field] = utils.now()

    def set_limit(self, limit: int):
        self.limit = limit

    def set_increment(self, every: TimeMetric, amount: int):
        self.set(self.get())
        self.second_increment = int(utils.metric_to_seconds(every) / amount)
        amount_str = utils.print_money(amount)
        metric_str = utils.metric_to_abv(every)
        self.rate_str = f"+{amount_str}/{metric_str}"

    def change(self, value: int):
        self.set(self.get() + value)