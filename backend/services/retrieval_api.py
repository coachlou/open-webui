import os
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

try:
    from openai import AzureOpenAI, OpenAI
except Exception:  # pragma: no cover - makes local development easier if openai is missing
    AzureOpenAI = None  # type: ignore[assignment]
    OpenAI = None  # type: ignore[assignment]


DEFAULT_TOP_K = 6


class CollectionQueryRequest(BaseModel):
    collection_ids: List[str] = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    top_k: int = Field(DEFAULT_TOP_K, ge=1, le=50)
    rerank_k: Optional[int] = Field(None, ge=1, le=100)
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    hybrid_alpha: Optional[float] = Field(None, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None


class Chunk(BaseModel):
    text: str
    metadata: Dict[str, Any]


class RetrievedChunk(BaseModel):
    chunk: Chunk
    score: float


class CollectionQueryResponse(BaseModel):
    status: bool
    query: str
    results: List[RetrievedChunk]


def _load_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    api_key = os.getenv("QDRANT_API_KEY")
    timeout = float(os.getenv("QDRANT_TIMEOUT", "5.0"))
    prefer_grpc = os.getenv("QDRANT_PREFER_GRPC", "false").lower() == "true"

    if prefer_grpc:
        # For gRPC we expect host and optional ports to be provided separately
        host = _load_env("QDRANT_HOST")
        http_port = int(os.getenv("QDRANT_HTTP_PORT", "6333"))
        grpc_port = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
        return QdrantClient(
            host=host,
            port=http_port,
            grpc_port=grpc_port,
            prefer_grpc=True,
            api_key=api_key,
            timeout=timeout,
        )

    url = _load_env("QDRANT_URL")
    return QdrantClient(url=url, api_key=api_key, timeout=timeout)


def _resolve_embedding_function() -> Callable[[str], List[float]]:
    provider = os.getenv("EMBEDDINGS_PROVIDER", "openai").lower()

    if provider == "openai":
        if OpenAI is None:
            raise RuntimeError("openai python package is required for OpenAI embeddings.")

        api_key = _load_env("OPENAI_API_KEY")
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        base_url = os.getenv("OPENAI_BASE_URL")

        client = OpenAI(api_key=api_key, base_url=base_url)

        def embed(text: str) -> List[float]:
            response = client.embeddings.create(model=model, input=text)
            return response.data[0].embedding  # type: ignore[return-value]

        return embed

    if provider == "azure_openai":
        if AzureOpenAI is None:
            raise RuntimeError(
                "openai python package >=1.0 is required for Azure OpenAI embeddings."
            )

        endpoint = _load_env("AZURE_OPENAI_ENDPOINT")
        api_key = _load_env("AZURE_OPENAI_API_KEY")
        api_version = _load_env("AZURE_OPENAI_API_VERSION")
        deployment = _load_env("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

        client = AzureOpenAI(
            azure_endpoint=endpoint, api_key=api_key, api_version=api_version
        )

        def embed(text: str) -> List[float]:
            response = client.embeddings.create(model=deployment, input=text)
            return response.data[0].embedding  # type: ignore[return-value]

        return embed

    raise RuntimeError(f"Unsupported EMBEDDINGS_PROVIDER '{provider}'")


@lru_cache(maxsize=1)
def get_embedding_function() -> Callable[[str], List[float]]:
    return _resolve_embedding_function()


def _build_filter(filters: Dict[str, Any]) -> Optional[Filter]:
    conditions: List[FieldCondition] = []
    for key, value in filters.items():
        field_key = f"metadata.{key}"
        if isinstance(value, list):
            conditions.append(FieldCondition(key=field_key, match=MatchAny(any=value)))
        else:
            conditions.append(FieldCondition(key=field_key, match=MatchValue(value=value)))
    if not conditions:
        return None
    return Filter(must=conditions)


def _normalise_score(raw_score: float) -> float:
    # Qdrant cosine similarity returns [-1, 1]. Map to [0, 1] for consistency.
    return max(0.0, min(1.0, (raw_score + 1.0) / 2.0))


def _convert_point(point: ScoredPoint, fallback_collection: str) -> RetrievedChunk:
    payload = point.payload or {}
    text = payload.get("text", "")
    metadata = payload.get("metadata") or {}
    metadata.setdefault("collection_id", fallback_collection)
    metadata["qdrant_point_id"] = str(point.id)

    return RetrievedChunk(
        chunk=Chunk(text=text, metadata=metadata),
        score=_normalise_score(point.score if point.score is not None else 0.0),
    )


app = FastAPI(
    title="Knowledge Retrieval API",
    version="1.0.0",
    description="Lightweight retrieval service over Qdrant collections.",
)


@app.post(
    "/collections/query",
    response_model=CollectionQueryResponse,
    summary="Retrieve passages from one or more knowledge bases.",
)
def query_collections(payload: CollectionQueryRequest) -> CollectionQueryResponse:
    client = get_qdrant_client()
    embed = get_embedding_function()

    vector = embed(payload.query)
    limit = max(payload.top_k, payload.rerank_k or payload.top_k)
    collection_prefix = os.getenv("QDRANT_COLLECTION_PREFIX", "")

    all_points: List[RetrievedChunk] = []

    filters: Optional[Filter] = None
    if payload.filters:
        filters = _build_filter(payload.filters)

    for collection_id in payload.collection_ids:
        collection_name = (
            f"{collection_prefix}_{collection_id}"
            if collection_prefix
            else collection_id
        )
        try:
            response = client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit,
                query_filter=filters,
            )
        except Exception as exc:  # pragma: no cover - depends on server state
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_id}' is unavailable: {exc}",
            ) from exc

        for point in response.points:
            retrieved = _convert_point(point, fallback_collection=collection_id)
            if payload.min_score is None or retrieved.score >= payload.min_score:
                all_points.append(retrieved)

    all_points.sort(key=lambda item: item.score, reverse=True)
    top_results = all_points[: payload.top_k]

    return CollectionQueryResponse(status=True, query=payload.query, results=top_results)


@app.get("/healthz", summary="Readiness probe")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


def create_app() -> FastAPI:
    """
    Helper for ASGI servers (e.g. uvicorn: `uvicorn backend.services.retrieval_api:create_app`)
    """

    return app
