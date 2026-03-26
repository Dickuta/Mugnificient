"""
Redis caching module with in-memory fallback
"""
import os
import json
import logging
import time
from functools import wraps
from typing import Callable, Any, Optional
import hashlib

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
USE_REDIS = os.getenv("USE_REDIS", "true").lower() == "true"

# Default cache TTL (seconds)
DEFAULT_TTL = 300


class InMemoryCache:
    """In-memory cache fallback"""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            timestamp, value, ttl = self._cache[key]
            if time.time() - timestamp < ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        self._cache[key] = (time.time(), value, ttl)
        return True
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
        return True
    
    def clear(self):
        self._cache.clear()


class RedisCache:
    """Redis cache client"""
    
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        try:
            import redis
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self.client.ping()
            logger.info(f"Redis connected: {REDIS_HOST}:{REDIS_PORT}")
        except ImportError:
            logger.warning("redis package not installed")
            self.client = None
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        if not self.client:
            return False
        try:
            # Convert SQLAlchemy objects to dictionaries for JSON serialization
            import datetime
            def serialize_sqlalchemy(obj):
                if hasattr(obj, '__dict__'):  # It's a SQLAlchemy model object
                    result = {}
                    for key, value in obj.__dict__.items():
                        if not key.startswith('_'):  # Skip private attributes
                            if isinstance(value, datetime.datetime):
                                result[key] = value.isoformat()
                            elif isinstance(value, datetime.date):
                                result[key] = value.isoformat()
                            else:
                                result[key] = value
                    return result
                elif isinstance(value, (datetime.datetime, datetime.date)):
                    return value.isoformat()
                else:
                    return str(obj)
            
            # Try to serialize the value, converting SQLAlchemy objects if needed
            serialized_value = None
            try:
                serialized_value = json.dumps(value)
            except TypeError:
                # If direct JSON serialization fails, convert SQLAlchemy objects
                import collections.abc
                def convert_nested_obj(obj):
                    if isinstance(obj, (list, tuple)):
                        return [convert_nested_obj(item) for item in obj]
                    elif isinstance(obj, collections.abc.Mapping):
                        return {key: convert_nested_obj(val) for key, val in obj.items()}
                    elif hasattr(obj, '__dict__'):
                        return serialize_sqlalchemy(obj)
                    elif isinstance(obj, (datetime.datetime, datetime.date)):
                        return obj.isoformat()
                    else:
                        return obj
                
                converted_value = convert_nested_obj(value)
                serialized_value = json.dumps(converted_value, default=str)
            
            self.client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
            return False
    
    def clear(self):
        pass


# Choose cache based on USE_REDIS
if USE_REDIS:
    cache = RedisCache()
else:
    cache = InMemoryCache()
    logger.info("Using in-memory cache")


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from arguments"""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = DEFAULT_TTL, key_prefix: str = ""):
    """Decorator to cache function results"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        
        return wrapper
    
    return decorator


def invalidate_cache(prefix: str = ""):
    """Invalidate cache entries"""
    cache.clear()
    logger.info(f"Cache invalidated: {prefix or 'all'}")
