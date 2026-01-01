"""
Health check service.

Provides health checks for all system components.
"""

import logging
from dataclasses import dataclass
from typing import Literal

from src.database import get_db_manager
from src.services.cache import get_cache_service
from src.llm.gemini import get_gemini_client

logger = logging.getLogger(__name__)


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: Literal["healthy", "unhealthy", "degraded"]
    message: str | None = None
    latency_ms: int | None = None


@dataclass
class SystemHealth:
    """Overall system health."""
    status: Literal["healthy", "unhealthy", "degraded"]
    components: list[ComponentHealth]
    version: str = "0.1.0"


class HealthService:
    """Service for checking system health."""
    
    async def check_database(self) -> ComponentHealth:
        """Check database connectivity."""
        import time
        start = time.time()
        
        try:
            db = get_db_manager()
            healthy = await db.health_check()
            latency = int((time.time() - start) * 1000)
            
            if healthy:
                return ComponentHealth(
                    name="database",
                    status="healthy",
                    message="Connected to PostgreSQL",
                    latency_ms=latency,
                )
            else:
                return ComponentHealth(
                    name="database",
                    status="unhealthy",
                    message="Database health check failed",
                )
        except Exception as e:
            return ComponentHealth(
                name="database",
                status="unhealthy",
                message=str(e),
            )
    
    async def check_cache(self) -> ComponentHealth:
        """Check Redis/cache connectivity."""
        import time
        start = time.time()
        
        try:
            cache = get_cache_service()
            await cache.connect()
            
            # Test set/get
            test_key = "_health_check"
            await cache.set(test_key, "ok", ttl=10)
            value = await cache.get(test_key)
            await cache.delete(test_key)
            
            latency = int((time.time() - start) * 1000)
            
            if value == "ok":
                return ComponentHealth(
                    name="cache",
                    status="healthy",
                    message="Cache operational",
                    latency_ms=latency,
                )
            else:
                return ComponentHealth(
                    name="cache",
                    status="degraded",
                    message="Cache read/write failed",
                )
        except Exception as e:
            return ComponentHealth(
                name="cache",
                status="unhealthy",
                message=str(e),
            )
    
    async def check_llm(self) -> ComponentHealth:
        """Check LLM API availability (without making actual call)."""
        try:
            client = get_gemini_client()
            
            # Just check if client is configured
            if client.settings.gemini_api_key:
                return ComponentHealth(
                    name="llm",
                    status="healthy",
                    message="Gemini API configured",
                )
            else:
                return ComponentHealth(
                    name="llm",
                    status="unhealthy",
                    message="GEMINI_API_KEY not set",
                )
        except Exception as e:
            return ComponentHealth(
                name="llm",
                status="unhealthy",
                message=str(e),
            )
    
    async def check_all(self) -> SystemHealth:
        """Run all health checks."""
        components = [
            await self.check_database(),
            await self.check_cache(),
            await self.check_llm(),
        ]
        
        # Determine overall status
        statuses = [c.status for c in components]
        
        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall = "unhealthy"
        else:
            overall = "degraded"
        
        return SystemHealth(
            status=overall,
            components=components,
        )


# Singleton
_health_service: HealthService | None = None


def get_health_service() -> HealthService:
    """Get health service singleton."""
    global _health_service
    if _health_service is None:
        _health_service = HealthService()
    return _health_service
