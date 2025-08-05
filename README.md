# LLM Document Processing System

A high-accuracy document processing and query answering system that uses Large Language Models (LLMs) and semantic search to analyze policy documents, contracts, and other text-based documents.

## Features

- **Multi-format Document Support**: PDF, DOCX, DOC, TXT, HTML
- **Semantic Search**: Vector-based similarity search using embeddings
- **LLM-powered Reasoning**: Advanced query understanding and answer generation using Google Gemini
- **High Accuracy**: Multiple extraction methods and validation
- **RESTful API**: Simple HTTP API with Bearer token authentication
- **Scalable Architecture**: Async processing with concurrent document handling
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Architecture

### 1. API Layer

- **POST /hackrx/run**: Main processing endpoint
- **POST /hackrx/run/detailed**: Detailed processing with metadata
- **GET /health**: Health check endpoint
- Bearer token authentication for all endpoints

### 2. Document Processing Pipeline

1. **Download**: Fetch documents from URLs with size validation
2. **Extract**: Multi-method text extraction (PyMuPDF, pdfplumber, python-docx)
3. **Chunk**: Intelligent text segmentation with overlap
4. **Embed**: Generate vector embeddings using Google Gemini or local models
5. **Store**: Index in FAISS vector database

### 3. Query Processing

1. **Parse**: Extract intent and entities from natural language queries
2. **Search**: Semantic similarity search in vector database
3. **Reason**: LLM-based answer generation with context
4. **Validate**: Quality assessment and confidence scoring

## Installation

### Prerequisites

- Python 3.8+
- Google Gemini API key (recommended) or local models

### Setup

1. **Clone and navigate to the project**:

```bash
cd c:\Users\sheri\OneDrive\Desktop\Hackrx
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Configure environment**:

```bash
copy .env.example .env
```

Edit `.env` file with your configuration:

```env
# Required
GEMINI_API_KEY=your-gemini-api-key-here
BEARER_TOKEN=your-secure-bearer-token

# Optional (defaults provided)
API_HOST=0.0.0.0
API_PORT=8000
GEMINI_MODEL=gemini-1.5-pro
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
```

4. **Create required directories**:

```bash
mkdir data logs
mkdir data\vector_db
```

## Usage

### Starting the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Process Documents

```http
POST /hackrx/run
Authorization: Bearer your-bearer-token
Content-Type: application/json

{
  "documents": [
    "https://example.com/policy.pdf",
    "https://example.com/contract.docx"
  ],
  "questions": [
    "What is the coverage limit?",
    "What are the exclusions?",
    "What is the waiting period?"
  ]
}
```

**Response**:

```json
{
  "answers": [
    "The coverage limit is $100,000 per incident as specified in Section 3.1...",
    "The following are excluded from coverage: pre-existing conditions...",
    "There is a waiting period of 30 days for new policies..."
  ],
  "processing_time": 12.5,
  "document_count": 2
}
```

#### Health Check

```http
GET /health
```

### Testing

Run the test script:

```bash
python test_api.py
```

## Configuration

### Environment Variables

| Variable                   | Description              | Default                     |
| -------------------------- | ------------------------ | --------------------------- |
| `GEMINI_API_KEY`           | Google Gemini API key    | Required                    |
| `BEARER_TOKEN`             | API authentication token | `dev-bearer-token`          |
| `API_HOST`                 | Server host              | `0.0.0.0`                   |
| `API_PORT`                 | Server port              | `8000`                      |
| `GEMINI_MODEL`             | LLM model                | `gemini-1.5-pro`            |
| `GEMINI_EMBEDDING_MODEL`   | Embedding model          | `models/text-embedding-004` |
| `MAX_DOCUMENT_SIZE_MB`     | Max document size        | `50`                        |
| `CHUNK_SIZE`               | Text chunk size          | `1000`                      |
| `CHUNK_OVERLAP`            | Chunk overlap            | `200`                       |
| `RESPONSE_TIMEOUT_SECONDS` | Response timeout         | `30`                        |

### Supported Document Formats

- **PDF**: Using PyMuPDF and pdfplumber for maximum text extraction
- **DOCX/DOC**: Microsoft Word documents
- **TXT**: Plain text files
- **HTML**: Web pages and HTML documents

## High Accuracy Features

### Multi-Method Text Extraction

- Primary extraction with PyMuPDF for speed
- Fallback to pdfplumber for complex layouts
- Table and structured content extraction
- Encoding detection and handling

### Advanced Query Processing

- Intent classification (coverage, claims, terms, etc.)
- Entity extraction (age, amounts, dates, procedures)
- Keyword identification and expansion
- LLM-enhanced query understanding

### Semantic Search

- High-dimensional embeddings (768D with Google Gemini text-embedding-004)
- Cosine similarity matching
- Context-aware chunk retrieval
- Relevance scoring and ranking

### Answer Generation

- Context-aware prompting
- Multi-chunk reasoning
- Fact verification against source documents
- Confidence scoring and quality assessment

## Performance Optimization

- **Concurrent Processing**: Multiple documents processed simultaneously
- **Efficient Chunking**: Sentence-aware segmentation with overlap
- **Vector Indexing**: ChromaDB for fast similarity search
- **Caching**: Persistent vector store with disk storage
- **Streaming**: Async I/O for all operations

## Error Handling

- Comprehensive exception handling at all levels
- Graceful degradation (local models if Gemini fails)
- Detailed error messages and logging
- Automatic retry mechanisms for transient failures

## Monitoring and Logging

- Structured logging with Loguru
- Request/response timing
- Processing statistics
- Error tracking and alerting
- Health check endpoint for monitoring

## Security

- Bearer token authentication
- Input validation and sanitization
- File size and format restrictions
- Secure temporary file handling
- No persistent storage of sensitive data

## Deployment

### Production Considerations

1. **Environment Variables**: Set secure tokens and API keys
2. **HTTPS**: Use reverse proxy (nginx) for SSL termination
3. **Rate Limiting**: Implement API rate limiting
4. **Monitoring**: Set up health checks and alerting
5. **Scaling**: Use multiple workers with load balancer

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## Troubleshooting

### Common Issues

1. **Gemini API Errors**: Check API key and rate limits
2. **Document Download Failures**: Verify URLs are accessible
3. **Memory Issues**: Reduce chunk size or concurrent downloads
4. **Slow Processing**: Check network connectivity and model performance

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## Contributing

1. Follow the existing code structure
2. Add comprehensive error handling
3. Include logging for debugging
4. Write tests for new features
5. Update documentation

## License

This project is proprietary software developed for HackRx.

## Support

For issues and questions, please check the logs first and ensure all dependencies are properly installed.
