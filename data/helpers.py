import utils, math
from utils import TimeMetric
from db.row import Row, DataChanges

"""
(value, cost)
"""

class IncrementalHelper:
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