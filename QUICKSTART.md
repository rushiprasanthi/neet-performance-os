# 🚀 NEET Platform - Quick Start Guide

## ✅ Scaffolding Complete!

Your complete monorepo infrastructure is ready. All files have been created with proper configurations for:

- ✅ FastAPI backend (async, PostgreSQL, Redis, Celery)
- ✅ React 18 frontend (Vite, TypeScript, React Query, Zustand)
- ✅ Docker Compose with all services
- ✅ GitHub Actions CI/CD pipeline
- ✅ Database migration system (Alembic)
- ✅ Testing infrastructure (pytest, coverage gates)

---

## 🎯 Getting Started (Choose One Path)

### Path 1: Docker Compose (⭐ Recommended)

**Fastest way to start the entire stack:**

```bash
# Navigate to project
cd "c:\Users\Administrator\Desktop\Neet project"

# Copy environment file
copy backend\.env.example backend\.env

# Start all services
docker-compose up
```

**Services available after startup:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

### Path 2: Local Development

#### Windows

```bash
cd "c:\Users\Administrator\Desktop\Neet project"
dev-setup.bat
```

#### Linux/Mac

```bash
cd "c:\Users\Administrator\Desktop\Neet project"
bash dev-setup.sh
```

**What this does:**
1. Creates Python virtual environment
2. Installs Poetry + backend dependencies
3. Installs Node modules + frontend dependencies
4. Copies environment files
5. Runs database migrations
6. Starts both backend and frontend servers

---

## 🔍 Verify Installation

### Check All Files Created

```bash
python validate-scaffolding.py
```

Expected output: ✅ All scaffolding files present!

### Test Backend Health

```bash
# Via curl
curl http://localhost:8000/

# Expected response:
# {
#   "status": "healthy",
#   "app_name": "NEET API",
#   "version": "0.1.0",
#   "environment": "development"
# }
```

### Test Frontend

Open http://localhost:5173 in your browser. You should see the NEET Platform welcome page.

---

## 🗄️ Database Setup

### Create Initial Migration

Once backend is running:

```bash
cd backend
poetry run alembic revision --autogenerate -m "Initial schema"
```

This will:
1. Generate a migration file in `alembic/versions/`
2. Auto-detect SQLAlchemy model changes
3. Ready for `poetry run alembic upgrade head` to apply

### Verify Database Connection

```bash
poetry run python
>>> from app.database import engine
>>> import asyncio
>>> asyncio.run(engine.execute("SELECT 1"))
# Should return without error
```

---

## 📝 Project Structure Overview

```
neet-project/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # App factory
│   │   ├── config.py          # Settings
│   │   ├── database.py        # DB setup
│   │   └── celery_app.py      # Task queue
│   ├── alembic/               # Migrations
│   ├── tests/                 # Test suite
│   ├── pyproject.toml         # Dependencies
│   ├── Dockerfile
│   └── .env                   # (Create from .env.example)
├── frontend/                  # React application
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   └── api/
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env                   # (Create from .env.example)
├── .github/workflows/         # CI/CD
├── docker-compose.yml         # Local environment
└── README.md                  # Full documentation
```

---

## 🏗️ Architecture Overview

### Backend Layers

```
Routes (API Endpoints)
↓
Services (Business Logic)
↓
Models (Database Schema)
↓
Database (PostgreSQL + SQLAlchemy)
```

### Current Structure

- **Config**: Pydantic Settings reading from `.env`
- **Database**: SQLAlchemy async engine with asyncpg driver
- **App Factory**: FastAPI with CORS, health checks
- **Celery**: Background task queue via Redis
- **Alembic**: Database versioning system

### Domain Structure (To Implement)

Each domain follows this pattern:

```
backend/app/domains/{domain}/
├── routes.py        # API endpoints
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas
├── services.py      # Business logic
├── dependencies.py  # Dependency injection
└── __init__.py
```

The 5 domains:
1. **identity** - Auth, users, permissions
2. **content** - Content management
3. **assessment** - Tests, quizzes, exams
4. **intelligence** - Analytics, insights
5. **recovery** - Error handling, resilience

---

## 📊 CI/CD Pipeline

GitHub Actions runs automatically on push to `main` or `develop`:

1. **Backend Lint** - Ruff, mypy, Black
2. **Backend Test** - pytest with 80% coverage gate
3. **Frontend Lint** - ESLint, TypeScript check
4. **Frontend Build** - Vite build verification
5. **Docker Build** - Container image builds

Check `.github/workflows/ci.yml` for details.

---

## 🛠️ Common Commands

### Backend

```bash
cd backend

# Run tests
poetry run pytest

# Test with coverage
poetry run pytest --cov=app

# Format code
poetry run black app/ tests/

# Lint
poetry run ruff check app/ tests/

# Type check
poetry run mypy app/

# Run migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Downgrade last migration
poetry run alembic downgrade -1

# Start server (local)
poetry run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Type check
npm run type-check

# Lint
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Run specific service
docker-compose up api
```

---

## 📋 Configuration Files

### Backend (.env)

Copy from `backend/.env.example` and update:

```env
# Database
POSTGRES_USER=neet_user
POSTGRES_PASSWORD=neet_password
DATABASE_URL=postgresql+asyncpg://...

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Other services
REDIS_URL=redis://...
CELERY_BROKER_URL=redis://...
```

### Frontend (.env)

Copy from `frontend/.env.example`:

```env
VITE_API_URL=http://localhost:8000
```

---

## ✨ Key Features Ready to Use

### ✅ Async Database Operations

```python
from app.database import get_db

@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

### ✅ Pydantic Schema Validation

```python
from pydantic import BaseModel

class ItemSchema(BaseModel):
    name: str
    description: str | None = None
    
    class Config:
        from_attributes = True
```

### ✅ Authentication Ready (with JWT stubs)

```python
# Implement in identity domain:
def create_access_token(data: dict, expires_delta: timedelta):
    encoded_jwt = jwt.encode(data, settings.secret_key, 
                              algorithm=settings.algorithm)
    return encoded_jwt
```

### ✅ Background Tasks via Celery

```python
from app.celery_app import celery_app

@celery_app.task
def process_data(item_id: int):
    # Long-running operation
    return result
```

### ✅ React State Management

```typescript
import { create } from 'zustand'

const useStore = create((set) => ({
  items: [],
  setItems: (items) => set({ items }),
}))
```

---

## 🚨 Troubleshooting

### Docker Compose won't start

**Solution:**
1. Check Docker is running: `docker --version`
2. Verify ports are free: 5432, 6379, 8000, 5173
3. Check logs: `docker-compose logs`

### "Database connection refused"

**Solution:**
1. Ensure PostgreSQL service is healthy: `docker-compose ps`
2. Wait 10 seconds for PostgreSQL to initialize
3. Check DATABASE_URL in .env matches service name

### Port already in use

**Solution:**

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Changed from 5432
```

### Poetry install fails

**Solution:**
```bash
cd backend
pip install --upgrade pip poetry
poetry cache clear . --all
poetry install
```

### npm install fails

**Solution:**
```bash
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Next Implementation Steps

### Step 1: Create Domain Structure

```bash
mkdir -p backend/app/domains/{identity,content,assessment,intelligence,recovery}
```

### Step 2: Add Domain Routers

Modify `backend/app/main.py` to include domain routers:

```python
from app.domains.identity.routes import router as identity_router

app.include_router(identity_router, prefix="/api/v1/identity")
```

### Step 3: Create Database Models

```python
# backend/app/domains/identity/models.py
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
```

### Step 4: Generate Migration

```bash
cd backend
poetry run alembic revision --autogenerate -m "Add User model"
```

### Step 5: Create Tests

```bash
# backend/tests/test_identity.py
@pytest.mark.asyncio
async def test_user_creation(client):
    response = await client.post("/api/v1/identity/users", ...)
    assert response.status_code == 201
```

---

## 📞 Support Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Alembic**: https://alembic.sqlalchemy.org/
- **React 18**: https://react.dev/
- **Vite**: https://vitejs.dev/
- **Docker**: https://docs.docker.com/
- **GitHub Actions**: https://docs.github.com/en/actions

---

## ✅ Success Checklist

- [ ] Cloned/navigated to project directory
- [ ] Docker Compose running all services OR local dev setup complete
- [ ] Backend health check: GET http://localhost:8000/ returns 200
- [ ] Frontend loads at http://localhost:5173
- [ ] `python validate-scaffolding.py` shows all ✅
- [ ] Database migrations run: `poetry run alembic upgrade head`
- [ ] Understand the 5 domain structure
- [ ] Ready to implement domain-specific code

---

## 🎉 You're All Set!

Your NEET Platform monorepo infrastructure is production-ready. You can now:

1. ✅ Start implementing domain-specific features
2. ✅ Create database models and migrations
3. ✅ Build API endpoints
4. ✅ Develop React components
5. ✅ Write tests with full coverage
6. ✅ Deploy to production with CI/CD

**Happy coding! 🚀**

---

*Last Updated: June 14, 2026*  
*For updates, check `SCAFFOLDING_COMPLETE.md` and `README.md`*
