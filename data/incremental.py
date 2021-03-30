# Imports
from enum import Enum, unique

from autoslot import Slots

import utils


# Time metric enum
@unique
class TimeMetric(Enum):
    SECOND = 1,
    MINUTE = 2,
    HOUR = 3,
    DAY = 4

    def seconds(self, amount: int = 1):
        if self == TimeMetric.SECOND:
            return amount
        elif self == TimeMetric.MINUTE:
            return amount * 60
        elif self == TimeMetric.HOUR:
            return amount * 3600
        else:
            return amount * 86400

    def abbreviation(self):
        if self == TimeMetric.SECOND:
            return 'sec'
        elif self == TimeMetric.MINUTE:
            return 'min'
        elif self == TimeMetric.HOUR:
            return 'hour'
        else:
            return 'day'


class Incremental(Slots):
    def __init__(self, base_ref: utils.DictRef, time_ref: utils.DictRef, metric: TimeMetric, increment: int):
        self._base_ref = base_ref
        self._time_ref = time_ref
        self._metric = metric
        self._increment = increment

    def get(self, override_now: int = None) -> int:
        if override_now is None:
            override_now = utils.now()
        q, mod = divmod(override_now - self._time_ref.get(), self._metric.seconds())
        whole = q * self._increment + int((float(mod) / self._metric.seconds()) * self._increment)
        return whole + self._base_ref.get()

    def change(self, amount: int, override_now: int = None) -> None:
        if override_now is None:
            override_now = utils.now()
        self.set(self.get(override_now) + amount, override_now)

    def set(self, amount: int, override_now: int = None) -> None:
        if override_now is None:
            override_now = utils.now()
        current = self.get(override_now) - self._base_ref.get()
        last_whole = self._time_ref.get() + round(current / (self._increment / self._metric.seconds()))
        self._time_ref.set(override_now - (override_now - last_whole))
        self._base_ref.set(amount)

    def set_increment(self, increment: int, override_now: int = None) -> None:
        self.set(self.get(override_now), override_now)
        self._increment = increment

    def print_rate(self) -> str:
        increment_str = utils.print_money(self._increment)
        return f"+{increment_str}/{self._metric.abbreviation()}"
