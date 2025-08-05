"""
Embedding service for generating vector representations of text using Google Gemini
or a local SentenceTransformer model.
"""

import os
import asyncio
from typing import List, Optional
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from loguru import logger
from google.api_core.exceptions import InvalidArgument, GoogleAPICallError

from app.core.config import settings
from app.core.exceptions import LLMError

# --- BEST PRACTICE: Define constants for model names ---
# This prevents typos and makes the code easier to update.
# 'embedding-001' is the correct model for text embeddings.
GEMINI_EMBEDDING_MODEL_NAME = "models/embedding-001"
LOCAL_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Fast and high-quality fallback

class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """
        Initializes the service. The key change is validating the API key here.
        """
        self.local_model: Optional[SentenceTransformer] = None
        self.use_gemini = False  # Default to False
        self.dimension = settings.EMBEDDING_DIMENSION

        # --- FIX #1: ROBUST API KEY VALIDATION ---
        # This is the most critical fix to prevent the 'API_KEY_INVALID' error.
        api_key = settings.GEMINI_API_KEY
        if api_key and api_key.strip() and len(api_key) > 10:  # Basic check for a valid-looking key
            logger.info("GEMINI_API_KEY found. Configuring the Gemini client.")
            self.use_gemini = True
            try:
                genai.configure(api_key=api_key)
            except Exception as e:
                # Catch potential configuration errors early.
                raise LLMError(f"Failed to configure Gemini client even though a key was provided: {e}")
        else:
            logger.warning("GEMINI_API_KEY is not set or is invalid. Falling back to local SentenceTransformer model.")
    
    async def initialize(self):
        """Initialize the embedding service by testing the connection or loading the local model."""
        try:
            if self.use_gemini:
                logger.info(f"Initializing Gemini embedding service with model: {GEMINI_EMBEDDING_MODEL_NAME}")
                await self._test_gemini_connection()
                # The Gemini embedding-001 model has a dimension of 768
                self.dimension = 768
            else:
                logger.info(f"Initializing local embedding service with model: {LOCAL_EMBEDDING_MODEL_NAME}")
                await self._initialize_local_model()
                
            logger.success(f"Embedding service initialized successfully. Dimension: {self.dimension}")
            
        except Exception as e:
            # The exception from _test_gemini_connection will be caught here.
            raise LLMError(f"Failed to initialize embedding service: {e}")
    
    async def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        
        try:
            if self.use_gemini:
                return await self._generate_gemini_embeddings(texts)
            else:
                # Ensure local model is loaded if not already
                if not self.local_model:
                    await self._initialize_local_model()
                return await self._generate_local_embeddings(texts)
                
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise LLMError(f"Failed to generate embeddings: {e}")

    async def _generate_gemini_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using the Google Gemini API efficiently."""
        
        # --- FIX #2: EFFICIENT BATCHING ---
        # The `embed_content` function is designed to handle a list of texts at once.
        # Calling it in a loop is highly inefficient. This is much faster.
        try:
            # The API handles batching internally up to its limit (e.g., 100).
            # We pass the whole list directly.
            response = await asyncio.to_thread(
                genai.embed_content,
                model=GEMINI_EMBEDDING_MODEL_NAME,
                content=texts,
                task_type="retrieval_document"
            )
            
            embeddings = [np.array(embedding) for embedding in response['embedding']]
            logger.info(f"Generated {len(embeddings)} Gemini embeddings.")
            return embeddings

        except (InvalidArgument, GoogleAPICallError) as e:
            logger.error(f"A Google API error occurred during Gemini embedding generation: {e}")
            logger.warning("Falling back to local embedding model due to API error.")
            # Ensure local model is loaded for fallback
            if not self.local_model:
                await self._initialize_local_model()
            return await self._generate_local_embeddings(texts)
    
    async def _generate_local_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using the local SentenceTransformer model."""
        if not self.local_model:
            raise LLMError("Local embedding model is not initialized.")
            
        embeddings = self.local_model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        return [np.array(embedding) for embedding in embeddings]

    async def _initialize_local_model(self):
        """Loads and initializes the local SentenceTransformer model."""
        if self.local_model is None:
            logger.info(f"Loading local model: {LOCAL_EMBEDDING_MODEL_NAME}...")
            # Run the synchronous model loading in a separate thread
            self.local_model = await asyncio.to_thread(SentenceTransformer, LOCAL_EMBEDDING_MODEL_NAME)
            self.dimension = self.local_model.get_sentence_embedding_dimension()
            logger.info("Local model loaded successfully.")

    async def _test_gemini_connection(self):
        """Tests the Gemini API connection with a simple request."""
        try:
            logger.info("Testing Gemini API connection...")
            await self.generate_embeddings(["test connection"])
            logger.success("✅ Gemini API connection test successful.")
        except (InvalidArgument, GoogleAPICallError) as e:
            # --- FIX #3: CLEARER ERROR MESSAGE ---
            error_message = (
                "Gemini API connection failed. This is likely due to an invalid API key "
                "or disabled API service in your Google Cloud project. "
                f"Please check your GOOGLE_API_KEY. Original Error: {e}"
            )
            logger.error(error_message)
            raise LLMError(error_message)

    def get_dimension(self) -> int:
        """Returns the embedding dimension of the currently active model."""
        return self.dimension