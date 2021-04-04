from unittest import TestCase

from common.incremental import Incremental
from utils import DictRef, TimeSlot, TimeMetric


class TestIncremental(TestCase):
    def setUp(self) -> None:
        self.d = {
            'base': 5,
            'time': 0
        }
        self.inc = Incremental(DictRef(self.d, 'base'), DictRef(self.d, 'time'), TimeSlot(TimeMetric.MINUTE, 27))

    def test_get(self):
        expected = {
            24: 10,
            47: 21
        }
        base = self.d['base']
        for curr_time, v in expected.items():
            self.assertEqual(v + base, self.inc.get(curr_time))

    def test_set(self):
        tests = {
            24: (27, 27),
            47: (43, 43),
            1717: (847, 847)
        }
        for curr_time, v in tests.items():
            self.inc.set(v[0], curr_time)
            self.assertEqual(v[1], self.inc.get(curr_time))

    def test_set_increment(self):
        tests = {
            24: (10, 27),
            47: (75, 96),
            1717: (24238, 847)
        }
        for curr_time, v in tests.items():
            self.inc.set_increment(v[1], 0)
            self.assertEqual(v[0] + 5, self.inc.get(curr_time))
