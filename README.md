# NEET Platform - Full Stack Monorepo

## Project Structure

```
.
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app factory
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # Database setup
│   │   ├── celery_app.py      # Celery configuration
│   │   └── __init__.py
│   ├── alembic/               # Database migrations
│   │   ├── env.py             # Async migration config
│   │   └── versions/          # Migration files
│   ├── tests/                 # Test suite
│   ├── pyproject.toml         # Poetry dependencies
│   ├── alembic.ini            # Alembic config
│   ├── .env.example           # Environment template
│   └── Dockerfile
├── frontend/                  # React + Vite
│   ├── src/
│   │   ├── main.tsx           # Entry point
│   │   ├── App.tsx            # Root component
│   │   ├── api/
│   │   │   └── client.ts      # Axios client
│   │   ├── index.css
│   │   └── App.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .eslintrc.cjs
│   └── Dockerfile
├── docker-compose.yml         # Local development environment
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend development)
- Poetry (Python dependency management)
- npm (Node package manager)

### Using Docker Compose (Recommended)

```bash
# Copy environment file
cp backend/.env.example backend/.env

# Start all services
docker-compose up

# Services will be available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:5173
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Local Development Setup

**Backend:**

```bash
cd backend

# Install dependencies
poetry install

# Create .env file
cp .env.example .env

# Run migrations
poetry run alembic upgrade head

# Start the API
poetry run uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## Architecture

### Backend (FastAPI)

- **Framework**: FastAPI with async support
- **Database**: PostgreSQL 16 with SQLAlchemy ORM (async)
- **Migrations**: Alembic with async support
- **Task Queue**: Celery with Redis broker
- **Cache**: Redis
- **Authentication**: JWT (HS256) - to be implemented per domain

### Frontend (React + Vite)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **Data Fetching**: React Query + Axios
- **Routing**: React Router v6
- **Linting**: ESLint

### Infrastructure

- **Containers**: Docker & Docker Compose
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **CI/CD**: GitHub Actions

## Domain Structure (To Be Implemented)

The backend follows a domain-separated monolith pattern with 5 domains:

1. **Identity** - Authentication, authorization, user management
2. **Content** - Content creation, management, retrieval
3. **Assessment** - Exam, quiz, test functionality
4. **Intelligence** - Analytics, insights, recommendations
5. **Recovery** - Error handling, data recovery, resilience

Each domain should have its own:
- `routes.py` - API endpoints
- `models.py` - Database models
- `schemas.py` - Pydantic schemas
- `services.py` - Business logic
- `dependencies.py` - Dependency injection

## Development Workflow

### Creating Database Migrations

```bash
cd backend

# Auto-generate migration
poetry run alembic revision --autogenerate -m "Add users table"

# Apply migrations
poetry run alembic upgrade head

# Downgrade
poetry run alembic downgrade -1
```

### Running Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_health.py -v
```

### Linting & Type Checking

```bash
cd backend

# Format code
poetry run black app/ tests/

# Lint
poetry run ruff check app/ tests/

# Type check
poetry run mypy app/

# Fix imports
poetry run ruff check --fix app/ tests/
```

### Frontend Development

```bash
cd frontend

# Type check
npm run type-check

# Lint
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## CI/CD Pipeline

The GitHub Actions CI pipeline includes:

1. **Backend Linting**: Ruff, mypy, Black
2. **Backend Testing**: pytest with 80% coverage gate
3. **Frontend Linting**: ESLint, TypeScript type checking
4. **Frontend Build**: Vite build verification
5. **Docker Build**: Verify images build successfully

Push to `main` or `develop` branches to trigger CI.

## Environment Variables

### Backend (.env)

```
# Database
POSTGRES_USER=neet_user
POSTGRES_PASSWORD=neet_password
POSTGRES_DB=neet_db
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (CHANGE IN PRODUCTION)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Frontend

Configure via `.env` in the frontend directory:

```
VITE_API_URL=http://localhost:8000
```

## Success Criteria

✅ `docker-compose up` starts all services without errors
✅ GET http://localhost:8000/ returns 200 with health status
✅ `alembic revision --autogenerate` runs without errors
✅ Frontend loads at http://localhost:5173
✅ All CI/CD checks pass

## Next Steps

1. Implement domain routers and models
2. Set up authentication (JWT via Identity domain)
3. Create database models and initial migrations
4. Add tests for each domain
5. Implement API endpoints
6. Build frontend components and pages
7. Set up monitoring and logging
8. Deploy to production environment

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Documentation](https://docs.docker.com/)
