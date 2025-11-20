# Visual Noise Museum 🎨

A production-ready, bleeding-edge full-stack web application for exploring and creating procedural noise patterns. Built with the latest technologies as of November 2025.

## 🚀 Tech Stack

### Frontend (Bleeding Edge)
- **Next.js 15+** with App Router
- **React 19** with React Compiler enabled
- **TypeScript 5.7+** for type safety
- **Bun** as runtime and package manager
- **Biome** for linting and formatting (faster than ESLint)
- **Tailwind CSS v4** for styling
- **Framer Motion** for animations
- **Canvas API** with OffscreenCanvas for performance
- **IndexedDB** for offline storage
- **Modern CSS**: Container queries, `:has()`, View Transitions API

### Backend (Bleeding Edge)
- **Python 3.13+** with modern type hints
- **FastAPI 0.115+** with full async/await
- **Pydantic v2.9+** for data validation
- **SQLAlchemy 2.0+** with async engine
- **PostgreSQL 16+** with pgvector extension
- **Redis 7+** for caching and rate limiting
- **Alembic** for database migrations
- **uv** for Python package management
- **Ruff** for linting and formatting
- **Structured logging** with structlog

## ✨ Features

### Offline-First Architecture
- Works completely standalone without backend
- All exhibits functional offline
- Settings saved to localStorage
- Pattern configurations saved to IndexedDB
- Export functionality works offline
- Automatic sync when backend available

### Backend-Enhanced Features
- Cloud sync of saved patterns across devices
- Public pattern gallery with community creations
- Social features: like, favorite, share
- Pattern similarity search using vector embeddings
- Real-time collaboration sessions via WebSocket
- Analytics dashboard of popular parameters
- High-resolution server-side rendering

### Noise Generation Exhibits
- **Perlin Noise**: Classic smooth gradient noise
- **Simplex Noise**: Improved Perlin with better performance
- **Worley Noise**: Cellular patterns (Voronoi)
- **FBM**: Fractional Brownian Motion
- **Turbulence**: Chaotic high-frequency patterns
- **Marble**: Sine-distorted textures

## 🏗️ Project Structure

```
.
├── frontend/                 # Next.js application
│   ├── app/                 # App Router pages
│   │   ├── exhibit/[id]/   # Individual exhibit pages
│   │   ├── discover/       # Public gallery
│   │   └── page.tsx        # Home page
│   ├── components/          # React components
│   │   ├── exhibits/       # Noise generation components
│   │   └── ui/             # Shared UI components
│   ├── lib/                # Utilities
│   │   ├── api-client.ts   # Backend API client
│   │   ├── offline-db.ts   # IndexedDB wrapper
│   │   ├── sync-manager.ts # Offline sync logic
│   │   └── noise-generator.ts # Noise algorithms
│   └── workers/            # Web Workers
│
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   │   ├── patterns.py
│   │   │   ├── collections.py
│   │   │   ├── analytics.py
│   │   │   └── sessions.py
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── db/             # Database config
│   │   └── core/           # Core utilities
│   ├── alembic/            # Migrations
│   └── tests/              # Tests
│
└── docker-compose.yml       # Docker setup
```

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended)
- OR manually:
  - Bun 1.0+ (for frontend)
  - Python 3.13+ (for backend)
  - PostgreSQL 16+ with pgvector
  - Redis 7+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd noise

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create .env file
cp .env.example .env

# Install uv
pip install uv

# Install dependencies
uv pip install -r pyproject.toml

# Start PostgreSQL and Redis (via Docker or locally)
# Ensure pgvector extension is installed

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install Bun (if not already installed)
curl -fsSL https://bun.sh/install | bash

# Create .env file
cp .env.example .env.local

# Install dependencies
bun install

# Start development server
bun run dev
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Pattern Management
- `POST /api/v1/patterns/` - Create pattern
- `GET /api/v1/patterns/{id}` - Get pattern
- `PUT /api/v1/patterns/{id}` - Update pattern
- `DELETE /api/v1/patterns/{id}` - Delete pattern
- `GET /api/v1/patterns/` - List patterns

#### Social Features
- `POST /api/v1/patterns/{id}/like` - Like pattern
- `POST /api/v1/patterns/{id}/fork` - Fork pattern
- `GET /api/v1/patterns/trending/top` - Trending patterns

#### Similarity Search
- `POST /api/v1/patterns/similar` - Find similar patterns

#### Collections
- `POST /api/v1/collections/` - Create collection
- `GET /api/v1/collections/{id}` - Get collection
- `GET /api/v1/collections/featured/list` - Featured collections

#### Analytics
- `GET /api/v1/analytics/exhibit-usage` - Exhibit statistics
- `GET /api/v1/analytics/trends` - Trending patterns

#### Collaboration
- `POST /api/v1/sessions/` - Create session
- `WS /api/v1/sessions/ws/{code}` - WebSocket endpoint

## 🗄️ Database Schema

### Core Tables
- **patterns**: Saved noise configurations
- **pattern_embeddings**: Vector embeddings for similarity search
- **users**: User accounts (optional)
- **pattern_likes**: Like/favorite relationships
- **collections**: Curated pattern galleries
- **collaboration_sessions**: Real-time session tracking
- **analytics_events**: Event tracking

## 🎨 Frontend Architecture

### Offline-First Design
1. **Network Detection**: Automatic online/offline detection
2. **Local Storage**: IndexedDB for pattern storage
3. **Sync Queue**: Queue actions when offline
4. **Conflict Resolution**: Merge strategies for offline edits

### State Management
- **React Query**: Server state and caching
- **Zustand**: Client state (if needed)
- **IndexedDB**: Persistent offline storage

### Performance Optimizations
- Canvas rendering with OffscreenCanvas
- Web Workers for heavy calculations
- React Server Components where appropriate
- Automatic code splitting

## 🧪 Testing

### Backend
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend
```bash
cd frontend
bun test
```

## 🚢 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel deploy
```

### Backend (Railway/Render/Fly.io)
```bash
cd backend
# Configure your deployment platform
# Set environment variables
# Deploy using platform CLI
```

### Production Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Development

### Code Quality

#### Backend
```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy app/
```

#### Frontend
```bash
# Lint & format
bun run lint:fix

# Type check
bun run type-check
```

## 📊 Monitoring

- **Logs**: Structured JSON logs via structlog
- **Health Checks**: `/health` and `/readiness` endpoints
- **Metrics**: Request latency, error rates, DB query times
- **Error Tracking**: Sentry integration (optional)

## 🔐 Security

- JWT authentication with refresh tokens
- SQL injection prevention via ORM
- Input validation with Pydantic
- Rate limiting with Redis
- CORS properly configured
- HTTPS in production
- Content Security Policy headers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Noise algorithms inspired by Ken Perlin's work
- Built with amazing open-source tools
- Community contributions welcome!

## 📞 Support

- Issues: GitHub Issues
- Documentation: See docs/ folder
- Community: Discord (TBD)

---

Built with ❤️ using bleeding-edge web technologies