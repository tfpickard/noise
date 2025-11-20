# Visual Noise Museum

This repository provides a dual-stack prototype for the Visual Noise Museum. It ships a FastAPI 0.115+ backend with async endpoints and a Next.js 15+/React 19 frontend scaffolded for offline-first rendering and progressive enhancement.

## Backend

- FastAPI app in `backend/app/main.py` exposes REST endpoints under `/api/v1/` with health probes at `/health` and `/readiness`.
- Async SQLAlchemy models target PostgreSQL 16+ with pgvector (see `backend/app/models/` and the Alembic migration in `backend/alembic/versions`).
- Redis powers caching and rate limiting; see `app/api/deps.py` for the sliding window guard.
- Pydantic v2 schemas live in `backend/app/schemas/`, and routers in `backend/app/api/v1/` mirror the required surface (patterns, collections, analytics, similarity, sessions, exports, auth, and collaboration websocket).
- Structured logging with correlation IDs via `structlog`; configure settings through `app/core/config.py`.

### Running

```bash
cd backend
# install deps
uv sync

# run migrations
DATABASE_URL=postgresql+asyncpg://noise:noise@localhost:5432/noise uv run alembic upgrade head

# start API
uv run uvicorn app.main:app --reload --port 8000
```

## Frontend

- Next.js App Router shell in `frontend/app/` targets React 19 with Framer Motion accents and modern CSS (container queries, `:has`).
- API access is centralized in `frontend/lib/api-client.ts` and offline storage utilities live in `frontend/lib/offline-db.ts` and `frontend/lib/sync-manager.ts`.
- Styling hook in `app/globals.css` embraces Tailwind-friendly utility composition.

### Running

```bash
cd frontend
bun install
bun run dev
```

## Offline-first notes

- Patterns save immediately to localStorage via IndexedDB-friendly helpers and sync to the backend when connectivity is restored.
- Collaboration and similarity features are stubbed to gracefully degrade when offline; WebSocket endpoints echo payloads for local testing.

## Production checklist

- See `ROADMAP_PROGRESS.md` for the actively maintained production checklist and feature status.

## Production readiness roadmap

- **Data + services**: Replace the in-memory store with PostgreSQL 16+ (pgvector) and Redis 7+; add Alembic migrations, seeded fixtures, and connection pooling; enable background workers for embeddings/renders and a rate-limit layer aligned to anonymous/authenticated limits.
- **API surface**: Finish JWT + refresh token auth with optional OAuth, enforce API versioning, add fork/remix genealogy, trending cache, similarity search via pgvector HNSW, and export/video render queues with status polling.
- **Frontend offline UX**: Implement IndexedDB persistence for patterns/collections, queued mutations with conflict resolution UI, online/offline badges, and progressive enhancement toggles for collaboration, similarity, and server renders.
- **Performance + rendering**: Ship WebGPU compute shaders with Canvas/OffscreenCanvas fallback, streaming/lazy data fetches, optimistic UI updates, and server-driven pagination for galleries and discover feeds.
- **Security + governance**: Add CSP/secure headers, JWT rotation with short-lived access tokens, per-endpoint rate limits (stricter for exports/auth), input validation hardening, RBAC for curator/admin tools, and privacy controls for public galleries.
- **Observability**: Integrate OpenTelemetry tracing, metrics (latency, error rates, DB/Redis timing, WebSocket connections), Sentry for error capture, structured logs with correlation IDs, and health/readiness probes per container.
- **Quality + testing**: Expand pytest (async) and frontend Biome/type-checked suites; add contract tests for offline/online sync, WebSocket collaboration, similarity search latency, and export throughput; include load tests for <100ms p99 APIs.
- **CI/CD + release**: Configure GitHub Actions for lint/tests/builds, Docker multi-stage images with health checks, provenance/SBOM generation, environment matrices (dev/stage/prod), backup/restore drills for Postgres/Redis, and rollout/rollback playbooks.

## Testing

- Backend: `uv run pytest` (async ready)
- Frontend: `bun run check` (Biome) and `bun run lint`

## Environment

- Python 3.13+, Bun runtime for the frontend.
- Replace the in-memory store with PostgreSQL 16+ (pgvector) and Redis 7+ for production deployments.
