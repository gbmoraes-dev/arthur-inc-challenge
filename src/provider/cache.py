import json
import os
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast
import redis
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_EXPIRY = 3600


class CacheClient:
    _instance = None
    _redis: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheClient, cls).__new__(cls)
            try:
                cls._instance._redis = redis.Redis(
                    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
                )
            except redis.ConnectionError:
                cls._instance._redis = None
        return cls._instance

    def get(self, key: str) -> Any:
        if not self._redis:
            return None

        try:
            value = self._redis.get(key)
            if isinstance(value, (str, bytes, bytearray)):
                return json.loads(value)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, expiry: int = REDIS_EXPIRY) -> bool:
        if not self._redis:
            return False

        try:
            self._redis.setex(key, expiry, json.dumps(value))
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        if not self._redis:
            return False

        try:
            self._redis.delete(key)
            return True
        except Exception:
            return False

    def is_available(self) -> bool:
        if not self._redis:
            return False

        try:
            return bool(self._redis.ping())
        except Exception:
            return False


def cached(
    prefix: str, expiry: int = REDIS_EXPIRY
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            cache_client = CacheClient()

            if not cache_client.is_available():
                return func(*args, **kwargs)

            cache_key = f"{prefix}:{func.__name__}:"

            if (
                args
                and hasattr(args[0], "__class__")
                and args[0].__class__.__name__ in func.__qualname__
            ):
                key_args = args[1:]
            else:
                key_args = args

            args_str = str(key_args)
            kwargs_str = str(sorted(kwargs.items()))
            cache_key += f"{args_str}:{kwargs_str}"

            cached_result = cache_client.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)

            cache_client.set(cache_key, result, expiry)

            return result

        return cast(Callable[..., T], wrapper)

    return decorator
