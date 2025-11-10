# Quick Start Guide

Get your File Ingestion & Retrieval App running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- 2GB free disk space (for embedding models)

## Step 1: Run Setup Script

```bash
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create data directories
- Generate `.env` configuration file

## Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
```

## Step 3: Start the Application

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Test the API

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Step 5: Upload Your First Document

### Using curl:

```bash
curl -X POST "http://localhost:8000/api/files/" \
  -F "file=@/path/to/your/document.pdf"
```

### Using Python:

```python
import requests

url = "http://localhost:8000/api/files/"
files = {"file": open("document.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using the Swagger UI:

1. Go to http://localhost:8000/docs
2. Find `POST /api/files/`
3. Click "Try it out"
4. Choose a file to upload
5. Click "Execute"

## Step 6: Query Your Document

After uploading, the file will be processed automatically. Query it using:

```bash
curl -X POST "http://localhost:8000/api/retrieval/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "collection_name": "file-YOUR-FILE-ID"
  }'
```

Replace `YOUR-FILE-ID` with the ID returned from the upload.

## Next Steps

### Create a Knowledge Base

Group multiple documents together:

```bash
curl -X POST "http://localhost:8000/api/knowledge/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Documents",
    "description": "Collection of my PDFs",
    "data": {
      "file_ids": ["file-id-1", "file-id-2"]
    }
  }'
```

### Enable Hybrid Search

Edit `.env` and add:
```
ENABLE_RAG_HYBRID_SEARCH=true
```

This combines BM25 keyword search with vector similarity for better results.

### Use OpenAI Embeddings

For better quality (requires API key):

Edit `.env`:
```
RAG_EMBEDDING_ENGINE=openai
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_OPENAI_API_KEY=sk-your-api-key-here
```

### Switch to Cloud Storage

For production use with S3:

Edit `.env`:
```
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=my-bucket
S3_ACCESS_KEY_ID=your-key
S3_SECRET_ACCESS_KEY=your-secret
S3_REGION_NAME=us-east-1
```

## Troubleshooting

### Port Already in Use

Change the port in `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8080)  # Changed to 8080
```

### Embedding Model Download Slow

First run downloads ~80MB model. This is one-time only. If interrupted:
```bash
rm -rf ~/.cache/huggingface
python main.py  # Will re-download
```

### Import Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade --force-reinstall
```

## Common API Patterns

### Upload and Wait for Processing

```python
import requests
import time

# Upload
response = requests.post(
    "http://localhost:8000/api/files/",
    files={"file": open("doc.pdf", "rb")}
)
file_id = response.json()["id"]

# Wait for processing
while True:
    status = requests.get(f"http://localhost:8000/api/files/{file_id}")
    if status.json()["data"]["status"] == "completed":
        break
    time.sleep(1)

print("Processing complete!")
```

### Query with Filters

```python
response = requests.post(
    "http://localhost:8000/api/retrieval/query",
    json={
        "query": "machine learning",
        "collection_name": f"file-{file_id}",
        "top_k": 5  # Return top 5 results
    }
)
results = response.json()
```

## Production Deployment

For production:

1. Set `reload=False` in `main.py`
2. Use a production ASGI server (gunicorn + uvicorn)
3. Set up proper authentication
4. Use PostgreSQL instead of SQLite
5. Use managed vector DB (Pinecone, Qdrant Cloud)
6. Enable HTTPS
7. Set up monitoring and logging

See README.md for detailed production setup.

## Support

- **Documentation**: See README.md
- **API Reference**: http://localhost:8000/docs
- **Issues**: Create an issue in the repository
