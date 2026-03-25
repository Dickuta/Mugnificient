import time
from functools import wraps
from typing import Callable, Any, Optional
import hashlib
import json


class Cache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            timestamp, value, ttl = self._cache[key]
            if time.time() - timestamp < ttl:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        self._cache[key] = (time.time(), value, ttl)

    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        self._cache.clear()

    def get_or_set(self, key: str, ttl: int, factory: Callable):
        cached = self.get(key)
        if cached is not None:
            return cached
        value = factory()
        self.set(key, value, ttl)
        return value


cache = Cache()


def cache_key(*args, **kwargs):
    """Generate a cache key from arguments"""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key_val = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            cached_result = cache.get(cache_key_val)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_key_val, result, ttl)
            return result

        return wrapper

    return decorator


def invalidate_cache(prefix: str = ""):
    """Invalidate cache entries with a specific prefix"""
    if not prefix:
        cache.clear()
    else:
        keys_to_delete = [k for k in cache._cache.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            cache.delete(key)
