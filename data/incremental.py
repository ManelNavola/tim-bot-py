# Imports
from enum import Enum, unique
from dataclasses import dataclass

from autoslot import Slots

from db.row import DataChanges
import utils


# Time metric enum
@unique
class TimeMetric(Enum):
    SECOND = 1,
    MINUTE = 2,
    HOUR = 3,
    DAY = 4

    def seconds(self):
        if self.value == TimeMetric.SECOND:
            return 1
        elif self.value == TimeMetric.MINUTE:
            return 60
        elif self.value == TimeMetric.HOUR:
            return 3600
        else:
            return 86400

    def abbreviation(self):
        if self.value == TimeMetric.SECOND:
            return 'sec'
        elif self.value == TimeMetric.MINUTE:
            return 'min'
        elif self.value == TimeMetric.HOUR:
            return 'hour'
        else:
            return 'day'


@dataclass
class Incremental(Slots):
    _base_ref: utils.DictRef
    _time_ref: utils.DictRef
    _metric: TimeMetric
    _increment: int

    def get(self) -> int:
        q, mod = divmod(utils.now() - self._time_ref.get(), self._metric.seconds())
        whole = q * self._increment + int((mod / self._metric.seconds()) * self._increment)
        return whole + self._base_ref.get()

    def change(self, amount: int):
        self.set(self.get() + amount)

    def set(self, amount: int):
        mod = (utils.now() - self._time_ref.get()) % self._metric.seconds()
        self._time_ref.set(utils.now() + mod)
        self._base_ref.set(amount)

    def set_increment(self, increment: int):
        self.set(self.get())
        self._increment = increment
