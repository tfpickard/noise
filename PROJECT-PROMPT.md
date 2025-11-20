Build a complete, production-ready "Visual Noise Museum" web application using absolute bleeding-edge tech stack as of November 2025. This includes a modern Python backend with database and API. The frontend must work fully offline/standalone, but gains enhanced features when connected to the backend.

FRONTEND STACK (BLEEDING EDGE):

- React 19 with React Compiler enabled
- Next.js 15+ with App Router
- TypeScript 5.7+
- Bun as runtime and package manager
- Biome for linting and formatting
- Tailwind CSS v4+
- Framer Motion for animations
- Canvas API with OffscreenCanvas for performance
- WebGPU compute shaders for heavy calculations (with Canvas fallback)
- Modern CSS: @container queries, :has(), view transitions API
- IndexedDB for offline storage of user patterns
- Must work in modern browsers (Chrome 120+, Firefox 120+, Safari 17+)

BACKEND STACK (BLEEDING EDGE):

- Python 3.13+ with modern type hints
- FastAPI 0.115+ with full async/await
- Pydantic v2.9+ for data validation
- SQLAlchemy 2.0+ with async engine
- PostgreSQL 16+ with pgvector extension for similarity search
- Redis 7+ for caching and rate limiting
- Alembic for database migrations
- uv for Python package management (not pip/poetry)
- Ruff for linting and formatting (not pylint/black)
- Pytest with async support
- Docker with multi-stage builds
- Structured logging with structlog

DATABASE SCHEMA:

- patterns table: saved noise configurations with parameters
- users table: optional authentication (email/OAuth)
- votes table: likes/favorites for patterns
- collections table: curated galleries
- embeddings table: vector embeddings for pattern similarity
- analytics table: aggregate stats on popular parameters
- sessions table: real-time collaboration sessions
- exports table: track generated images

API ARCHITECTURE:

- RESTful API with FastAPI
- WebSocket endpoints for real-time features
- GraphQL endpoint using Strawberry (optional but nice)
- Rate limiting with Redis
- API versioning (/api/v1/)
- JWT authentication (optional, graceful degradation)
- CORS configured for frontend
- OpenAPI/Swagger docs auto-generated

OFFLINE-FIRST ARCHITECTURE:
Frontend works completely standalone:

- All exhibits functional without backend
- Settings saved to localStorage
- Pattern configurations saved to IndexedDB
- Export functionality works offline
- Progressive enhancement when backend available

Backend enhances with:

- Cloud sync of saved patterns across devices
- Public pattern gallery with community creations
- Social features: like, favorite, share
- Pattern similarity search (find similar noise configs)
- Collaboration: real-time shared canvas sessions
- Analytics dashboard of popular parameters
- Preset library from community
- Pattern versioning and history
- High-resolution server-side rendering for large exports

REQUIRED BACKEND ENDPOINTS:

1. PATTERN MANAGEMENT
POST /api/v1/patterns - Save a pattern configuration
GET /api/v1/patterns/{id} - Get pattern by ID
GET /api/v1/patterns/user/{user_id} - Get user's patterns
PUT /api/v1/patterns/{id} - Update pattern
DELETE /api/v1/patterns/{id} - Delete pattern
GET /api/v1/patterns/discover - Discover feed with pagination

2. SOCIAL FEATURES
POST /api/v1/patterns/{id}/like - Like a pattern
DELETE /api/v1/patterns/{id}/like - Unlike
GET /api/v1/patterns/trending - Trending patterns (Redis cached)
POST /api/v1/patterns/{id}/fork - Fork/remix a pattern
GET /api/v1/patterns/{id}/forks - Get pattern genealogy

3. SIMILARITY SEARCH
POST /api/v1/patterns/similar - Find similar patterns via pgvector
POST /api/v1/patterns/{id}/embedding - Generate embedding from pattern

4. COLLECTIONS
POST /api/v1/collections - Create curated collection
GET /api/v1/collections/{id} - Get collection with patterns
PUT /api/v1/collections/{id}/patterns - Add patterns to collection
GET /api/v1/collections/featured - Featured collections

5. ANALYTICS
GET /api/v1/analytics/popular-parameters - Most used parameter ranges
GET /api/v1/analytics/exhibit-usage - Which exhibits are most popular
GET /api/v1/analytics/trends - Parameter trends over time

6. REAL-TIME COLLABORATION
WS /api/v1/collaborate/{session_id} - WebSocket for shared canvas
POST /api/v1/sessions - Create collaboration session
GET /api/v1/sessions/{id} - Get session state

7. EXPORT SERVICE
POST /api/v1/export/render - Server-side high-res render (8K+)
GET /api/v1/export/{id} - Get rendered export
POST /api/v1/export/video - Generate animated video from pattern

8. AUTHENTICATION (OPTIONAL)
POST /api/v1/auth/register - Create account
POST /api/v1/auth/login - Login (JWT)
POST /api/v1/auth/refresh - Refresh token
GET /api/v1/auth/me - Get current user

FRONTEND FEATURES (BACKEND-ENHANCED):

1. OFFLINE DETECTION

- Detect network status automatically
- Show badge indicating online/offline mode
- Queue writes when offline, sync when back online
- Conflict resolution for patterns edited offline

1. PATTERN GALLERY

- Grid view of saved patterns (local + cloud)
- Filter by exhibit type, date, popularity
- Search by description or parameters
- Share patterns via unique URL
- One-click remix/fork functionality

1. DISCOVER PAGE

- Trending patterns from community
- Featured collections by curators
- "Similar to this" recommendations
- Activity feed from followed users (optional)

1. REAL-TIME COLLABORATION

- Generate shareable session link
- Multiple cursors with user names/colors
- Synchronized parameter changes
- Chat sidebar for collaborators
- Session recording/playback

1. ANALYTICS DASHBOARD

- Personal stats: patterns created, exports made
- Global stats: most popular exhibits, parameters
- Heat maps of parameter space exploration
- Your patterns' view/like counts

BACKEND TECHNICAL REQUIREMENTS:

1. PERFORMANCE

- Response times under 100ms for API calls
- WebSocket latency under 50ms
- Redis caching for expensive queries
- Database connection pooling
- Async I/O throughout (no blocking calls)
- Background tasks with Celery or FastAPI BackgroundTasks

1. VECTOR SIMILARITY

- Generate embeddings from pattern parameters using sklearn
- Store in pgvector with HNSW index
- Sub-second similarity search over 100k+ patterns
- Cosine similarity for pattern matching

1. RATE LIMITING

- IP-based limits: 100 req/min for anonymous
- User-based limits: 1000 req/min for authenticated
- Stricter limits on export/render endpoints
- Redis-backed sliding window counter

1. SECURITY

- JWT with short expiration (15min) and refresh tokens
- CORS properly configured
- SQL injection prevention via SQLAlchemy ORM
- Input validation with Pydantic
- Rate limiting on authentication endpoints
- HTTPS only in production
- Content Security Policy headers

1. OBSERVABILITY

- Structured logging with correlation IDs
- Request tracing with OpenTelemetry
- Metrics: request latency, error rates, DB query times
- Health check endpoints (/health, /readiness)
- Integration with Sentry for error tracking

DATABASE SCHEMA (DETAIL):

```sql
-- patterns table
CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NULL,
    exhibit_type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    description TEXT,
    parameters JSONB NOT NULL, -- full config
    seed BIGINT,
    thumbnail_url VARCHAR(500),
    is_public BOOLEAN DEFAULT true,
    likes_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    forked_from UUID REFERENCES patterns(id) NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_patterns_exhibit ON patterns(exhibit_type);
CREATE INDEX idx_patterns_user ON patterns(user_id);
CREATE INDEX idx_patterns_public ON patterns(is_public) WHERE is_public = true;
CREATE INDEX idx_patterns_params ON patterns USING gin(parameters);

-- embeddings for similarity search
CREATE TABLE pattern_embeddings (
    pattern_id UUID PRIMARY KEY REFERENCES patterns(id) ON DELETE CASCADE,
    embedding vector(128), -- pgvector type
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings_vector ON pattern_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- users table (optional auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- likes/favorites
CREATE TABLE pattern_likes (
    pattern_id UUID REFERENCES patterns(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (pattern_id, user_id)
);

-- collections
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE collection_patterns (
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    pattern_id UUID REFERENCES patterns(id) ON DELETE CASCADE,
    position INTEGER,
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (collection_id, pattern_id)
);

-- analytics events
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    pattern_id UUID REFERENCES patterns(id) NULL,
    user_id UUID REFERENCES users(id) NULL,
    session_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analytics_type_time ON analytics_events(event_type, created_at DESC);
```

DEPLOYMENT ARCHITECTURE:

```
Frontend:
- Vercel Edge Runtime or Cloudflare Pages
- Global CDN distribution
- Automatic HTTPS
- Preview deployments per PR

Backend:
- Docker containers
- Deploy to Railway, Render, or Fly.io
- PostgreSQL managed instance
- Redis managed instance
- Horizontal scaling ready
- CI/CD with GitHub Actions

Docker Compose for local development:
- PostgreSQL with pgvector
- Redis
- FastAPI backend (hot reload)
- Next.js frontend (hot reload)
```

CODE ORGANIZATION:

```
project/
├── frontend/                  # Next.js app
│   ├── app/                  # App Router
│   │   ├── page.tsx          # Home/gallery
│   │   ├── exhibit/[id]/     # Individual exhibit
│   │   ├── discover/         # Public gallery
│   │   ├── collaborate/      # Real-time sessions
│   │   └── api/              # API route handlers
│   ├── components/
│   │   ├── exhibits/         # Exhibit components
│   │   ├── ui/               # Shared UI
│   │   └── patterns/         # Pattern management
│   ├── lib/
│   │   ├── api-client.ts     # Backend API client
│   │   ├── offline-db.ts     # IndexedDB wrapper
│   │   └── sync-manager.ts   # Offline sync logic
│   └── workers/              # Web Workers for compute
│
├── backend/                   # FastAPI app
│   ├── app/
│   │   ├── main.py           # FastAPI app setup
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── patterns.py
│   │   │   │   ├── collections.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── collaborate.py
│   │   │   └── deps.py       # Dependencies
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── pattern_service.py
│   │   │   ├── embedding_service.py
│   │   │   └── render_service.py
│   │   ├── db/
│   │   │   ├── session.py    # Async DB session
│   │   │   └── base.py
│   │   └── core/
│   │       ├── config.py     # Settings (Pydantic)
│   │       ├── security.py   # JWT, auth
│   │       └── cache.py      # Redis cache
│   ├── alembic/              # Migrations
│   ├── tests/
│   └── pyproject.toml        # uv config
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

PROGRESSIVE ENHANCEMENT EXAMPLES:

1. Saving Patterns:

- Offline: Save to IndexedDB only
- Online: Save to IndexedDB + sync to backend
- Conflict: Show merge UI if edited in multiple places

1. Pattern Gallery:

- Offline: Show locally saved patterns only
- Online: Merge local + cloud patterns, show community feed

1. Export:

- Offline: Client-side canvas export (limited resolution)
- Online: Option for server-side 8K+ rendering

1. Collaboration:

- Offline: Not available (gracefully hidden)
- Online: Real-time multi-user editing via WebSocket

1. Similarity Search:

- Offline: Basic parameter-based sorting
- Online: ML-powered semantic similarity via pgvector

BACKEND CODE QUALITY:

- Type hints throughout (Python 3.13 syntax)
- Async/await consistently used
- Pydantic v2 for all data validation
- SQLAlchemy 2.0 async patterns
- Proper error handling with custom exceptions
- Comprehensive test coverage (pytest-asyncio)
- API documentation auto-generated (OpenAPI)
- Ruff configured (pyproject.toml)
- Docker health checks
- Graceful shutdown handling

MONITORING & DEBUGGING:

- Structured logs (JSON format) with correlation IDs
- Request/response logging middleware
- Database query logging in dev
- Redis operation logging
- WebSocket connection tracking
- Exception tracking with Sentry
- Performance profiling endpoints (dev only)

DELIVERABLES:

1. Complete Next.js 15+ frontend (standalone functional)
1. Complete FastAPI backend with all endpoints
1. PostgreSQL schema with migrations
1. Docker Compose for local development
1. Production deployment configs
1. Comprehensive API documentation
1. Frontend-backend integration guide
1. Offline-first sync strategy documentation
1. README with full setup for both stacks
1. Example .env files for configuration

The goal: A technically sophisticated, production-ready full-stack application that works beautifully offline but becomes even more powerful when connected. Showcase bleeding-edge web and backend technologies with real-world features like collaboration, social discovery, and ML-powered recommendations.
