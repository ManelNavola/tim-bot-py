from collections import UserDict

import utils


class Cache(UserDict):
    REMOVE_PCT: float = 0.2

    def __init__(self, d=None, limit: int = 100):
        super().__init__(d)
        self.limit = limit

    def try_clean(self):
        k_v = list(self.data.items())
        k_v.sort(key=lambda x: x[1][1])
        for k in range(int(self.limit * Cache.REMOVE_PCT)):
            del self.data[k]

    def clear_all(self):
        self.data.clear()

    def __setitem__(self, key: object, value: object):
        super().__setitem__(key, (value, utils.now()))
        if len(self.data) > self.limit:
            self.try_clean()

    def __getitem__(self, key: object):
        cached_item = super().__getitem__(key)
        if cached_item:
            cached_item = (cached_item[0], utils.now())
            return cached_item[0]
        return cached_item

    def get(self, key: object, default_value=None):
        return self.data.get(key, (default_value,))[0]
