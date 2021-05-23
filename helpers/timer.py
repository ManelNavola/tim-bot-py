import asyncio
from asyncio import Event

from helpers.observable import Observable


class WaitUntil:
    def __init__(self, timeout):
        self._timeout = timeout
        self._task = asyncio.ensure_future(self._job())
        self._running = True
        self._was_completed = False
        self._wait_event: Event = Event()
        self.on_timer_finish: Observable = Observable()

    def is_running(self):
        return self._running

    async def _job(self):
        await asyncio.sleep(self._timeout)
        if self._running:
            self._running = False
            self._was_completed = True
            self._wait_event.set()

    def cancel(self):
        if self._running:
            self._running = False
            self._task.cancel()
            self._wait_event.set()

    async def wait(self) -> bool:
        await self._wait_event.wait()
        return self._was_completed
