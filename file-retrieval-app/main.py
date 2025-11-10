"""
File Ingestion and Retrieval App
A standalone application for document ingestion, processing, and retrieval
Based on Open WebUI's RAG system
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.routers import files, retrieval, knowledge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="File Ingestion & Retrieval API",
    description="Standalone API for document ingestion, processing, and semantic retrieval",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(retrieval.router, prefix="/api/retrieval", tags=["Retrieval"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "File Ingestion & Retrieval API",
        "version": "1.0.0",
        "endpoints": {
            "files": "/api/files",
            "retrieval": "/api/retrieval",
            "knowledge": "/api/knowledge",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info("Starting File Ingestion & Retrieval API...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info",
    )
