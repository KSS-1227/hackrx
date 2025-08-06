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

# Use FAISS vector store for Render deployment (more reliable)
from app.services.vector_store import VectorStoreService

# Load environment variables
load_dotenv()

# Setup logging with Render-friendly config
from app.utils.logging_config import setup_render_logging
setup_render_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting LLM Document Processing System on Render...")
    
    # Initialize vector store with error handling
    try:
        vector_store = VectorStoreService()
        await vector_store.initialize()
        app.state.vector_store = vector_store
        logger.info("Vector store initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        # Continue without vector store for basic functionality
        app.state.vector_store = None
    
    logger.info("System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down system...")
    if hasattr(app.state, 'vector_store') and app.state.vector_store:
        try:
            await app.state.vector_store.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="LLM Document Processing System",
    description="High-accuracy document processing and query answering system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware with Render-friendly settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(
    api_router,
    prefix="/hackrx"
)

@app.get("/")
async def root():
    """Root endpoint for Render health checks"""
    return {"message": "LLM Document Processing System", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0", "platform": "render"}

if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", settings.API_PORT))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level=settings.LOG_LEVEL.lower(),
        workers=1  # Single worker for Render free tier
    )