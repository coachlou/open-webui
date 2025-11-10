# File Ingestion & Retrieval App

A standalone application for document ingestion, processing, and semantic retrieval. Built on components from Open WebUI's RAG (Retrieval-Augmented Generation) system.

## Features

- **Document Upload & Storage**: Upload documents via REST API with support for local, S3, GCS, and Azure storage
- **Multi-Format Support**: PDF, DOCX, PPTX, CSV, Excel, TXT, Markdown, HTML, XML, and more
- **Text Processing**: Automatic text extraction, chunking, and embedding generation
- **Vector Search**: Semantic similarity search using embeddings
- **Hybrid Search**: Optional BM25 + Vector hybrid search for better results
- **Knowledge Bases**: Organize documents into collections with access control
- **Flexible Embeddings**: Support for local models (sentence-transformers), OpenAI, Ollama, Azure OpenAI
- **Multiple Vector DBs**: ChromaDB (default), Qdrant, Milvus, PostgreSQL pgvector, Elasticsearch, and more

## Architecture

```
┌─────────────┐
│   Upload    │
│   File      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Store     │  ← Local/S3/GCS/Azure
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Extract   │  ← Format-specific loaders
│   Text      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Chunk     │  ← RecursiveCharacterTextSplitter
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Embed     │  ← Sentence Transformers/OpenAI/Ollama
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Vector DB  │  ← ChromaDB/Qdrant/etc.
└─────────────┘
```

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd file-retrieval-app
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database

```bash
# Create data directories
mkdir -p data/uploads data/chroma

# The database will be automatically created on first run
```

### 5. Run the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Files

- `POST /api/files/` - Upload a file
- `GET /api/files/` - List all files
- `GET /api/files/{id}` - Get file metadata
- `GET /api/files/{id}/content` - Download file
- `DELETE /api/files/{id}` - Delete file

#### Knowledge Bases

- `POST /api/knowledge/` - Create knowledge base
- `GET /api/knowledge/` - List knowledge bases
- `GET /api/knowledge/{id}` - Get knowledge base
- `POST /api/knowledge/{id}/file/add` - Add files to knowledge base
- `POST /api/knowledge/{id}/query` - Query knowledge base

#### Retrieval

- `GET /api/retrieval/` - Get retrieval configuration
- `POST /api/retrieval/process` - Process a file for retrieval
- `POST /api/retrieval/query` - Query documents

## Usage Examples

### Upload a File

```bash
curl -X POST "http://localhost:8000/api/files/" \
  -F "file=@document.pdf" \
  -F "metadata={\"name\":\"My Document\"}"
```

### Query Documents

```bash
curl -X POST "http://localhost:8000/api/retrieval/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "collection_name": "file-<file-id>"
  }'
```

### Create Knowledge Base

```bash
curl -X POST "http://localhost:8000/api/knowledge/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Knowledge Base",
    "description": "Collection of documents",
    "data": {"file_ids": ["file-id-1", "file-id-2"]}
  }'
```

## Configuration

### Embedding Models

**Local (Default)**:
```env
RAG_EMBEDDING_ENGINE=
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**OpenAI**:
```env
RAG_EMBEDDING_ENGINE=openai
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_OPENAI_API_KEY=your-key-here
```

**Ollama**:
```env
RAG_EMBEDDING_ENGINE=ollama
RAG_EMBEDDING_MODEL=nomic-embed-text
RAG_OLLAMA_BASE_URL=http://localhost:11434
```

### Vector Databases

**ChromaDB (Default)** - No additional setup required:
```env
VECTOR_DB=chroma
CHROMA_DATA_PATH=./data/chroma
```

**Qdrant** - Requires Qdrant server:
```env
VECTOR_DB=qdrant
QDRANT_URL=http://localhost:6333
```

### Storage Providers

**Local (Default)**:
```env
STORAGE_PROVIDER=local
UPLOAD_DIR=./data/uploads
```

**AWS S3**:
```env
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=my-bucket
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
```

## Supported File Formats

| Category | Formats |
|----------|---------|
| Documents | PDF, DOCX, DOC, ODT, RTF |
| Spreadsheets | XLSX, XLS, CSV |
| Presentations | PPTX, PPT |
| Web | HTML, XML |
| Text | TXT, MD, JSON, LOG |
| Code | PY, JS, JAVA, GO, and 40+ more |
| Archives | EPUB |

## Advanced Features

### Hybrid Search

Enable BM25 + Vector hybrid search for improved retrieval:

```env
ENABLE_RAG_HYBRID_SEARCH=true
```

### Reranking

Add a reranking model to improve result quality:

```env
RAG_RERANKING_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

### Custom Chunking

Adjust chunk size and overlap:

```env
CHUNK_SIZE=1500
CHUNK_OVERLAP=100
```

## Project Structure

```
file-retrieval-app/
├── app/
│   ├── models/          # Database models
│   ├── routers/         # API endpoints
│   ├── retrieval/       # Document processing & vector search
│   │   ├── loaders/     # Document format loaders
│   │   └── vector/      # Vector database implementations
│   ├── storage/         # File storage providers
│   ├── utils/           # Utilities
│   └── internal/        # Database connection
├── data/                # Application data (git-ignored)
│   ├── uploads/         # Uploaded files
│   └── chroma/          # ChromaDB data
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
└── .env                # Configuration (create from .env.example)
```

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
pytest
```

## Troubleshooting

### Database Migration Issues

If you encounter database issues, remove the database and restart:

```bash
rm data/database.db
python main.py
```

### Embedding Model Downloads

First run will download embedding models (~80MB for all-MiniLM-L6-v2). This is normal.

### Import Errors

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

## Credits

This standalone application is built using components from [Open WebUI](https://github.com/open-webui/open-webui), an extensible, feature-rich, and user-friendly self-hosted WebUI.

## License

This project maintains compatibility with Open WebUI's MIT License. See the original project for full license details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Create an issue in this repository
- Check the Open WebUI documentation for component-specific details
