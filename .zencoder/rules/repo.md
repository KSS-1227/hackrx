---
description: Repository Information Overview
alwaysApply: true
---

# LLM Document Processing System Information

## Summary

A high-accuracy document processing and query answering system that uses Large Language Models (LLMs) and semantic search to analyze policy documents, contracts, and other text-based documents. The system supports multiple document formats, provides semantic search capabilities, and uses Google Gemini for advanced query understanding and answer generation.

## Structure

- **app/**: Core application code organized in a modular structure
  - **api/**: API routes and endpoints
  - **core/**: Core configuration and exceptions
  - **models/**: Data models and schemas
  - **services/**: Business logic services
  - **utils/**: Utility functions
- **data/**: Storage for vector database
- **frontend/**: React-based web interface
- **logs/**: Application logs
- **venv/**: Python virtual environment

## Language & Runtime

**Backend Language**: Python
**Version**: 3.8+ (recommended 3.11)
**Framework**: FastAPI
**Frontend Language**: JavaScript/React
**Build System**: pip (backend), npm/Vite (frontend)
**Package Manager**: pip (backend), npm (frontend)

## Dependencies

### Backend Dependencies

**Main Dependencies**:

- fastapi: Web framework for building APIs
- uvicorn: ASGI server for FastAPI
- google-generativeai: Google Gemini API client
- langchain: Framework for LLM applications
- PyMuPDF/pdfplumber: PDF processing libraries
- chromadb: Vector database for embeddings
- spacy/nltk: NLP processing libraries

**Development Dependencies**:

- pytest/pytest-asyncio: Testing framework
- black/flake8: Code formatting and linting

### Frontend Dependencies

**Main Dependencies**:

- react: UI library (v19.1.0)
- react-dom: DOM rendering for React
- axios: HTTP client for API requests

**Development Dependencies**:

- vite: Build tool and development server
- eslint: Code linting
- @vitejs/plugin-react: React plugin for Vite

## Build & Installation

### Backend

```bash
# Create virtual environment
python -m venv venv
# Activate virtual environment (Windows)
venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Configure environment
copy .env.example .env
# Edit .env with API keys and configuration
# Create required directories
mkdir -p data/vector_db logs
```

### Frontend

```bash
# Navigate to frontend directory
cd frontend
# Install dependencies
npm install
# Start development server
npm run dev
# Build for production
npm run build
```

## Testing

**Framework**: pytest
**Test Location**: test_api.py (API tests)
**Run Command**:

```bash
python test_api.py
```

## Usage & Operations

**Start Server**:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

**API Endpoints**:

- `POST /hackrx/run`: Process documents and answer questions
- `POST /hackrx/run/detailed`: Detailed processing with metadata
- `GET /health`: Health check endpoint

**Environment Variables**:

- `GEMINI_API_KEY`: Google Gemini API key (required)
- `BEARER_TOKEN`: API authentication token
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `GEMINI_MODEL`: LLM model (default: gemini-1.5-pro)
- `GEMINI_EMBEDDING_MODEL`: Embedding model (default: models/text-embedding-004)
