import unittest

from resource_token_bucket_py import TokenBucket


class FakeClock:
    def __init__(self, start=0.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TestTokenBucket(unittest.TestCase):
    def test_starts_full(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=10, refill_rate=1, clock=clock)
        self.assertEqual(bucket.tokens, 10)
        self.assertEqual(bucket.capacity, 10)
        self.assertEqual(bucket.refill_rate, 1)

    def test_initial_tokens_override(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, initial_tokens=3, clock=clock)
        self.assertEqual(bucket.tokens, 3)

    def test_consume_reduces_tokens(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, clock=clock)
        self.assertTrue(bucket.consume(3))
        self.assertEqual(bucket.tokens, 7)

    def test_consume_fails_when_insufficient(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, initial_tokens=2, clock=clock)
        self.assertFalse(bucket.consume(3))
        self.assertEqual(bucket.tokens, 2)

    def test_refill_after_time(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 2, initial_tokens=0, clock=clock)
        clock.advance(1.5)
        self.assertEqual(bucket.tokens, 3)
        self.assertTrue(bucket.consume(3))
        self.assertEqual(bucket.tokens, 0)

    def test_refill_caps_at_capacity(self):
        clock = FakeClock()
        bucket = TokenBucket(5, 10, initial_tokens=0, clock=clock)
        clock.advance(100)
        self.assertEqual(bucket.tokens, 5)

    def test_peek_does_not_modify(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, clock=clock)
        self.assertTrue(bucket.peek(10))
        self.assertEqual(bucket.tokens, 10)
        self.assertFalse(bucket.peek(11))
        self.assertEqual(bucket.tokens, 10)

    def test_consume_zero_always_succeeds(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, initial_tokens=0, clock=clock)
        self.assertTrue(bucket.consume(0))
        self.assertEqual(bucket.tokens, 0)

    def test_consume_negative_raises(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, clock=clock)
        with self.assertRaises(ValueError):
            bucket.consume(-1)

    def test_peek_negative_raises(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, clock=clock)
        with self.assertRaises(ValueError):
            bucket.peek(-1)

    def test_constructor_validation(self):
        clock = FakeClock()
        with self.assertRaises(ValueError):
            TokenBucket(0, 1, clock=clock)
        with self.assertRaises(ValueError):
            TokenBucket(10, 0, clock=clock)
        with self.assertRaises(ValueError):
            TokenBucket(10, 1, initial_tokens=-1, clock=clock)
        with self.assertRaises(ValueError):
            TokenBucket(10, 1, initial_tokens=11, clock=clock)

    def test_elapsed_time_accumulates_across_calls(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 1, initial_tokens=0, clock=clock)
        clock.advance(0.5)
        self.assertEqual(bucket.tokens, 0.5)
        clock.advance(0.5)
        self.assertEqual(bucket.tokens, 1.0)
        self.assertTrue(bucket.consume(1))
        self.assertEqual(bucket.tokens, 0)

    def test_fractional_refill(self):
        clock = FakeClock()
        bucket = TokenBucket(10, 0.5, initial_tokens=0, clock=clock)
        clock.advance(1)
        self.assertEqual(bucket.tokens, 0.5)
        self.assertFalse(bucket.consume(1))
        clock.advance(1)
        self.assertEqual(bucket.tokens, 1.0)
        self.assertTrue(bucket.consume(1))


if __name__ == "__main__":
    unittest.main()
