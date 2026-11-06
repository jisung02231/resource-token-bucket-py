# resource-token-bucket-py

A token bucket that refills at a fixed rate and consumes tokens on demand, returning booleans for flow control under load.

```python
from resource_token_bucket_py import TokenBucket

bucket = TokenBucket(capacity=10, refill_rate=2)

if bucket.consume():
    pass  # do work
else:
    pass  # back off
```

The bucket starts full. `consume(amount=1)` removes tokens and returns `True` if enough are available, otherwise `False` and the bucket is unchanged. `peek(amount=1)` answers the same question without consuming. `tokens` is a property that reports the current count after accounting for elapsed time.

## Why this exists

Rate limiting is usually a few lines of code until it is not: you need to refill lazily without a background thread, cap the refill at the bucket size, and keep the arithmetic correct when the clock jumps. This library keeps all of that in one small class with no dependencies. The trade-off is that it is not thread-safe. Adding a lock would make every consume call take a mutex even in single-threaded use, which is the common case for a per-request limiter. If you share a bucket across threads, wrap it yourself.

## The awkward edge

Time is measured with `time.monotonic` by default, so wall-clock adjustments do not affect refill. But tests that depend on real elapsed time are flaky. The constructor accepts a `clock` callable, and the test suite passes a fake clock that advances explicitly. If you inject your own clock, it must never go backwards; a backwards jump is treated as zero elapsed time.
