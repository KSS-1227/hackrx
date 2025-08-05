"""
Vector store service for semantic search and document storage
"""

import os
import pickle
import asyncio
from typing import List, Optional, Dict, Any
import numpy as np
import faiss
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.core.exceptions import VectorStoreError
from app.models.document import DocumentChunk
from app.services.embedding_service import EmbeddingService


class VectorStoreService:
    """FAISS-based vector store for document chunks"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.index: Optional[faiss.Index] = None
        self.chunks: List[DocumentChunk] = []
        self.dimension = settings.EMBEDDING_DIMENSION
        self.index_path = Path(settings.VECTOR_DB_PATH)
        self.chunks_path = self.index_path / "chunks.pkl"
        self.faiss_index_path = self.index_path / "faiss.index"
        
        # Create directory if it doesn't exist
        self.index_path.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the vector store"""
        try:
            logger.info("Initializing vector store...")
            
            # Initialize embedding service
            await self.embedding_service.initialize()
            
            # Try to load existing index
            if await self._load_existing_index():
                logger.info(f"Loaded existing vector store with {len(self.chunks)} chunks")
            else:
                logger.info("Creating new vector store")
                self._create_new_index()
                
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize vector store: {str(e)}")
    
    async def store_documents(self, chunks: List[DocumentChunk]):
        """Store document chunks in the vector store"""
        try:
            logger.info(f"Storing {len(chunks)} document chunks...")
            
            # Generate embeddings for all chunks
            embeddings = await self.embedding_service.generate_embeddings(
                [chunk.content for chunk in chunks]
            )
            
            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.set_embedding(embedding)
            
            # Add to FAISS index
            embeddings_array = np.array([chunk.get_embedding() for chunk in chunks]).astype('float32')
            
            if self.index is None:
                self._create_new_index()
            
            # Add vectors to index
            start_id = len(self.chunks)
            self.index.add(embeddings_array)
            
            # Store chunks with their IDs
            for i, chunk in enumerate(chunks):
                chunk.metadata['vector_id'] = start_id + i
                self.chunks.append(chunk)
            
            # Save to disk
            await self._save_index()
            
            logger.info(f"Successfully stored {len(chunks)} chunks. Total chunks: {len(self.chunks)}")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to store documents: {str(e)}")
    
    async def search(self, query: str, top_k: int = 10) -> List[DocumentChunk]:
        """Search for relevant document chunks"""
        try:
            if self.index is None or len(self.chunks) == 0:
                logger.warning("Vector store is empty, returning no results")
                return []
            
            # Generate query embedding
            query_embeddings = await self.embedding_service.generate_embeddings([query])
            query_embedding = query_embeddings[0]  # Get the first (and only) embedding
            query_vector = np.array([query_embedding]).astype('float32')
            
            # Search in FAISS index
            scores, indices = self.index.search(query_vector, min(top_k, len(self.chunks)))
            
            # Return matching chunks
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks):  # Valid index
                    chunk = self.chunks[idx]
                    # Add similarity score to metadata
                    chunk.metadata['similarity_score'] = float(score)
                    results.append(chunk)
            
            logger.info(f"Found {len(results)} relevant chunks for query: {query[:50]}...")
            return results
            
        except Exception as e:
            raise VectorStoreError(f"Failed to search vector store: {str(e)}")
    
    async def clear(self):
        """Clear all data from the vector store"""
        try:
            logger.info("Clearing vector store...")
            
            self.chunks = []
            self._create_new_index()
            await self._save_index()
            
            logger.info("Vector store cleared successfully")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to clear vector store: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_chunks": len(self.chunks),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__ if self.index else None
        }
    
    async def close(self):
        """Close the vector store and save data"""
        try:
            if self.index is not None and len(self.chunks) > 0:
                await self._save_index()
            logger.info("Vector store closed successfully")
        except Exception as e:
            logger.error(f"Error closing vector store: {str(e)}")
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        # Use IndexFlatIP for cosine similarity (after L2 normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    async def _load_existing_index(self) -> bool:
        """Load existing index from disk"""
        try:
            if not self.faiss_index_path.exists() or not self.chunks_path.exists():
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(str(self.faiss_index_path))
            
            # Load chunks
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load existing index: {str(e)}")
            return False
    
    async def _save_index(self):
        """Save index and chunks to disk"""
        try:
            if self.index is not None:
                # Save FAISS index
                faiss.write_index(self.index, str(self.faiss_index_path))
                
                # Save chunks
                with open(self.chunks_path, 'wb') as f:
                    pickle.dump(self.chunks, f)
                
                logger.debug("Vector store saved to disk")
                
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")
            raise VectorStoreError(f"Failed to save vector store: {str(e)}")


class ChromaVectorStore:
    """Alternative ChromaDB-based vector store (for future use)"""
    
    def __init__(self):
        # Placeholder for ChromaDB implementation
        pass
    
    async def initialize(self):
        """Initialize ChromaDB"""
        # TODO: Implement ChromaDB initialization
        pass