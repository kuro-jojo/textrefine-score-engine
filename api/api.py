from fastapi import APIRouter
from .endpoints.evaluation import router as evaluation_router
from .endpoints.health import router as health_router

router = APIRouter()

# Include all API endpoints
router.include_router(evaluation_router, tags=["evaluation"])
router.include_router(health_router, tags=["health"])
