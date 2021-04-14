# Imports
import math

from autoslot import Slots

import utils
from helpers.dictref import DictRef
from utils import TimeSlot


class Incremental(Slots):
    def __init__(self, base_ref: DictRef[int], time_ref: DictRef[int], time_slot: TimeSlot):
        self._base_ref: DictRef[int] = base_ref
        self._time_ref: DictRef[int] = time_ref
        self._time_slot: TimeSlot = time_slot
        self.check()

    def get(self, override_now: int = None) -> int:
        self.check()
        if override_now is None:
            override_now = utils.now()
        q, mod = divmod(override_now - self._time_ref.get(), self._time_slot.metric.seconds())
        whole = q * self._time_slot.amount + int((float(mod) / self._time_slot.metric.seconds())
                                                 * self._time_slot.amount)
        return whole + self._base_ref.get()

    def check(self):
        if self._time_ref.get() == -1:
            self._time_ref.set(utils.now())
        if self._base_ref.get() == -1:
            self._base_ref.set(0)

    def get_until(self, target: int, override_now: int = None) -> int:
        if override_now is None:
            override_now = utils.now()
        current: float = (override_now - self._time_ref.get()) / self._time_slot.metric.seconds()
        need: float = target - current * self._time_slot.amount
        if need <= 0:
            return 0
        f: float = float(self._time_slot.amount) / float(self._time_slot.metric.seconds())
        seconds_needed = math.ceil(float(need) / f)
        return seconds_needed

    def disable(self):
        self._time_ref.set(-1)

    def set(self, amount: int, override_now: int = None) -> None:
        self.check()
        if override_now is None:
            override_now = utils.now()
        self._time_ref.set(override_now)
        self._base_ref.set(amount)

    def set_increment(self, increment: int, override_now: int = None) -> None:
        self.check()
        self.set(self.get(override_now), override_now)
        self._time_slot.amount = increment

    def print_rate(self) -> str:
        self.check()
        increment_str = utils.print_money(self._time_slot.amount)
        return f"+{increment_str}/{self._time_slot.metric_abbreviation()}"
