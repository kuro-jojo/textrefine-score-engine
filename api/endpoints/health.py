from fastapi import APIRouter, Request
from logging_config import setup_logging
from ..limiter import get_limiter

logger = setup_logging()

router = APIRouter()


@router.get("/health")
@router.get("/")
@get_limiter().limit(
    "100/minute",
    error_message="Limit set to 100 requests per minute. Please try again later.",
)
async def health_check(request: Request):
    logger.info("Health endpoint accessed. Text Refine Score Engine is healthy")
    return {"status": "healthy", "service": "Text Refine Score Engine"}
