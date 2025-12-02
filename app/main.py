from contextlib import asynccontextmanager
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.components.embeddings_model import EmbeddingModelSingleton
from app.config.logging import setup_logging
from app.config.security.resource_server import require_auth
from app.handlers.comments_handler import router as comments_router
from app.handlers.summaries_handler import router as summaries_router
from app.handlers.auth_test_handler import router as auth_test_router
from app.settings import settings

setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    EmbeddingModelSingleton.get_model()
    print("Embedding model loaded at startup")

    yield
    print("Shutting down Saaransh backend")


app = FastAPI(
    title="saaransh_backend",
    description="Backend service for Saaransh application",
    version="1.0.0",
    lifespan=lifespan,
)

origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

protected_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(require_auth)]
)

protected_router.include_router(comments_router)
protected_router.include_router(summaries_router)
protected_router.include_router(auth_test_router)

app.include_router(protected_router)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
