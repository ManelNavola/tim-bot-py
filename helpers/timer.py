import asyncio


class DelayTask:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())
        self._running = True

    def is_running(self):
        return self._running

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        if self._running:
            self._task.cancel()
            self._running = False
