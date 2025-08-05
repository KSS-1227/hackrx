"""
Document-related data models
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import numpy as np


class DocumentChunk(BaseModel):
    """Represents a chunk of text from a document"""
    
    id: str
    content: str
    source: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
    chunk_index: Optional[int] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def set_embedding(self, embedding: np.ndarray):
        """Set the embedding vector for this chunk"""
        self.embedding = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
    
    def get_embedding(self) -> Optional[np.ndarray]:
        """Get the embedding vector as numpy array"""
        if self.embedding is None:
            return None
        return np.array(self.embedding)


class ProcessedDocument(BaseModel):
    """Represents a fully processed document"""
    
    source: str
    filename: str
    format: str
    size_bytes: int
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any] = {}
    processing_time: float = 0.0
    
    @property
    def total_content_length(self) -> int:
        """Get total character count of all chunks"""
        return sum(len(chunk.content) for chunk in self.chunks)
    
    @property
    def chunk_count(self) -> int:
        """Get number of chunks"""
        return len(self.chunks)