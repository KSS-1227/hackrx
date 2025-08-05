"""
ChromaDB-based vector store service for Windows compatibility
"""

import os
import asyncio
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.core.exceptions import VectorStoreError
from app.models.document import DocumentChunk
from app.services.embedding_service import EmbeddingService


class ChromaVectorStoreService:
    """ChromaDB-based vector store for document chunks (Windows compatible)"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client: Optional[chromadb.Client] = None
        self.collection = None
        self.collection_name = "document_chunks"
        self.db_path = Path(settings.VECTOR_DB_PATH)
        
        # Create directory if it doesn't exist
        self.db_path.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the ChromaDB vector store"""
        try:
            logger.info("Initializing ChromaDB vector store...")
            
            # Initialize embedding service
            await self.embedding_service.initialize()
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=None  # We'll provide embeddings manually
                )
                logger.info(f"Loaded existing collection with {self.collection.count()} chunks")
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=None
                )
                logger.info("Created new ChromaDB collection")
                
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize ChromaDB vector store: {str(e)}")
    
    async def store_documents(self, chunks: List[DocumentChunk]):
        """Store document chunks in the vector store"""
        try:
            logger.info(f"Storing {len(chunks)} document chunks in ChromaDB...")
            
            if not self.collection:
                raise VectorStoreError("Vector store not initialized")
            
            # Generate embeddings for all chunks
            embeddings = await self.embedding_service.generate_embeddings(
                [chunk.content for chunk in chunks]
            )
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            embeddings_list = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Generate unique ID
                chunk_id = f"{chunk.source}_{chunk.chunk_index}_{i}"
                ids.append(chunk_id)
                documents.append(chunk.content)
                
                # Prepare metadata (ChromaDB requires string values)
                metadata = {
                    "source": chunk.source,
                    "chunk_index": str(chunk.chunk_index),
                    "start_char": str(chunk.start_char),
                    "end_char": str(chunk.end_char)
                }
                
                # Add other metadata as strings
                for key, value in chunk.metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        metadata[f"meta_{key}"] = str(value)
                
                metadatas.append(metadata)
                embeddings_list.append(embedding)
            
            # Add to ChromaDB collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings_list
            )
            
            logger.info(f"Successfully stored {len(chunks)} chunks. Total chunks: {self.collection.count()}")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to store documents in ChromaDB: {str(e)}")
    
    async def search(self, query: str, top_k: int = 10) -> List[DocumentChunk]:
        """Search for relevant document chunks"""
        try:
            if not self.collection:
                raise VectorStoreError("Vector store not initialized")
            
            if self.collection.count() == 0:
                logger.warning("Vector store is empty, returning no results")
                return []
            
            # Generate query embedding
            query_embeddings = await self.embedding_service.generate_embeddings([query])
            query_embedding = query_embeddings[0]  # Get the first (and only) embedding
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count())
            )
            
            # Convert results back to DocumentChunk objects
            chunks = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    # Extract metadata
                    metadata = results['metadatas'][0][i]
                    
                    # Create DocumentChunk
                    chunk = DocumentChunk(
                        content=results['documents'][0][i],
                        source=metadata.get('source', ''),
                        chunk_index=int(metadata.get('chunk_index', 0)),
                        start_char=int(metadata.get('start_char', 0)),
                        end_char=int(metadata.get('end_char', 0))
                    )
                    
                    # Add similarity score and other metadata
                    chunk.metadata['similarity_score'] = float(results['distances'][0][i])
                    
                    # Add other metadata
                    for key, value in metadata.items():
                        if key.startswith('meta_'):
                            original_key = key[5:]  # Remove 'meta_' prefix
                            chunk.metadata[original_key] = value
                    
                    chunks.append(chunk)
            
            logger.info(f"Found {len(chunks)} relevant chunks for query: {query[:50]}...")
            return chunks
            
        except Exception as e:
            raise VectorStoreError(f"Failed to search ChromaDB vector store: {str(e)}")
    
    async def clear(self):
        """Clear all data from the vector store"""
        try:
            logger.info("Clearing ChromaDB vector store...")
            
            if self.collection:
                # Delete the collection and recreate it
                self.client.delete_collection(self.collection_name)
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=None
                )
            
            logger.info("ChromaDB vector store cleared successfully")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to clear ChromaDB vector store: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count() if self.collection else 0
            return {
                "total_chunks": count,
                "index_size": count,
                "dimension": settings.EMBEDDING_DIMENSION,
                "index_type": "ChromaDB"
            }
        except Exception:
            return {
                "total_chunks": 0,
                "index_size": 0,
                "dimension": settings.EMBEDDING_DIMENSION,
                "index_type": "ChromaDB"
            }
    
    async def close(self):
        """Close the vector store"""
        try:
            # ChromaDB automatically persists data
            logger.info("ChromaDB vector store closed successfully")
        except Exception as e:
            logger.error(f"Error closing ChromaDB vector store: {str(e)}")


# Alias for compatibility
VectorStoreService = ChromaVectorStoreService
