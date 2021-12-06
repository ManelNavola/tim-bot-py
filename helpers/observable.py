from typing import TypeVar, Generic, Callable, Set

T = TypeVar('T')


class Observable(Generic[T]):
    def __init__(self):
        self._observers: Set[Callable[[T], None]] = set()

    def __add__(self, other: Callable[[T], None]) -> 'Observable[Generic[T]]':
        self.register(other)
        return self

    def __sub__(self, other: Callable[[T], None]) -> 'Observable[Generic[T]]':
        self.unregister(other)
        return self

    def register(self, func: Callable[[T], None]) -> None:
        self._observers.add(func)

    def unregister(self, func: Callable[[T], None]) -> None:
        self._observers.remove(func)

    def unregister_all(self) -> None:
        self._observers.clear()

    def call(self, value: T = None):
        for func in self._observers:
            func(value)
