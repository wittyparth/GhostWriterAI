"""
Redis cache service.

Provides caching for session state, rate limiting, and general caching.
"""

import logging
import json
from typing import Any

logger = logging.getLogger(__name__)

# Try to import redis, fallback to in-memory if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")


class InMemoryCache:
    """Simple in-memory cache fallback."""
    
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._ttls: dict[str, float] = {}
    
    async def get(self, key: str) -> Any | None:
        import time
        if key in self._ttls and self._ttls[key] < time.time():
            del self._store[key]
            del self._ttls[key]
            return None
        return self._store.get(key)
    
    async def set(self, key: str, value: Any, ex: int | None = None) -> bool:
        import time
        self._store[key] = value
        if ex:
            self._ttls[key] = time.time() + ex
        return True
    
    async def delete(self, key: str) -> int:
        if key in self._store:
            del self._store[key]
            if key in self._ttls:
                del self._ttls[key]
            return 1
        return 0
    
    async def exists(self, key: str) -> int:
        import time
        if key in self._ttls and self._ttls[key] < time.time():
            del self._store[key]
            del self._ttls[key]
            return 0
        return 1 if key in self._store else 0
    
    async def close(self):
        pass


class CacheService:
    """
    Cache service with Redis or in-memory fallback.
    
    Provides async caching for:
    - Session state
    - Rate limiting counters
    - Temporary data
    """
    
    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url
        self._client = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to Redis or use in-memory fallback."""
        if REDIS_AVAILABLE and self.redis_url:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                # Test connection
                await self._client.ping()
                self._connected = True
                logger.info(f"Connected to Redis: {self.redis_url}")
                return True
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, using in-memory cache")
        
        self._client = InMemoryCache()
        self._connected = True
        logger.info("Using in-memory cache")
        return True
    
    async def disconnect(self):
        """Disconnect from cache."""
        if self._client:
            await self._client.close()
            self._connected = False
    
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self._connected:
            await self.connect()
        
        value = await self._client.get(key)
        if value and isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        if not self._connected:
            await self.connect()
        
        if not isinstance(value, str):
            value = json.dumps(value)
        
        return await self._client.set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._connected:
            await self.connect()
        
        return await self._client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._connected:
            await self.connect()
        
        return await self._client.exists(key) > 0
    
    # Convenience methods for common patterns
    async def get_session(self, session_id: str) -> dict | None:
        """Get session data."""
        return await self.get(f"session:{session_id}")
    
    async def set_session(self, session_id: str, data: dict, ttl: int = 3600) -> bool:
        """Set session data."""
        return await self.set(f"session:{session_id}", data, ttl)
    
    async def get_generation_state(self, post_id: str) -> dict | None:
        """Get generation state for a post."""
        return await self.get(f"generation:{post_id}")
    
    async def set_generation_state(self, post_id: str, state: dict, ttl: int = 3600) -> bool:
        """Set generation state for a post."""
        return await self.set(f"generation:{post_id}", state, ttl)


# Singleton
_cache: CacheService | None = None


def get_cache_service(redis_url: str | None = None) -> CacheService:
    """Get or create cache service singleton."""
    global _cache
    if _cache is None:
        from src.config.settings import get_settings
        settings = get_settings()
        _cache = CacheService(redis_url or settings.redis_url)
    return _cache
