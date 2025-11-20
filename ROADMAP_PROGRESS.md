# Production Implementation Plan

This checklist tracks execution of the production readiness roadmap. Items marked as completed reflect concrete code/config shipped in this repo. Pending items remain planned.

## Data & Services
- [ ] Add background workers for embeddings and render queue with durable broker
- [x] Move state to PostgreSQL 16+ via async SQLAlchemy models and migration
- [x] Wire Redis 7+ client for caching/rate limits (optional fallback in dev)

## API Surface
- [x] Patterns CRUD with forks and likes backed by the database
- [x] Discover/trending feeds with Redis cache fallback
- [ ] Full collections curation flows (ordering, feature flags, permissions)
- [x] Similarity endpoint storing embeddings
- [ ] Export/video render queues with status polling
- [x] JWT auth with refresh flow and /me using persisted users
- [ ] GraphQL endpoint (Strawberry) for unified queries

## Frontend Offline UX
- [ ] IndexedDB-backed pattern/collection persistence
- [ ] Mutation queue with conflict resolution UI
- [ ] Online/offline badge and progressive enhancement toggles

## Security & Governance
- [x] JWT rotation with short-lived access tokens and refresh tokens
- [x] Basic rate limiting guard using Redis sliding window
- [ ] CSP and hardened security headers
- [ ] RBAC for curator/admin tooling and privacy controls

## Observability
- [x] Structured logging with correlation IDs middleware
- [ ] OpenTelemetry tracing + metrics (latency, DB, Redis, websockets)
- [ ] Sentry integration for exception capture

## Quality & Testing
- [ ] Async pytest coverage for services and API
- [ ] Frontend Biome lint/type checks wired in CI

## CI/CD & Ops
- [x] Docker Compose with Postgres/Redis and health checks
- [ ] Multi-stage Dockerfiles and GitHub Actions matrix builds
- [ ] Backup/restore and rollout/rollback playbooks
