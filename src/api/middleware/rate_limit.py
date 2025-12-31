"""
Rate limiting middleware using Redis or in-memory fallback.

Limits requests per user/IP to prevent abuse.
"""

import logging
import time
from collections import defaultdict
from typing import Any

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """Simple in-memory rate limiter (use Redis in production)."""
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if request is allowed.
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - self.window_size
        
        # Clean old requests
        self._requests[key] = [
            ts for ts in self._requests[key]
            if ts > window_start
        ]
        
        # Check limit
        current_count = len(self._requests[key])
        remaining = max(0, self.requests_per_minute - current_count)
        
        if current_count >= self.requests_per_minute:
            return False, 0
        
        # Add new request
        self._requests[key].append(now)
        return True, remaining - 1
    
    def get_retry_after(self, key: str) -> int:
        """Get seconds until rate limit resets."""
        if not self._requests[key]:
            return 0
        
        oldest = min(self._requests[key])
        reset_time = oldest + self.window_size
        return max(0, int(reset_time - time.time()))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, app, requests_per_minute: int = 10):
        super().__init__(app)
        self.limiter = InMemoryRateLimiter(requests_per_minute)
        self.excluded_paths = {"/health", "/docs", "/openapi.json", "/redoc"}
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique key for the client."""
        # Use API key if provided, otherwise use IP
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key}"
        
        # Get real IP (consider X-Forwarded-For for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        client_key = self._get_client_key(request)
        is_allowed, remaining = self.limiter.is_allowed(client_key)
        
        if not is_allowed:
            retry_after = self.limiter.get_retry_after(client_key)
            logger.warning(f"Rate limit exceeded for {client_key}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_minute)
        
        return response
