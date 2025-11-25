# Client Build Setup (Open WebUI v0.6.36 + Citation Fixes)

## Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker (if running backend via Docker) or Python venv for backend
- For GPU options, ensure appropriate drivers and CUDA support.

## Installation
1. Clone this repo: `git clone <client_repo_url>`
2. Install frontend deps:
   ```bash
   cd client-repo
   npm install
   ```
3. Build frontend once (optional but recommended to validate):
   ```bash
   npm run build
   ```
   *The `scripts/prepare-pyodide.js` honors `SKIP_PYODIDE_FETCH=1` if you want to avoid downloading Pyodide packages (set env var before `npm run build`).*

4. Backend setup options:
   - **Docker Compose (Coolify)**: use `docker-compose.coolify.yaml` (or standard `docker-compose.yaml`) with your env vars (OpenAI keys, Qdrant, etc.).
   - **Local Python**: create a venv in `backend/`, install `pip install -r backend/requirements.txt`, run `./start.sh` or `python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080`.

## Running
- `npm run dev` to start Vite dev server (frontend hitting backend on port 8080).
- For production: use Docker (build/push image) or run `npm run build` + backend server.
- Coolify: point service to this repo, compose file `docker-compose.coolify.yaml`, ensure env vars (Qdrant, OPENAI, secret keys) are set.

## Deploy Notes
- The frontend build uses `SKIP_PYODIDE_FETCH=1` in Dockerfile to avoid network access issues during build; remove or change if you need Pyodide packages.
- `docker-compose.coolify.yaml` exposes port 8080 and sets required env vars (OPENAI, Qdrant, secret keys).

## Testing
- Run `npm run build` to verify frontend compiles.
- Optional: `npm run dev` for local manual tests.
- Backend: run `pytest` or `uvicorn` smoke tests as needed.
