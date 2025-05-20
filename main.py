from fastapi import FastAPI
from api.endpoints import evaluation
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import uvicorn

app = FastAPI(
    title="Text Refine Score Engine API",
    description="API for scoring text based on correctness and vocabulary.",
    version="1.0.0",
)

origins = [
    "http://localhost:4200",  # Angular app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluation.router, prefix="/api/v1")
handler = Mangum(app)


@app.get("/")
async def root():
    return {"message": "Text Refine Score Engine API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
