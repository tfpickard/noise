# Architecture Documentation

## System Overview

Visual Noise Museum is a full-stack application designed with an **offline-first** architecture that progressively enhances when connected to the backend.

## Frontend Architecture

### Technology Choices

#### Next.js 15 with App Router
- **Server Components** by default for better performance
- **Client Components** (`"use client"`) for interactive features
- **Streaming** and **Suspense** for progressive loading
- **Parallel Routes** for complex layouts

#### React 19 with Compiler
- **Automatic memoization** eliminates need for useMemo/useCallback
- **Improved performance** through compile-time optimizations
- **Better DX** with automatic optimization

#### Bun Runtime
- **Faster package installation** than npm/yarn/pnpm
- **Built-in TypeScript** support
- **Improved performance** for development server
- **Drop-in Node.js replacement**

### State Management Strategy

```
┌─────────────────┐
│   User Action   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Local State    │ ← React Query for server state
│  (Zustand/Hook) │   IndexedDB for offline persistence
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────┐
│Online│  │Offline│
└───┬──┘  └───┬──┘
    │         │
    ▼         ▼
┌──────┐  ┌──────┐
│ API  │  │Queue │
└──────┘  └───┬──┘
              │
              ▼ (when online)
          ┌──────┐
          │ Sync │
          └──────┘
```

### Offline-First Implementation

1. **Detection**: Monitor `navigator.onLine` and `online/offline` events
2. **Storage**: Use IndexedDB for pattern storage
3. **Queue**: Queue write operations when offline
4. **Sync**: Automatically sync when connection restored
5. **Conflict Resolution**: Last-write-wins with timestamps

### Performance Optimizations

#### Canvas Rendering
- Use `OffscreenCanvas` where supported
- Implement Web Workers for heavy calculations
- Cache generated patterns
- Progressive rendering for large canvases

#### Code Splitting
- Route-based splitting (automatic with Next.js)
- Component-level splitting with `dynamic()`
- Library splitting with `optimizePackageImports`

#### Modern CSS Features
- Container queries for responsive components
- `:has()` selector for parent-based styling
- View Transitions API for smooth page transitions
- CSS Grid and Subgrid for layouts

## Backend Architecture

### Technology Choices

#### FastAPI
- **High performance** via async/await
- **Automatic API docs** with OpenAPI
- **Type safety** with Pydantic
- **WebSocket support** built-in

#### Async Stack
- **SQLAlchemy 2.0** with async engine
- **asyncpg** for PostgreSQL
- **aioredis** for Redis
- All I/O operations non-blocking

#### Vector Similarity Search
- **pgvector** extension for PostgreSQL
- **HNSW index** for fast approximate search
- **Cosine similarity** for pattern matching
- Sub-second search over 100k+ patterns

### API Architecture

```
┌──────────────────┐
│   HTTP Request   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Middleware     │
│  - CORS          │
│  - Rate Limiting │
│  - Logging       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   API Router     │
│  - v1/patterns   │
│  - v1/sessions   │
│  - etc.          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Service Layer  │
│  - Business Logic│
│  - Validation    │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────┐
│ DB   │  │Redis │
└──────┘  └──────┘
```

### Database Design

#### Normalization
- **3NF** for core tables
- **Denormalization** for counts (performance)
- **Indexes** on foreign keys and query patterns

#### Vector Embeddings
```python
# Pattern parameters → Vector embedding
parameters = {
    "scale": 0.01,
    "octaves": 4,
    "persistence": 0.5,
    ...
}

# Extract features → 128-dimensional vector
embedding = embedding_service.generate_embedding(parameters)

# Store in pgvector column
embedding: Mapped[Vector] = mapped_column(Vector(128))

# Query similar patterns
similar = db.query(Pattern).order_by(
    PatternEmbedding.embedding.cosine_distance(query_embedding)
).limit(10)
```

#### Caching Strategy
- **Pattern data**: 1 hour TTL
- **Trending patterns**: 5 minutes TTL
- **User sessions**: Session lifetime
- **Analytics**: 15 minutes TTL

### Real-Time Collaboration

```
┌─────────┐         ┌─────────┐
│ Client  │◄───WS──►│ Server  │
│    A    │         │         │
└─────────┘         └────┬────┘
                         │
┌─────────┐         ┌────┴────┐
│ Client  │◄───WS──►│ Manager │
│    B    │         │         │
└─────────┘         └────┬────┘
                         │
┌─────────┐         ┌────┴────┐
│ Client  │◄───WS──►│  Redis  │
│    C    │         │  PubSub │
└─────────┘         └─────────┘
```

### Security Architecture

#### Authentication Flow
```
1. User login → JWT access token (15min) + refresh token (7d)
2. Access token in Authorization header
3. Verify token on each request
4. Refresh when expired
```

#### Rate Limiting
- **Sliding window** counter in Redis
- **IP-based** for anonymous users
- **User-based** for authenticated users
- **Endpoint-specific** limits

#### Input Validation
- **Pydantic** schemas for all inputs
- **SQL injection** prevented by ORM
- **XSS prevention** via Content Security Policy
- **CORS** restricted to known origins

## Data Flow Examples

### Saving a Pattern (Offline)

```
User creates pattern
    ↓
Save to IndexedDB
    ↓
Add to sync queue
    ↓
(Online?) → Yes → Sync to backend
    ↓           ↓
    No          Update local record
    ↓           with remote ID
Wait for         ↓
online event    Mark as synced
```

### Similarity Search

```
User requests similar patterns
    ↓
Generate embedding from pattern
    ↓
Query pgvector with cosine distance
    ↓
Filter by threshold
    ↓
Order by similarity
    ↓
Return top N results
```

### Real-Time Collaboration

```
User A updates parameter
    ↓
Send via WebSocket
    ↓
Server broadcasts to session
    ↓
All clients receive update
    ↓
Update local state
    ↓
Re-render canvas
```

## Scalability Considerations

### Frontend
- **CDN** for static assets
- **Edge functions** for API routes
- **Service Workers** for offline caching
- **Lazy loading** for components

### Backend
- **Horizontal scaling** via stateless design
- **Database connection pooling**
- **Redis for session sharing**
- **Background tasks** for heavy operations
- **Read replicas** for read-heavy workloads

### Database
- **Indexes** on frequently queried columns
- **Partitioning** for large tables (future)
- **VACUUM** and maintenance tasks
- **Connection pooling**

## Monitoring & Observability

### Logging
- **Structured logs** (JSON)
- **Correlation IDs** for request tracing
- **Log levels**: DEBUG, INFO, WARN, ERROR
- **Centralized logging** (optional)

### Metrics
- **Request latency** (p50, p95, p99)
- **Error rates** by endpoint
- **Database query times**
- **Cache hit rates**
- **WebSocket connections**

### Health Checks
- `/health`: Basic liveness check
- `/readiness`: Dependency health check
- Database connectivity
- Redis connectivity

## Future Enhancements

### Planned Features
- [ ] WebGPU compute shaders for noise generation
- [ ] Pattern version history
- [ ] Server-side 8K rendering
- [ ] Video export (animated patterns)
- [ ] GraphQL endpoint (Strawberry)
- [ ] OAuth authentication
- [ ] Pattern recommendations (ML)
- [ ] Mobile app (React Native)

### Technical Debt
- [ ] Comprehensive test coverage
- [ ] E2E testing with Playwright
- [ ] Performance benchmarking
- [ ] Load testing
- [ ] Security audit
