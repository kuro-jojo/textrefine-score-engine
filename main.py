import uvicorn
import os
from fastapi import FastAPI, Request
from api.limiter import get_limiter
from api import api
from api.middleware import ClientIPFilter
from api.request_context import set_request_context
from fastapi.middleware.cors import CORSMiddleware
from logging_config import setup_logging, initialize_log_maintenance
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import asyncio

# Add IP filter to logger
logger = setup_logging()
ip_filter = ClientIPFilter()
logger.addFilter(ip_filter)

app = FastAPI(
    title="Text Refine Score Engine API",
    description="API for scoring text based on correctness, coherence and vocabulary",
    version="1.0.0",
)
app.state.limiter = get_limiter()
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# Initialize log maintenance
async def init_app():
    await initialize_log_maintenance()
    logger.info("Starting Text Refine Score Engine API")
    return app

app = asyncio.run(init_app())

origins = os.getenv("ORIGINS", "http://localhost:4200").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure origins is a list
if isinstance(origins, str):
    origins = [origins]


# Add middleware to set request context
@app.middleware("http")
async def set_request_context_middleware(request: Request, call_next):
    set_request_context(request)
    response = await call_next(request)
    return response


app.include_router(api.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
