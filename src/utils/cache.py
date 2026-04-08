"""
API caching layer to reduce redundant API calls.
"""

import time
import hashlib
import json
from typing import Optional, Any, Callable, Dict
from functools import wraps


class APICache:
    """
    TTL-based cache for API responses.
    
    Usage:
        cache = APICache(ttl_seconds=300)  # 5 minute TTL
        
        # Direct cache access
        cache.set("endpoint", {"param": "value"}, response_data)
        cached = cache.get("endpoint", {"param": "value"})
        
        # Or use as decorator
        @cache.cached("endpoint", ttl=300)
        def fetch_data(params):
            ...
    """
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, tuple] = {}
        self.default_ttl = default_ttl
        self.stats = {"hits": 0, "misses": 0, "sets": 0}
    
    def _make_key(self, endpoint: str, params: Dict = None) -> str:
        params_str = json.dumps(params, sort_keys=True, default=str) if params else ""
        raw = f"{endpoint}:{params_str}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Any]:
        key = self._make_key(endpoint, params)
        
        if key in self._cache:
            data, timestamp = self._cache[key]
            age = time.time() - timestamp
            
            if age < self.default_ttl:
                self.stats["hits"] += 1
                return data
            else:
                del self._cache[key]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, endpoint: str, params: Dict, data: Any, ttl: int = None):
        key = self._make_key(endpoint, params)
        self._cache[key] = (data, time.time())
        self.stats["sets"] += 1
    
    def invalidate(self, endpoint: str = None, params: Dict = None):
        if endpoint is None:
            self._cache.clear()
        else:
            key = self._make_key(endpoint, params)
            if key in self._cache:
                del self._cache[key]
    
    def cached(self, endpoint: str, ttl: int = None):
        if ttl is None:
            ttl = self.default_ttl
        
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                params = {**dict(kwargs)}
                for i, arg in enumerate(args):
                    params[f"arg{i}"] = arg
                
                cached_result = self.get(endpoint, params)
                if cached_result is not None:
                    return cached_result
                
                result = func(*args, **kwargs)
                self.set(endpoint, params, result, ttl)
                return result
            
            return wrapper
        
        return decorator
    
    def get_stats(self) -> Dict:
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "total_requests": total,
            "hit_rate_pct": round(hit_rate, 1),
            "cached_items": len(self._cache)
        }
    
    def __repr__(self):
        stats = self.get_stats()
        return f"APICache(hit_rate={stats['hit_rate_pct']}%, items={stats['cached_items']})"


api_cache = APICache(default_ttl=300)


def cached_trades(ttl: int = 300):
    return api_cache.cached("trades", ttl)


def cached_market(ttl: int = 600):
    return api_cache.cached("market", ttl)


def cached_positions(ttl: int = 300):
    return api_cache.cached("positions", ttl)