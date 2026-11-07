"""Small resilience helpers used by internal services."""
import functools
import random
import time


def retry(times=3, delay=1.0, backoff=2.0, jitter=0.1, exceptions=(Exception,)):
    """Retry a function with exponential backoff and a little random jitter."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    time.sleep(wait + random.uniform(0, jitter))
                    wait *= backoff

        return wrapper

    return decorator


class CircuitBreaker:
    """Stop calling a failing dependency for a cool-down period."""

    def __init__(self, max_failures=5, reset_after=30.0):
        self.max_failures = max_failures
        self.reset_after = reset_after
        self.failures = 0
        self.opened_at = None

    def call(self, func, *args, **kwargs):
        if self.opened_at and time.time() - self.opened_at < self.reset_after:
            raise RuntimeError("circuit open: dependency is cooling down")
        try:
            result = func(*args, **kwargs)
        except Exception:
            self.failures += 1
            if self.failures >= self.max_failures:
                self.opened_at = time.time()
            raise
        self.failures = 0
        self.opened_at = None
        return result


class PaymentClient:
    """Thin wrapper around the payments gateway."""

    @retry(times=4, delay=0.5, exceptions=(TimeoutError,))
    def charge(self, order_id: str, amount: int) -> dict:
        return {"order_id": order_id, "amount": amount, "status": "charged"}

    @retry(times=3, delay=1.0, exceptions=(TimeoutError,))
    def refund(self, order_id: str, amount: int) -> dict:
        return {"order_id": order_id, "amount": amount, "status": "refund_pending"}
