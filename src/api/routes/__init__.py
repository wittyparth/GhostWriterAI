"""
API Routes Package.

Contains all API route handlers.
"""

from src.api.routes.posts import router as posts_router

__all__ = ["posts_router"]
