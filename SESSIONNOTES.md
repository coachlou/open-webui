# Session Notes

**Retriever Setup**
- FastAPI retrieval service running at `https://retriever.loudalo.com`, secured with a Bearer token.
- Uses OpenAI `text-embedding-3-small`; matches Qdrant collection `open-webui_knowledge`.
- Custom GPT action schema: `/collections/query`, `bearerAuth`, `collection_ids` constrained to `["open-webui_knowledge"]`.

**Multi-Collection Strategy**
- A single Custom GPT can serve multiple matters if the action allows selecting collection IDs.
- Consider exposing `GET /collections` or listing available collections in instructions to guide selection.

**Metadata Filters to Capture**
- `doc_type` (complaint, deposition, interrogatory, exhibit, motion, order, correspondence, etc.).
- `file_name` / `document_id` to tie chunks back to the source.
- `participants` (witness, author, recipient), `organization`.
- `document_date`, `event_date`, `ingested_at`.
- `issue_tags` / `topic`, `phase` (pleadings, discovery, trial).
- `court`, `project_location`, `version`, `confidential`, `privileged`, `language`.
- Any case-specific fields (e.g., contract section, cost code).

**Future Ingestion Ideas**
- Standalone ingestion service with queue (Redis/SQS) and worker to extract, chunk, embed, and push to Qdrant.
- Maintain metadata/provenance store for dedupe, auditing, and discovery endpoints (`/collections`, `/collections/{id}/documents`).
- Optional storage of original binaries when source stability or compliance requires it.

