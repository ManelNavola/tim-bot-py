# Imports
from autoslot import Slots

import utils
from helpers.dictref import DictRef
from helpers.translate import tr
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
        partial: int = int((float(mod) / self._time_slot.metric.seconds()) * self._time_slot.amount)
        whole: int = q * self._time_slot.amount
        return whole + partial + self._base_ref.get()

    def _get_fraction(self, override_now: int):
        diff: int = override_now - self._time_ref.get()
        return diff % self._time_slot.metric.seconds()

    def get_base(self):
        return self._base_ref.get()

    def check(self):
        if self._time_ref.get() == -1:
            self._time_ref.set(utils.now())
        if self._base_ref.get() == -1:
            self._base_ref.set(0)

    def get_until(self, target: int, override_now: int = None) -> int:
        if override_now is None:
            override_now = utils.now()

        need: int = target - self.get(override_now)
        if need <= 0:
            return 0

        seconds_per_one: float = float(self._time_slot.metric.seconds()) / self._time_slot.amount
        fraction_time: int = self._get_fraction(override_now)
        last_whole_time: int = override_now - fraction_time
        at_whole_time: int = self.get(last_whole_time)
        target_time: int = last_whole_time + int(seconds_per_one * (target - at_whole_time))

        return target_time - fraction_time - override_now

    def disable(self):
        self._time_ref.set(-1)

    def set(self, amount: int, override_now: int = None) -> None:
        self.check()
        if override_now is None:
            override_now = utils.now()
        self._time_ref.set(override_now - self._get_fraction(override_now))
        self._base_ref.set(amount)

    def set_increment(self, increment: int, override_now: int = None) -> None:
        self.check()
        self.set(self.get(override_now), override_now)
        self._time_slot.amount = increment

    def print_rate(self, lang: str) -> str:
        self.check()
        increment_str = utils.print_money(lang, self._time_slot.amount)
        return f"+{tr(lang, 'MISC.RATE', amount=increment_str, time=self._time_slot.metric_abbreviation(lang))}"
