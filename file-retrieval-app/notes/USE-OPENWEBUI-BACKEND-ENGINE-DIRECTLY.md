Here's what you need to use Open WebUI's backend retrieval engine directly:

  Authentication

  Generate an API Key:
  POST https://your-openwebui-instance.com/api/v1/auths/api_key
  Authorization: Bearer <your-session-token>

  Or generate it via the UI: Settings → Account → API Keys

  Format: sk-<uuid>

  Use in all requests:
  Authorization: Bearer sk-your-generated-api-key

  Core Retrieval Endpoints

  1. Query a Single Document/Collection

  Endpoint: POST /api/v1/retrieval/query/doc

  Request body:
  {
    "collection_name": "your_collection_name",
    "query": "your search query",
    "k": 5,                    // optional: top K results (default: config value)
    "k_reranker": 10,         // optional: top K for reranking
    "r": 0.7,                 // optional: relevance threshold (0-1)
    "hybrid": true            // optional: enable hybrid search (vector + BM25)
  }

  Response: Returns matching documents with relevance scores

  2. Query Multiple Collections

  Endpoint: POST /api/v1/retrieval/query/collection

  Request body:
  {
    "collection_names": ["collection1", "collection2"],
    "query": "your search query",
    "k": 5,
    "k_reranker": 10,
    "r": 0.7,
    "hybrid": true,
    "hybrid_bm25_weight": 0.5  // optional: weight for BM25 in hybrid search
  }

  3. List Knowledge Bases

  Endpoint: GET /api/v1/knowledge/

  Returns all accessible knowledge bases for the authenticated user.

  4. Get Specific Knowledge Base

  Endpoint: GET /api/v1/knowledge/{id}

  Returns details and files for a specific knowledge base.

  Example GPT Action Schema

  openapi: 3.0.0
  info:
    title: Open WebUI Retrieval API
    version: 1.0.0
  servers:
    - url: https://your-openwebui-instance.com/api/v1

  paths:
    /retrieval/query/collection:
      post:
        operationId: queryKnowledgeBase
        summary: Search knowledge base collections
        security:
          - BearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                required:
                  - collection_names
                  - query
                properties:
                  collection_names:
                    type: array
                    items:
                      type: string
                  query:
                    type: string
                  k:
                    type: integer
                    default: 5
                  hybrid:
                    type: boolean
                    default: true
        responses:
          '200':
            description: Search results

    /knowledge/:
      get:
        operationId: listKnowledgeBases
        summary: List available knowledge bases
        security:
          - BearerAuth: []
        responses:
          '200':
            description: List of knowledge bases

  components:
    securitySchemes:
      BearerAuth:
        type: http
        scheme: bearer

  Quick Start

  1. Generate API key in Open WebUI UI
  2. Get collection names via GET /api/v1/knowledge/
  3. Query collections via POST /api/v1/retrieval/query/collection

  The retrieval engine supports:
  - Hybrid search (vector + BM25 keyword matching)
  - Reranking with cross-encoders
  - Multiple vector databases (Chroma, Qdrant, Pinecone, etc.)
  - Relevance filtering

  All endpoints require authentication with your API key as a Bearer token.