# AGENTS.md

## Scope

These instructions apply to the entire Visual Noise Museum repository. This is a full-stack progressive web app showcasing bleeding-edge web technologies with an offline-first architecture.

## General workflow

- Never commit failing code. Run and document the relevant test suite when making changes:
  - Backend: `pytest` with async support
  - Frontend: `bun test` and type checking
- Keep diffs minimal: don't reformat untouched files and avoid sweeping refactors unless the task demands it.
- Write descriptive commit messages ("area: summary") and keep PR titles succinct.
- Prefer small, focused PRs. If a change spans both backend and frontend, describe the cross-service impact in the PR body.
- Always verify the offline-first behavior: features must gracefully degrade when the backend is unavailable.

## Backend (`backend/`)

- Target Python 3.13+ with modern type hints throughout.
- Match the existing FastAPI + SQLAlchemy 2.0 async style.
- Use `uv` for package management (not pip/poetry).
- Use `ruff` for linting and formatting (not pylint/black).
- Always add or update type hints; favor modern Python 3.13+ syntax.
- Keep functions pure where possible; push I/O to service layers.
- Use structured logging with `structlog`; never use `print()`.
- Database migrations live under `backend/alembic`. Every schema change requires a migration plus corresponding SQLAlchemy model updates.
- Tests belong in `backend/tests/` and use pytest-asyncio.
- API responses must be under 100ms; use Redis caching for expensive queries.
- All database operations must use async/await (no blocking I/O).
- Validate all input with Pydantic v2.9+.
- Use FastAPI 0.115+ with full async endpoints.
- Vector embeddings use pgvector with HNSW indexing for sub-second similarity search.
- Rate limiting uses Redis with sliding window counters.

## Frontend (`frontend/`)

- This is a Next.js 15+ App Router application with React 19 and React Compiler enabled.
- Use Bun as the runtime and package manager (not npm/yarn/pnpm).
- Use Biome for linting and formatting (not ESLint/Prettier).
- TypeScript 5.7+ required for all code; export shared types from `lib/`.
- Tailwind CSS v4+ for styling; leverage modern CSS (@container, :has(), view transitions).
- Canvas rendering uses OffscreenCanvas where supported; WebGPU compute shaders with Canvas fallback.
- Animations use Framer Motion.
- All exhibits must work completely offline using IndexedDB for persistence.
- API calls centralized in `lib/api-client.ts`; components should not hit fetch directly.
- Offline sync managed through `lib/sync-manager.ts` with conflict resolution.
- Network status detection must show online/offline badge and queue writes appropriately.
- Run `bun run lint` and type checking when touching code.
- Progressive enhancement: features gracefully degrade without backend, enhance when connected.

## Offline-First Architecture

Critical: The frontend must be fully functional without the backend.

- All noise exhibits work standalone (Canvas API, WebGPU compute).
- Settings persist to localStorage.
- Pattern configurations save to IndexedDB.
- Export functionality works offline (client-side canvas rendering).
- When online, backend enhances with: cloud sync, pattern gallery, social features, similarity search, real-time collaboration, analytics.
- Sync conflicts must have clear resolution UI.
- Show clear indicators when features require backend connectivity.

## Backend API Design

- Follow RESTful conventions under `/api/v1/`.
- All endpoints return consistent JSON structure.
- Use WebSocket at `/api/v1/collaborate/{session_id}` for real-time features.
- Rate limits: 100 req/min anonymous, 1000 req/min authenticated.
- CORS properly configured for frontend origin.
- OpenAPI/Swagger docs auto-generated and kept current.
- JWT authentication optional with graceful degradation.
- Health checks at `/health` and `/readiness`.

## Database

- PostgreSQL 16+ with pgvector extension.
- Use async SQLAlchemy 2.0 patterns exclusively.
- Connection pooling configured for performance.
- Indexes on frequently queried columns (see schema in PROJECT-PROMPT.md).
- JSONB for flexible pattern parameters with GIN indexes.
- Vector embeddings use HNSW index for cosine similarity.

## Performance Requirements

- API response times under 100ms.
- WebSocket latency under 50ms.
- Similarity search over 100k+ patterns in sub-second time.
- Frontend canvas rendering at 60fps minimum.
- Redis caching for trending patterns, analytics aggregates.
- Background tasks for expensive operations (embeddings, server-side renders).

## DevOps / Deployment

- Docker Compose for local development (PostgreSQL + Redis + backend + frontend).
- Multi-stage Dockerfiles: install only runtime deps in final image.
- Frontend deploys to Vercel Edge or Cloudflare Pages.
- Backend deploys to Railway/Render/Fly.io with managed PostgreSQL and Redis.
- Environment variables documented in README.md as single source of truth.
- CI/CD via GitHub Actions.
- Health checks in Docker containers.

## Code Organization

```
project/
├── frontend/           # Next.js 15+ app
│   ├── app/           # App Router pages
│   ├── components/    # React components
│   ├── lib/           # API client, offline DB, sync
│   └── workers/       # Web Workers for compute
├── backend/           # FastAPI app
│   ├── app/
│   │   ├── api/v1/   # Route handlers
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── core/     # Config, security, cache
│   ├── alembic/      # Database migrations
│   ├── tests/        # Pytest suite
│   └── pyproject.toml # uv configuration
└── docker-compose.yml
```

## Testing

- Backend: Full pytest coverage with async fixtures, mocked external services.
- Frontend: Component tests and integration tests for offline/online modes.
- Test offline-first behavior: verify IndexedDB storage, sync queue, conflict resolution.
- Test progressive enhancement: features work offline, enhance online.

## Documentation

- Any new feature or breaking change requires README updates.
- API endpoints must have OpenAPI documentation (auto-generated).
- Inline comments explain "why", not "what"; docstrings for high-level context.
- Document offline/online behavior differences for new features.

## Security

- JWT with short expiration (15min) and refresh tokens.
- Input validation via Pydantic on all endpoints.
- SQL injection prevention via SQLAlchemy ORM (no raw queries).
- Rate limiting on authentication and expensive endpoints.
- CORS, CSP headers properly configured.
- HTTPS only in production.

## Monitoring

- Structured logging with correlation IDs.
- Request/response logging middleware.
- OpenTelemetry for tracing.
- Sentry integration for error tracking.
- Metrics: request latency, error rates, DB query times, WebSocket connections.

## PR Guidelines

- Title: "area: concise summary" (e.g., `backend: add pattern similarity search`).
- Body:
  1. Summary bullet list of changes.
  2. Testing section with commands run and results.
  3. If touching offline-first features, document offline/online behavior.
  4. Performance impact notes for API or rendering changes.
