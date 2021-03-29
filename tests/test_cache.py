from unittest import TestCase

from data.cache import Cache


class TestCache(TestCase):
    def test_setget(self):
        cache = Cache()
        cache['Test'] = 24
        self.assertIn('Test', cache)
        self.assertEqual(cache['Test'], 24)

    def test_clean(self):
        cache = Cache()
        # Fill cache
        for i in range(len(cache), cache.limit):
            cache[i] = 'Anything'
        self.assertEqual(len(cache), 100)
        # Overload cache
        cache['TooMany'] = 2
        self.assertEqual(len(cache), cache.limit - int(cache.limit * Cache.REMOVE_PCT) + 1)
