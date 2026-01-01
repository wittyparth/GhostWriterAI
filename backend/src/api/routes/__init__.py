"""
API Routes Package.

Contains all API route handlers.
"""

from src.api.routes.posts import router as posts_router
from src.api.routes.streaming import router as streaming_router
from src.api.routes.history import router as history_router

__all__ = ["posts_router", "streaming_router", "history_router"]


