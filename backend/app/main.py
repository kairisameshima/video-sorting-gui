from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from .core.config import CORS_ORIGINS, TEMP_DIR
from .api.endpoints import router as api_router

# Create FastAPI app
app = FastAPI(
    title="Video Sorting GUI",
    description="A video sorting application with React frontend and FastAPI backend",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "Video Sorting GUI API is running"}
