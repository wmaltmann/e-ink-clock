import uasyncio as asyncio

class Queue:
    def __init__(self, maxsize=50):
        self._queue = []
        self._set = set()
        self._maxsize = maxsize
        self._get_event = asyncio.Event()

    def put_nowait(self, item):
        if item in self._set:
            return  # skip duplicates
        if len(self._queue) >= self._maxsize:
            raise OverflowError("Queue full")
        self._queue.append(item)
        self._set.add(item)
        self._get_event.set()

    async def get_all(self):
        while not self._queue:
            self._get_event.clear()
            await self._get_event.wait()
        items = list(self._queue)
        self._queue.clear()
        self._set.clear()
        return items

    def empty(self):
        return len(self._queue) == 0
