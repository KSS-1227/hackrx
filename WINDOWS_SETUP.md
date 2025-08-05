# Windows Setup Guide

This guide helps you set up the LLM Document Processing System on Windows.

## Prerequisites

1. **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
2. **Git** (optional) - Download from [git-scm.com](https://git-scm.com/downloads)

## Installation Steps

### Step 1: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Dependencies (Choose One Option)

#### Option A: Windows-Compatible (Recommended)

```bash
pip install -r requirements-windows.txt
```

#### Option B: Minimal Installation (Fastest)

```bash
pip install -r requirements-minimal.txt
```

#### Option C: Full Installation (If no conflicts)

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

1. Copy `.env.example` to `.env`:

   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   BEARER_TOKEN=your-secure-bearer-token
   ```

### Step 4: Run the Application

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

## Testing the API

### Health Check

```bash
curl http://localhost:8000/health
```

### Test Document Processing

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer your-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["https://example.com/document.pdf"],
    "questions": ["What is this document about?"]
  }'
```

## Troubleshooting

### Common Issues

1. **FAISS Installation Error**

   - Use `requirements-windows.txt` which uses ChromaDB instead
   - ChromaDB is more Windows-friendly

2. **OpenAI API Key Error**

   - Make sure your `.env` file has the correct API key
   - Verify the key is valid at [OpenAI Platform](https://platform.openai.com/)

3. **Port Already in Use**

   - Change the port in `.env`: `API_PORT=8001`
   - Or kill the process using port 8000

4. **Permission Errors**
   - Run Command Prompt as Administrator
   - Or use PowerShell with elevated privileges

### Performance Tips

1. **Use SSD Storage** - Vector database performs better on SSD
2. **Increase RAM** - Large documents require more memory
3. **Close Unnecessary Programs** - Free up system resources

## API Documentation

Once running, visit:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Windows-Specific Features

- **ChromaDB Vector Store**: More reliable on Windows than FAISS
- **Automatic Fallback**: Falls back to FAISS if ChromaDB fails
- **Windows Path Handling**: Proper Windows path support
- **No SWIG Dependency**: Avoids compilation issues

## Production Deployment

For production on Windows Server:

1. Use `requirements-production.txt`
2. Set up Windows Service
3. Configure IIS reverse proxy
4. Use HTTPS certificates
5. Set up monitoring

## Support

If you encounter issues:

1. Check the logs in `./logs/app.log`
2. Verify all dependencies are installed
3. Ensure Python version compatibility
4. Check Windows firewall settings
