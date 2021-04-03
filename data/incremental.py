# Imports
from autoslot import Slots

import utils
from utils import DictRef, TimeSlot


class Incremental(Slots):
    def __init__(self, base_ref: DictRef, time_ref: DictRef, time_slot: TimeSlot):
        self._base_ref: DictRef = base_ref
        self._time_ref: DictRef = time_ref
        self._time_slot: TimeSlot = time_slot

    def get(self, override_now: int = None) -> int:
        if override_now is None:
            override_now = utils.now()
        q, mod = divmod(override_now - self._time_ref.get(), self._time_slot.metric_seconds())
        whole = q * self._time_slot.amount + int((float(mod) / self._time_slot.metric_seconds())
                                                 * self._time_slot.amount)
        return whole + self._base_ref.get()

    def change(self, amount: int, override_now: int = None) -> None:
        if override_now is None:
            override_now = utils.now()
        self.set(self.get(override_now) + amount, override_now)

    def set(self, amount: int, override_now: int = None) -> None:
        if override_now is None:
            override_now = utils.now()
        current = self.get(override_now) - self._base_ref.get()
        last_whole = self._time_ref.get() + round(current / (self._time_slot.amount / self._time_slot.metric_seconds()))
        self._time_ref.set(override_now - (override_now - last_whole))
        self._base_ref.set(amount)

    def set_absolute(self, amount: int, override_now: int = None) -> None:
        if override_now is None:
            override_now = utils.now()
        self._time_ref.set(override_now)
        self._base_ref.set(amount)

    def set_increment(self, increment: int, override_now: int = None) -> None:
        self.set(self.get(override_now), override_now)
        self._time_slot.amount = increment

    def print_rate(self) -> str:
        increment_str = utils.print_money(self._time_slot.amount)
        return f"+{increment_str}/{self._time_slot.metric_abbreviation()}"
