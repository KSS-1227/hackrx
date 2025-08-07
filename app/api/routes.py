"""
API routes for the LLM Document Processing System
"""

import time
from typing import List
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, UploadFile, File, Form
from loguru import logger
import json

from app.models.schemas import ProcessingRequest  # We're using direct JSON responses now
from app.services.document_processor import DocumentProcessor
from app.services.query_processor import QueryProcessor
from app.services.llm_service import LLMService
from app.core.config import settings

router = APIRouter()


@router.post("/run")
async def process_documents(
    documents: List[UploadFile] = File(...),
    questions: str = Form(...),
    fastapi_request: Request = None,
    background_tasks: BackgroundTasks = None
):
    """
    Process documents and answer questions
    
    This endpoint:
    1. Downloads and processes documents from provided URLs
    2. Extracts and chunks text content
    3. Generates embeddings and stores in vector database
    4. Processes queries using semantic search and LLM reasoning
    5. Returns structured answers
    """
    start_time = time.time()
    
    try:
        # Parse questions from JSON string
        questions = json.loads(questions)
        
        logger.info(f"Processing request with {len(documents)} documents and {len(questions)} questions")
        
        # Initialize services
        document_processor = DocumentProcessor()
        query_processor = QueryProcessor()
        llm_service = LLMService()
        
        # Get vector store from app state
        vector_store = fastapi_request.app.state.vector_store
        
        # Step 1: Process documents
        logger.info("Starting document processing...")
        file_paths = []
        processed_docs = []
        
        for file in documents:
            contents = await file.read()
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
                temp_file.write(contents)
                file_paths.append(temp_file.name)
        
        processed_docs = await document_processor.process_documents(file_paths)
        
        if not processed_docs:
            raise HTTPException(status_code=400, detail="No documents could be processed")
        
        # Step 2: Store embeddings in vector database (if available)
        if vector_store:
            logger.info("Storing document embeddings...")
            await vector_store.store_documents(processed_docs)
        
        # Step 3: Process queries
        logger.info("Processing queries...")
        answers = []
        
        for question in questions:
            try:
                if vector_store:
                    # Semantic search for relevant chunks
                    relevant_chunks = await vector_store.search(question, top_k=10)
                else:
                    # Fallback: use all document chunks (simple but works)
                    relevant_chunks = processed_docs[:10]  # Limit to first 10 chunks
                
                # Generate answer using LLM
                answer = await llm_service.generate_answer(
                    question=question,
                    context_chunks=relevant_chunks
                )
                
                answers.append(answer)
                
            except Exception as e:
                logger.error(f"Error processing question '{question}': {str(e)}")
                answers.append(f"Unable to process question: {str(e)}")
        
        processing_time = time.time() - start_time
        
        logger.info(f"Request processed successfully in {processing_time:.2f} seconds")
        
        # Format the response according to the new JSON structure
        return {
            "answers": answers,
            "processing_time": processing_time,
            "document_count": len(processed_docs)
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error processing request after {processing_time:.2f} seconds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/detailed")
async def process_documents_detailed(
    request: ProcessingRequest,
    fastapi_request: Request
):
    """
    Process documents and return detailed response with metadata
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing detailed request with {len(request.documents)} documents and {len(request.questions)} questions")
        
        # Initialize services
        document_processor = DocumentProcessor()
        query_processor = QueryProcessor()
        llm_service = LLMService()
        
        # Get vector store from app state
        vector_store = fastapi_request.app.state.vector_store
        
        # Process documents
        processed_docs = await document_processor.process_documents(
            [str(url) for url in request.documents]
        )
        
        if not processed_docs:
            raise HTTPException(status_code=400, detail="No documents could be processed")
        
        # Store embeddings (if available)
        if vector_store:
            await vector_store.store_documents(processed_docs)
        
        # Process queries with detailed information
        answers = []
        query_info = []
        
        for question in request.questions:
            try:
                if vector_store:
                    # Semantic search
                    relevant_chunks = await vector_store.search(question, top_k=10)
                else:
                    # Fallback: use all document chunks
                    relevant_chunks = processed_docs[:10]
                
                # Generate answer
                answer = await llm_service.generate_answer(
                    question=question,
                    context_chunks=relevant_chunks
                )
                
                answers.append(answer)
                
                # Collect query metadata
                query_info.append({
                    "question": question,
                    "answer": answer,
                    "confidence": 0.85,  # Placeholder - implement confidence scoring
                    "relevant_chunks": [chunk.content[:200] + "..." for chunk in relevant_chunks[:3]],
                    "source_documents": list(set([chunk.source for chunk in relevant_chunks]))
                })
                
            except Exception as e:
                logger.error(f"Error processing question '{question}': {str(e)}")
                answers.append(f"Unable to process question: {str(e)}")
                query_info.append({
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "confidence": 0.0,
                    "relevant_chunks": [],
                    "source_documents": []
                })
        
        processing_time = time.time() - start_time
        
        # Prepare document info
        doc_info = []
        for doc in processed_docs:
            doc_info.append({
                "url": doc.source,
                "filename": doc.metadata.get("filename", "unknown"),
                "size_bytes": doc.metadata.get("size_bytes", 0),
                "format": doc.metadata.get("format", "unknown"),
                "pages": doc.metadata.get("pages"),
                "chunks": len([chunk for chunk in processed_docs if chunk.source == doc.source]),
                "processing_time": doc.metadata.get("processing_time", 0.0)
            })
        
        # Format the detailed response according to the new JSON structure
        return {
            "answers": answers,
            "processing_time": processing_time,
            "document_count": len(processed_docs),
            "documents": doc_info,
            "queries": query_info
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error processing detailed request after {processing_time:.2f} seconds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))