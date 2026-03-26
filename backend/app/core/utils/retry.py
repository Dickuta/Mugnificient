"""
Retry and Circuit Breaker utilities for external API calls
"""
import logging
from functools import wraps
from typing import Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        self.failures = 0
        self.state = "closed"
    
    def _on_failure(self):
        """Handle failed call"""
        self.failures += 1
        self.last_failure_time = __import__('time').time()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failures} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        import time
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout


def with_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to add retry logic to functions
    
    Usage:
        @with_retry(max_attempts=3)
        def call_external_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            reraise=True
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Circuit breaker instances for external services
payment_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
email_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
delivery_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)


def call_with_circuit_breaker(breaker: CircuitBreaker, func: Callable, *args, **kwargs) -> Any:
    """Execute function with circuit breaker protection"""
    return breaker.call(func, *args, **kwargs)
