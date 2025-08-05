"""
LLM Document Processing System - Main Application Entry Point
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from loguru import logger

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
# Use FAISS vector store instead of ChromaDB due to database schema issues
from app.services.vector_store import VectorStoreService
# Commented out ChromaDB import due to schema issues
# try:
#     from app.services.vector_store_chroma import VectorStoreService
# except ImportError:
#     # Fallback to FAISS if ChromaDB not available
#     from app.services.vector_store import VectorStoreService

# Load environment variables
load_dotenv()

# Setup logging
from app.utils.logging_config import setup_logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting LLM Document Processing System...")
    
    # Initialize vector store
    vector_store = VectorStoreService()
    await vector_store.initialize()
    app.state.vector_store = vector_store
    
    logger.info("System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down system...")
    if hasattr(app.state, 'vector_store'):
        await app.state.vector_store.close()

# Create FastAPI application
app = FastAPI(
    title="LLM Document Processing System",
    description="High-accuracy document processing and query answering system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes without token verification
app.include_router(
    api_router,
    prefix="/hackrx"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
