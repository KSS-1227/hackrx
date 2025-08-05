# Migration Guide: OpenAI to Google Gemini

This guide explains the changes made to migrate the project from OpenAI to Google Gemini.

## Changes Made

### 1. Configuration Files Updated

- **`.env.example`**: Updated to use Gemini API key and models
- **`.env`**: Updated your existing environment file
- **`app/core/config.py`**: Changed configuration variables from OpenAI to Gemini

### 2. Dependencies Updated

- **`requirements.txt`**: Replaced OpenAI packages with Google Gemini packages
  - Removed: `openai==1.12.0`, `langchain-openai==0.0.5`
  - Added: `google-generativeai==0.3.2`, `langchain-google-genai==0.0.8`

### 3. Service Files Rewritten

- **`app/services/llm_service.py`**: Complete rewrite to use Google Gemini API
- **`app/services/embedding_service.py`**: Updated to use Gemini embeddings

### 4. Documentation Updated

- **`README.md`**: Updated all references from OpenAI to Gemini
- **Embedding dimensions**: Changed from 3072 to 768 (Gemini's embedding size)

## Next Steps

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

### 2. Update Your Environment

Edit your `.env` file and replace `your-gemini-api-key-here` with your actual API key:

```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 3. Install New Dependencies

Run the following command to install the updated dependencies:

```bash
pip install -r requirements.txt
```

### 4. Clear Vector Database (Important!)

Since the embedding dimensions changed from 3072 to 768, you need to clear your existing vector database:

```bash
# Windows
rmdir /s data\vector_db
mkdir data\vector_db

# Or manually delete the contents of the data/vector_db folder
```

### 5. Test the Migration

Run the test script to verify everything works:

```bash
python test_api.py
```

## Key Differences

### API Changes

| Feature             | OpenAI                   | Gemini                      |
| ------------------- | ------------------------ | --------------------------- |
| Chat Model          | `gpt-4-turbo`            | `gemini-1.5-pro`            |
| Embedding Model     | `text-embedding-3-large` | `models/text-embedding-004` |
| Embedding Dimension | 3072                     | 768                         |
| API Library         | `openai`                 | `google-generativeai`       |

### Code Changes

1. **Async Handling**: Gemini API calls are wrapped with `asyncio.to_thread()` since the library is synchronous
2. **Response Format**: Different response structure from Gemini API
3. **Configuration**: Uses `genai.configure()` instead of client initialization
4. **Error Handling**: Updated to handle Gemini-specific exceptions

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Gemini API key is valid and has the necessary permissions
2. **Rate Limits**: Gemini has different rate limits than OpenAI
3. **Model Names**: Ensure you're using correct Gemini model names
4. **Embedding Dimension Mismatch**: Clear your vector database if you get dimension errors

### Fallback Behavior

The system maintains fallback behavior:

- If Gemini API fails, it falls back to local SentenceTransformer models
- Local models are automatically downloaded and cached

## Benefits of Gemini

1. **Cost**: Generally more cost-effective than OpenAI
2. **Performance**: Competitive performance with GPT-4
3. **Integration**: Good integration with Google ecosystem
4. **Availability**: No waitlist required

## Support

If you encounter any issues:

1. Check the logs in `./logs/app.log`
2. Verify your API key is correct
3. Ensure all dependencies are installed
4. Clear vector database if embedding errors occur

The migration is complete! Just add your Gemini API key and install the dependencies to start using the system.
