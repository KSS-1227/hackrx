"""
Pydantic models for request/response schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, validator


class ProcessingRequest(BaseModel):
    """Request model for document processing"""
    documents: List[HttpUrl] = Field(..., description="URLs to policy or contract documents")
    questions: List[str] = Field(..., min_items=1, description="Array of natural language queries")
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one question is required')
        for question in v:
            if not question.strip():
                raise ValueError('Questions cannot be empty')
        return v


class ProcessingResponse(BaseModel):
    """Response model for document processing"""
    answers: List[str] = Field(..., description="Array of answer strings, each addressing a question")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    document_count: Optional[int] = Field(None, description="Number of documents processed")


class DocumentInfo(BaseModel):
    """Information about a processed document"""
    url: str
    filename: str
    size_bytes: int
    format: str
    pages: Optional[int] = None
    chunks: int
    processing_time: float


class QueryInfo(BaseModel):
    """Information about a processed query"""
    question: str
    answer: str
    confidence: float
    relevant_chunks: List[str]
    source_documents: List[str]


class DetailedProcessingResponse(BaseModel):
    """Detailed response model with additional metadata"""
    answers: List[str]
    processing_time: float
    document_count: int
    documents: List[DocumentInfo]
    queries: List[QueryInfo]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    timestamp: Optional[str] = None