# asyncslot

A tiny bounded async queue for `asyncio`, with backpressure: producers block on
`put()` when the queue is full, consumers block on `get()` when it is empty.

```python
from asyncslot import BoundedSlot

q = BoundedSlot(capacity=8)
await q.put(item)
item = await q.get()
```

## Known issue

There is a lost-wakeup race in `get()` cancellation: if a waiting `get()` is
cancelled in the same tick a `put()` hands it an item, the producer's slot is
never released and the queue can wedge. The minimal interleaving that reproduces
it is recorded in `tests/fixtures/race_schedule.log:1`, and `tests/test_queue.py`
turns that interleaving into a failing test. The defect itself is at
`src/asyncslot/queue.py:28`.

## License

MIT.
