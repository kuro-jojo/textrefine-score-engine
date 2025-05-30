from fastapi import APIRouter, Request
from logging_config import setup_logging
from ..limiter import get_limiter

logger = setup_logging()

router = APIRouter()


@router.get("/health")
@router.get("/")
@get_limiter().limit("100/minute", error_message="Too many requests. Please try again later.")
async def health_check(request: Request):
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "Text Refine Score Engine"}