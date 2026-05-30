"""API package for AI Visual Copilot backend."""
from fastapi import APIRouter

api_router = APIRouter()

from .routers import health, screenshots, users, history, workflows  # noqa: F401

api_router.include_router(health)
api_router.include_router(screenshots)
api_router.include_router(users)
api_router.include_router(history)
api_router.include_router(workflows)
