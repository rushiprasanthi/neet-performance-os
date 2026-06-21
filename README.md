

# 🧠 NEET Performance Operating System (NEET POS)

> **Not just a test platform. A performance intelligence system.** > NEET POS explains *why* a student is stuck, exactly *where* they are losing marks, and generates a data-driven recovery plan to fix it.

## 📖 1. Project Overview

NEET aspirants face a compounding problem: they drown in content (lectures, PDFs, PYQs) but lack clarity on what actually controls their score. Existing platforms report outcomes (e.g., "Score = 510") but fail to diagnose the root causes of failure (conceptual gaps vs. execution errors vs. time management).

**NEET POS** is an advanced diagnostic and recovery intelligence platform built on top of high-frequency behavioral data. It captures atomic test-taking events (time spent per question, answer changes, review flags), computes performance analytics asynchronously, and generates highly targeted **Recovery Missions**.

**Target Audience:** NEET (National Eligibility cum Entrance Test) Medical Aspirants in India.

**Business Value:** Radically improves student retention and outcomes by converting failure (a bad mock test) into a structured, actionable recovery plan, entirely eliminating student decision fatigue.

---

## ✨ 2. Key Features

The platform's 25-Feature MVP is meticulously categorized by domain:

### 🔐 Authentication & Identity

* **Secure JWT Sessions:** 15-minute access tokens with 7-day Redis-backed refresh token rotation.
* **Hardened Security:** Argon2id password hashing, constant-time verification, and IP/email rate limiting (5-attempt lockout).
* **RBAC:** Strict multi-actor segregation (Student, Teacher, Admin).

### 📚 Content & Taxonomy

* **Deep Categorization:** Hierarchical taxonomy (Subject → Chapter → Topic) for surgical analytics.
* **Question Engine:** Comprehensive Question Bank supporting Previous Year Questions (PYQs) and tags.
* **Bulk Processing:** Async CSV/XLSX bulk import pipeline with row-by-row validation (Celery).

### ⏱️ Assessment Engine

* **Multiple Formats:** Full 180-question NEET Mocks, Chapter-level Unit Tests, and Mixed Revision.
* **Atomic Tracking:** OMR simulation tracking every answer selection, change, review flag, and millisecond time-delta per question.
* **Resilient State:** Auto-saving test state to Redis every 30 seconds for seamless browser crash recovery.

### 🧠 Performance Intelligence

* **Analytics Pipeline:** Async Celery workers aggregate test data into `SubjectAnalytics`, `ChapterAnalytics`, and `TopicAnalytics`.
* **Weakness Heatmap:** Visual severity mapping (Critical/High/Medium/Low) at the topic level.
* **Composite Performance Score:** Evaluates readiness based on accuracy, consistency, and time-management, rather than just raw marks.

### 🛡️ Recovery System

* **Mistake Vault:** Rule-based heuristic classification of incorrect answers (e.g., Guessing vs. Timing vs. Conceptual gaps).
* **Recovery Missions:** Algorithmic generation of prioritized next-step action plans (e.g., "Revise Thermodynamics," "Retry 20 previous mistakes").

---

## 📸 3. Screenshots

### Login Page

*(Add Screenshot Here - Displaying the clean, rate-limited auth interface)*

### Performance Dashboard

*(Add Screenshot Here - Highlighting the Composite Performance Score and Weakness Heatmap)*

### Active Test / OMR Simulation

*(Add Screenshot Here - Displaying the 180-minute countdown and review-flagging interface)*

### Mistake Vault

*(Add Screenshot Here - Displaying classified errors like "Time Killer" or "Concept Gap")*

---

## 🏗️ 4. Architecture Overview

The backend is structured as a **Domain-Driven Monolith**, designed for clean future extraction into microservices if scaling demands it.

### High-Level Flow

1. **Client Layer:** React/Vite SPA utilizing `Zustand` for active test state (timer, OMR sheet) and `TanStack Query` for caching server state.
2. **API Gateway:** FastAPI async routers with Pydantic payload validation and `get_current_user` dependency injection.
3. **Data Layer:** PostgreSQL (via asyncpg/SQLAlchemy) for transactional integrity; Redis for ephemeral test states, rate-limiting, and refresh tokens.
4. **Async Workers:** Celery tasks intercept test submissions (via Redis broker) to perform heavy analytical aggregations without blocking the user's <300ms API response.

### Authentication Flow (P-002)

* Login validates credentials (Argon2) → Generates short-lived JWT (body) + UUID Refresh Token (HttpOnly Cookie).
* Refresh tokens are stored strictly in Redis (Key: `refresh_token:{uuid} -> {user_id}`).
* Fast revocation on logout by wiping Redis keys without touching the primary database.

---

## 🛠️ 5. Tech Stack

| Layer | Technology | Decision Rationale |
| --- | --- | --- |
| **Frontend** | React 18, Vite, Tailwind CSS | High performance, excellent developer experience. |
| **Client State** | Zustand, TanStack Query | Zustand handles high-freq test events; Query handles API caches. |
| **Backend** | FastAPI (Python 3.11+) | Async-first, automatic OpenAPI docs, Pydantic type-safety. |
| **Database** | PostgreSQL 16 (Asyncpg) | ACID compliance required for financial-grade test attempt data. |
| **ORM & Migrations** | SQLAlchemy 2.0, Alembic | Fully async ORM supporting complex analytical joins. |
| **Cache & Broker** | Redis 7 | Single infra piece serving rate-limits, session cache, and Celery. |
| **Background Tasks** | Celery 5.3 | Offloads heavy analytics & mission generation from main API loop. |
| **Security** | Argon2id, JWT, SlowAPI | OWASP-recommended hashing and rate limiting. |
| **Infrastructure** | Docker, Docker Compose | Containerized local dev mirroring production. |

---

## 📁 6. Folder Structure

```text
neet-project/
├── backend/
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── domains/            # Domain-Driven boundaries
│   │   │   ├── identity/       # Auth, Users, Roles, Profiles
│   │   │   ├── content/        # Subjects, Chapters, Questions
│   │   │   ├── assessment/     # Tests, Attempts, Timer Events
│   │   │   ├── intelligence/   # Dashboard, Heatmap, Analytics
│   │   │   └── recovery/       # Mistakes, Missions
│   │   ├── database.py         # Asyncpg and Redis configs
│   │   ├── celery_app.py       # Async worker configuration
│   │   └── main.py             # FastAPI application entrypoint
│   ├── tests/                  # Pytest suite
│   ├── pyproject.toml          # Poetry dependencies
│   └── Dockerfile              # Backend container spec
├── frontend/
│   ├── src/
│   │   ├── features/           # Domain-aligned React components
│   │   ├── store/              # Zustand state slices
│   │   └── pages/              # Route-level components
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Vite bundler config
├── docs/                       # Project blueprints & state tracking
└── docker-compose.yml          # Local infra orchestration

```

---

## 🚀 7. Installation Guide

### Prerequisites

* Docker & Docker Compose
* Python 3.11+ (if running bare-metal)
* Node.js 18+ & npm

### Quick Start (Docker)

The easiest way to run the entire stack (Postgres, Redis, API, Celery Worker, Frontend).

```bash
# Clone repository
git clone https://github.com/your-org/neet-pos.git
cd neet-pos

# Copy environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Spin up the environment
docker-compose up -d --build

```

* **Frontend UI:** `http://localhost:5173`
* **API Swagger Docs:** `http://localhost:8000/docs`

### Manual Backend Setup (Local Development)

```bash
cd backend
# Setup virtual environment and dependencies
poetry install
# Apply Database Migrations
poetry run alembic upgrade head
# Start FastAPI Server
poetry run uvicorn app.main:app --reload
# Start Celery Worker (in a separate terminal)
poetry run celery -A app.celery_app worker --loglevel=info

```

### Manual Frontend Setup

```bash
cd frontend
npm install
npm run dev

```

---

## ⚙️ 8. Environment Variables

Create a `.env` file in the `backend` directory based on `.env.example`:

| Variable | Description | Required | Example |
| --- | --- | --- | --- |
| `POSTGRES_USER` | DB Username | Yes | `neet_user` |
| `POSTGRES_PASSWORD` | DB Password | Yes | `neet_password` |
| `DATABASE_URL` | SQLAlchemy Async URL | Yes | `postgresql+asyncpg://user:pass@localhost:5432/neet` |
| `REDIS_URL` | Redis Connection | Yes | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT Signing Key | Yes | `super-secret-32-char-string` |
| `CORS_ORIGINS` | Allowed UI URLs | Yes | `["http://localhost:5173"]` |

---

## 🔌 9. API Documentation

Comprehensive auto-generated API docs are available via Swagger UI at `/docs` when the server is running. Key routes:

### Authentication (`/api/v1/auth`)

* `POST /register` - Creates user & profile.
* `POST /login` - Issues JWT & Refresh cookie. Validates against Redis lockout.
* `POST /refresh` - Rotates tokens.
* `POST /logout` - Revokes session centrally in Redis.
* `GET /me` - Returns active session info.

### Content (`/api/v1/content`)

* `GET /subjects` - Fetches domain taxonomy.
* `GET /subjects/{id}/chapters` - Hierarchical drill-down.

### Assessment (`/api/v1/assessment`) *[In Development]*

* `POST /tests/{id}/attempts` - Initializes test state and timer.
* `PATCH /attempts/{id}/answers` - High-frequency bulk upsert for answer events.
* `POST /attempts/{id}/submit` - Synchronous scoring, triggers async Analytics Celery tasks.

---

## 🔒 10. Authentication Flow

This project uses a highly secure, stateless-yet-revocable architecture:

1. **Access Tokens:** Fast, stateless JWTs (15 min TTL) passed via `Authorization: Bearer`.
2. **Refresh Tokens:** Random UUIDs stored in Redis mapped to User IDs (7 day TTL), transmitted strictly via `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
3. **Protection:** The `get_current_user` FastAPI dependency validates the JWT signature and expiration. Rate limiting (SlowAPI + Redis) tracks failed logins, locking out brute-force attacks after 5 attempts.

---

## 🛠️ 11. Development Workflow

* **Backend Quality:** Monitored via `ruff` (linting), `mypy` (strict type-checking), and `black` (formatting).
* **Migrations:** Controlled strictly by `alembic`. Never modify DB schemas without generating a migration revision.
* **Testing:** Pytest with `pytest-asyncio`. Target coverage: `> 80%`.
* **State Management:** We maintain `PROJECT_BRAIN.md`, `PROJECT_STATE.md`, and `CHANGELOG.md` inside `/docs` to track exact implementation context. Update these after major module completions.

---

## 🚢 12. Deployment Guide

### Production Readiness Checklist

* [ ] Change `SECRET_KEY` to a secure vault value.
* [ ] Update `CORS_ORIGINS` to your production domain.
* [ ] Ensure `REFRESH_TOKEN_COOKIE_SECURE=True` is enabled in `routes.py`.
* [ ] Provision managed PostgreSQL (e.g., AWS RDS).
* [ ] Provision managed Redis (e.g., AWS ElastiCache) for session & Celery persistence.
* [ ] Configure Nginx/Caddy as a reverse proxy with SSL termination.

---

## 🗺️ 13. Roadmap

| Milestone | Status | Details |
| --- | --- | --- |
| **M1: Foundation** | ✅ | FastAPI Setup, Dockerization, Postgres+Redis, Pytest. |
| **M2: Identity** | ✅ | Users, Profiles, JWT Flow, RBAC, Redis Rate Limiting. |
| **M3: Taxonomy** | 🔄 | Subjects Engine (Done), Chapters & Topics (In Progress). |
| **M4: Content** | ⏳ | Question Bank CRUD, Tags, Bulk CSV Import. |
| **M5: Assessment** | ⏳ | The Core Loop. Mock creation, Timer Engine, Attempt Tracking. |
| **M6: Intelligence** | ⏳ | Celery Analytics Pipeline, Weakness Heatmap, Mistake Vault. |

---

## 🤝 14. Contributing

1. Clone the repository.
2. Checkout a new feature branch (`git checkout -b feature/F012-topics-engine`).
3. Ensure backend code conforms to `ruff` and `black`.
4. Write `pytest` unit tests for new service logic.
5. Update `docs/PROJECT_STATE.md` to reflect architectural changes.
6. Open a Pull Request for review.

---

## 📄 15. License

Copyright © 2026. All rights reserved.
*(Update with open-source MIT/Apache 2.0 license if electing to open-source the platform).*

---

## 📊 16. Project Statistics

* **Target MVP Features:** 25 Core Features
* **Project Status:** Phase 2 Complete (Infrastructure & Identity fully operational)
* **API Endpoints:** ~15 active, ~35 planned for MVP
* **Data Scale:** The `attempt_answers` table is engineered to handle massive timeseries-like ingestion (projected 13M+ rows annually at minimal scale).

---

## 💡 17. Why This Project Matters

**From an Engineering Perspective:**
NEET POS solves a highly complex data ingestion and processing challenge. Tracking atomic student interactions (milliseconds spent per question, changed answers) generates massive telemetry data.

**Technical Achievements:**

1. **Idempotency & Resilience:** High-frequency auto-saving and idempotent submission endpoints ensure zero data loss during unstable network conditions.
2. **Decoupled Architecture:** Using Celery + Redis ensures that complex multi-table aggregations (identifying "Conceptual Gaps" across thousands of historical attempts) do not degrade the core user experience or block the API event loop.
3. **Domain-Driven Design:** By structuring the monolith into distinct bounded contexts (Identity, Content, Assessment), the codebase achieves the simplicity of a monolith with the organizational scalability of microservices.

---
