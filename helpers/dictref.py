from typing import Generic, TypeVar, Any, Optional

from autoslot import Slots

T = TypeVar('T')


class DictRef(Generic[T], Slots):
    def __init__(self, dictionary: dict[Any, T], key: Any):
        self.dictionary: dict[Any, T] = dictionary
        self.key: Any = key

    def try_get(self) -> Optional[T]:
        return self.dictionary.get(self.key)

    def delete(self) -> None:
        del self.dictionary[self.key]

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
