import logging
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import pybreaker
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from exceptions import ExternalAPIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

brasil_api_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30,
    exclude=[ValueError, TypeError],
    name="brasil_api_breaker",
)

osrm_api_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30,
    exclude=[ValueError, TypeError],
    name="osrm_api_breaker",
)


def with_retry(
    max_attempts: int = 3, min_wait: float = 1.0, max_wait: float = 10.0
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return retry(
                    stop=stop_after_attempt(max_attempts),
                    wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
                    retry=retry_if_exception_type(requests.RequestException),
                    reraise=True,
                )(func)(*args, **kwargs)
            except RetryError as e:
                raise ExternalAPIError(
                    f"Service unavailable after {max_attempts} attempts"
                ) from e

        return cast(F, wrapper)

    return decorator


def log_circuit_open(breaker: pybreaker.CircuitBreaker) -> None:
    logger.warning(f"Circuit {breaker.name} OPEN: The service is unavailable")


def log_circuit_close(breaker: pybreaker.CircuitBreaker) -> None:
    logger.info(f"Circuit {breaker.name} CLOSED: The service is back online")


def log_circuit_half_open(breaker: pybreaker.CircuitBreaker) -> None:
    logger.info(f"Circuit {breaker.name} HALF-OPEN: The service is being tested")


class CircuitBreakerMonitor(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        if new_state.name == pybreaker.STATE_OPEN:
            log_circuit_open(cb)
        elif new_state.name == pybreaker.STATE_CLOSED:
            log_circuit_close(cb)
        elif new_state.name == pybreaker.STATE_HALF_OPEN:
            log_circuit_half_open(cb)

    def failure(self, cb, exc):
        logger.error(f"Circuit breaker {cb.name} failed with error: {exc}")

    def success(self, cb):
        logger.debug(f"Circuit breaker {cb.name} executed successfully")


monitor = CircuitBreakerMonitor()
brasil_api_breaker.add_listener(monitor)
osrm_api_breaker.add_listener(monitor)
