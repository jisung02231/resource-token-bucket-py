import time


class TokenBucket:
    """A token bucket that refills at a fixed rate and consumes tokens on demand.

    The bucket starts full with ``capacity`` tokens. Tokens are added at
    ``refill_rate`` tokens per second up to the capacity. Each call to
    :meth:`consume` attempts to remove ``amount`` tokens; it returns ``True``
    if enough tokens were available, otherwise ``False`` and the bucket is
    left unchanged.

    Time is measured with ``time.monotonic`` by default so that wall-clock
    adjustments cannot affect the refill logic. A custom clock function can be
    supplied for deterministic testing.
    """

    def __init__(self, capacity, refill_rate, *, initial_tokens=None, clock=None):
        """Create a token bucket.

        :param capacity: Maximum number of tokens the bucket can hold. Must be
            a positive number.
        :param refill_rate: Tokens added per second. Must be a positive number.
        :param initial_tokens: Starting token count. Defaults to ``capacity``.
            Must be between 0 and ``capacity`` inclusive.
        :param clock: A callable returning a monotonically increasing number of
            seconds. Defaults to ``time.monotonic``.
        """
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        if initial_tokens is None:
            initial_tokens = capacity
        if initial_tokens < 0 or initial_tokens > capacity:
            raise ValueError("initial_tokens must be between 0 and capacity")

        self._capacity = float(capacity)
        self._refill_rate = float(refill_rate)
        self._tokens = float(initial_tokens)
        self._clock = clock if clock is not None else time.monotonic
        self._last_refill = self._clock()

    @property
    def capacity(self):
        """Maximum number of tokens the bucket can hold."""
        return self._capacity

    @property
    def refill_rate(self):
        """Tokens added per second."""
        return self._refill_rate

    @property
    def tokens(self):
        """Current number of tokens, after accounting for elapsed time."""
        self._refill()
        return self._tokens

    def _refill(self):
        now = self._clock()
        elapsed = now - self._last_refill
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
            self._last_refill = now

    def consume(self, amount=1):
        """Try to remove ``amount`` tokens.

        Returns ``True`` and removes the tokens if enough are available,
        otherwise returns ``False`` and leaves the bucket unchanged.

        :param amount: Number of tokens to consume. Must be non-negative.
        """
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self._refill()
        if amount > self._tokens:
            return False
        self._tokens -= amount
        return True

    def peek(self, amount=1):
        """Return ``True`` if ``amount`` tokens could be consumed right now.

        This does not modify the bucket.
        """
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self._refill()
        return amount <= self._tokens
