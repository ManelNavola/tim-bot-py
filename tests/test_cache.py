from unittest import TestCase

from helpers.storage import Cache


class TestCache(TestCase):
    def test_setget(self):
        cache = Cache()
        cache['Test'] = 24
        self.assertIn('Test', cache)
        self.assertEqual(24, cache['Test'])

    def test_clean(self):
        cache = Cache()
        # Fill cache
        for i in range(len(cache), cache.limit):
            cache[i] = 'Anything'
        self.assertEqual(100, len(cache))
        # Overload cache
        cache['TooMany'] = 2
        self.assertEqual(cache.limit - int(cache.limit * Cache.REMOVE_PCT) + 1, len(cache))
