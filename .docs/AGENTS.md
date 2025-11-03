# Repository Guidelines

## Project Structure & Module Organization
Open WebUI pairs a SvelteKit UI with a FastAPI backend:
- `src/` holds Svelte routes and shared modules in `src/lib/...`; UI components live in PascalCase folders and static assets in `static/`.
- `backend/open_webui/` houses API routers, services, and migrations, with helpers under `.../internal` and `.../utils`.
- `backend/open_webui/test/` mirrors the router layout for pytest suites, while fixtures live in `test/test_files/`.
- `cypress/`, `docs/`, `scripts/`, and deployment manifests (`docker-compose*.yaml`, `kubernetes/`) cover e2e specs and ops tooling.
- Create new documentation under `docs/codex/` for consistency.

## Build, Test, and Development Commands
Install dependencies with `npm install`. Run `npm run dev` (or `npm run dev:5050`) for Vite hot reload, and pair it with `backend/dev.sh` for live FastAPI reloads. `npm run build` creates a production bundle; `npm run preview` serves that bundle locally. Container users can run `make install` or `docker-compose up -d`, and `run.sh` rebuilds plus runs a local Docker image. Lint before committing with `npm run lint` or the focused `lint:frontend`, `lint:backend`, and `lint:types` scripts.

## Coding Style & Naming Conventions
Prettier governs formatting: tabs, single quotes, 100-character width, and LF endings (`npm run format` or `npm run format:backend`). Follow ESLint + TypeScript recommendations, keep Svelte components PascalCase, and store modules camelCase (e.g., `sessionStore.ts`) under `src/lib/stores`. Python modules in `backend/open_webui` stay snake_case, Black-formatted, and pylint clean.

## Testing Guidelines
Use `npm run test:frontend` for Vitest suites and `npm run cy:open` for Cypress flows in `cypress/e2e`. Backend endpoints rely on pytest; run `python -m pytest backend/open_webui/test -k <pattern>` inside a Python 3.11+ virtualenv, installing `project[all]` extras when integration adapters are needed. Store any new helper scripts under `test/scripts/codex/`, add tests alongside new routers or UI modules, and record manual checks in your PR when automation is not feasible.

## Commit & Pull Request Guidelines
Keep commits focused and use conventional prefixes (`feat:`, `fix:`, `docs:`, etc.) to match PR title expectations. Target the `dev` branch, complete the PR template with a changelog entry, linked issues, screenshots, and manual test notes, and mirror config changes in `docs/` or `.env.example`. First-time contributors should open a Discussion, confirm CLA acceptance, and avoid submitting unchecked AI-generated code.

## Security & Configuration Tips
Copy `.env.example` to `.env` for local secrets; never commit credentials. Adjust the CORS hosts in `backend/dev.sh` when using alternate ports. For deployments, lean on the Docker Compose and Kubernetes manifests and update them alongside config-breaking changes.
