"""Retry utilities with exponential backoff."""

import logging
import time
import random
from typing import Callable, Any, Optional, Type
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class RetryPolicy:
    """Retry policy configuration."""

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt."""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt reset."""
        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


def with_retry(
    policy: Optional[RetryPolicy] = None,
    retry_on: tuple = (Exception,)
):
    """Decorator for retrying functions.
    
    Args:
        policy: Retry policy (uses default if None)
        retry_on: Tuple of exceptions to retry on
    
    Example:
        @with_retry(policy=RetryPolicy(max_attempts=5))
        def flaky_function():
            ...
    """
    if policy is None:
        policy = RetryPolicy()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(policy.max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e

                    if attempt < policy.max_attempts - 1:
                        delay = policy.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{policy.max_attempts} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {policy.max_attempts} attempts failed. Last error: {e}"
                        )

            # All attempts failed
            raise last_exception

        return wrapper

    return decorator
