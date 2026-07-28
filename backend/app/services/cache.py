"""
Simple in-memory cache for embeddings and API responses.
"""

import time
from typing import Optional, List, Dict, Any

_cache = {}
_cache_expiry = {}


def cache_get(key: str) -> Optional[Any]:
    """Get cached value if not expired."""
    if key in _cache and _cache_expiry.get(key, 0) > time.time():
        return _cache[key]
    return None


def cache_set(key: str, value: Any, ttl: int = 3600):
    """Cache value for TTL seconds."""
    _cache[key] = value
    _cache_expiry[key] = time.time() + ttl


def cache_clear():
    """Clear all cache."""
    _cache.clear()
    _cache_expiry.clear()


def cache_delete(key: str):
    """Delete a specific cache entry."""
    if key in _cache:
        del _cache[key]
    if key in _cache_expiry:
        del _cache_expiry[key]


def cache_get_or_set(key: str, func, ttl: int = 3600):
    """Get from cache or execute function and cache result."""
    cached = cache_get(key)
    if cached is not None:
        return cached
    
    result = func()
    cache_set(key, result, ttl)
    return result