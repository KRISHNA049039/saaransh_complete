from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings
from app.handlers.comments_handler import router as comments_router
from app.config.logging import setup_logging
from app.settings import settings

setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="saaransh_backend",
    description="Backend service for Saaransh application",
    version="1.0.0",
)

origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(comments_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
