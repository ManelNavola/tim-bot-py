from typing import Generic, TypeVar

from autoslot import Slots

T = TypeVar('T')


class DictRef(Generic[T], Slots):
    def __init__(self, dictionary: dict, key: str):
        self.dictionary = dictionary
        self.key = key

    def get(self) -> T:
        return self.dictionary[self.key]

    def get_update(self):
        self._update()
        return self.dictionary[self.key]

    def __getitem__(self, key):
        return self.dictionary[self.key][key]

    def set(self, value: T):
        self.dictionary[self.key] = value

    def __setitem__(self, key, value):
        self.dictionary[self.key][key] = value
        self._update()

    def _update(self):
        self.set(self.get())
