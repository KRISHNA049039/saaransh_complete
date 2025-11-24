from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings

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

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
