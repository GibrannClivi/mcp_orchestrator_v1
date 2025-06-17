"""
In-memory L2 cache using cachetools.
"""
from cachetools import TTLCache
from typing import Any

cache = TTLCache(maxsize=1000, ttl=300)

def get_from_cache(key: str) -> Any:
    return cache.get(key)

def set_in_cache(key: str, value: Any) -> None:
    cache[key] = value

def clear_cache() -> None:
    cache.clear()
