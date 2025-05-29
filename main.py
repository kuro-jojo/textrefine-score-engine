from fastapi import FastAPI
from api.endpoints import evaluation
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import uvicorn
from logging_config import setup_logging

logger = setup_logging()

app = FastAPI(
    title="Text Refine Score Engine API",
    description="API for scoring text based on correctness, coherence and vocabulary",
    version="1.0.0",
)

import os

logger.info("Starting Text Refine Score Engine API")

origins = os.getenv("ORIGINS", "http://localhost:4200").split(',')

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

app.include_router(evaluation.router, prefix="/api/v1")
handler = Mangum(app)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Text Refine Score Engine API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
