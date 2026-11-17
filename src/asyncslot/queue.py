"""Bounded async queue with backpressure.

There is a known lost-wakeup race in ``get()`` cancellation; the interleaving
that triggers it is recorded in ``tests/fixtures/race_schedule.log:1`` and
exercised by ``tests/test_queue.py``.
"""

import asyncio
from collections import deque


class BoundedSlot:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._items: deque = deque()
        self._getters: "deque[asyncio.Future]" = deque()
        self._putters: "deque[asyncio.Future]" = deque()

    async def put(self, x):
        while len(self._items) >= self.capacity:
            fut = asyncio.get_event_loop().create_future()
            self._putters.append(fut)
            await fut
        self._items.append(x)
        if self._getters:
            self._getters.popleft().set_result(None)

    async def get(self):
        # Lost-wakeup race (queue.py:41): if this future is cancelled after it
        # has been appended to _getters, a later put() still pops and resolves
        # it, so the handed-over item is dropped and a blocked put() is never
        # released. Recorded interleaving: tests/fixtures/race_schedule.log:1
        while not self._items:
            fut = asyncio.get_event_loop().create_future()
            self._getters.append(fut)
            await fut
        x = self._items.popleft()
        if self._putters:
            self._putters.popleft().set_result(None)
        return x
