import asyncio

import pytest

from asyncslot import BoundedSlot


@pytest.mark.asyncio
async def test_cancelled_get_then_put_does_not_wedge():
    # Minimal interleaving recorded in tests/fixtures/race_schedule.log:1
    q = BoundedSlot(1)
    g = asyncio.ensure_future(q.get())
    await asyncio.sleep(0)
    g.cancel()
    await q.put(1)
    assert await asyncio.wait_for(q.get(), 1) == 1
