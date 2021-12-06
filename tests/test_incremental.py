import random
from unittest import TestCase

from typing import Dict

from helpers.dictref import DictRef
from helpers.incremental import Incremental
from utils import TimeSlot, TimeMetric


class TestIncremental(TestCase):
    def setUp(self) -> None:
        self.d: Dict[str, int] = {
            'base': random.randint(100, 10000),
            'time': random.randint(100, 10000),
        }
        self.inc: Incremental = Incremental(DictRef(self.d, 'base'), DictRef(self.d, 'time'),
                                            TimeSlot(TimeMetric.MINUTE, 27))

    def test_get(self):
        base_time: int = self.d['time']
        base_value: int = self.d['base']
        for i in range(10000):
            change: int = int((float(i) / self.inc._time_slot.metric.seconds()) * self.inc._time_slot.amount)
            self.assertLess(abs(self.inc.get(base_time + i) - base_value - change), 2)

    def test_set(self):
        self.dc = self.d.copy()
        base_time: int = self.d['time']
        base_value: int = self.d['base']
        self.inc.set(base_value, base_time)
        self.assertEqual(self.inc.get(base_time), base_value)
        for i in range(10000):
            rand_inc: int = random.randint(1, 100000)
            self.inc.set(base_value + rand_inc, base_time)
            self.assertEqual(self.inc.get(base_time), base_value + rand_inc)

        self.d = self.dc
        for i in range(1000):
            self.dc = self.d.copy()

            rand_inc: int = random.randint(1, 100000)
            self.inc.set(base_value + rand_inc, base_time)
            self.assertEqual(self.inc.get(base_time), base_value + rand_inc)

            rand_wait: int = random.randint(1000, 100000)
            change: int = int((float(rand_wait) / self.inc._time_slot.metric.seconds()) * self.inc._time_slot.amount)
            self.assertLess(abs(self.inc.get(base_time + rand_wait) - base_value - change - rand_inc), 2)

            self.d = self.dc
