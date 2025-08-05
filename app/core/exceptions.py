"""
Custom exceptions and exception handlers
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
import traceback


class DocumentProcessingError(Exception):
    """Raised when document processing fails"""
    pass


class VectorStoreError(Exception):
    """Raised when vector store operations fail"""
    pass


class LLMError(Exception):
    """Raised when LLM operations fail"""
    pass


class DocumentDownloadError(Exception):
    """Raised when document download fails"""
    pass


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(DocumentProcessingError)
    async def document_processing_exception_handler(request: Request, exc: DocumentProcessingError):
        logger.error(f"Document processing error: {str(exc)}")
        return JSONResponse(
            status_code=422,
            content={"error": "Document processing failed", "detail": str(exc)}
        )
    
    @app.exception_handler(VectorStoreError)
    async def vector_store_exception_handler(request: Request, exc: VectorStoreError):
        logger.error(f"Vector store error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Vector store operation failed", "detail": str(exc)}
        )
    
    @app.exception_handler(LLMError)
    async def llm_exception_handler(request: Request, exc: LLMError):
        logger.error(f"LLM error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "LLM operation failed", "detail": str(exc)}
        )
    
    @app.exception_handler(DocumentDownloadError)
    async def download_exception_handler(request: Request, exc: DocumentDownloadError):
        logger.error(f"Document download error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={"error": "Document download failed", "detail": str(exc)}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": "An unexpected error occurred"}
        )