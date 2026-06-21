# PROJECT BRAIN: NEET POS Platform

## Product Vision
A specialized preparation platform for the NEET exam (Target Score: 0-720) focusing on Physics, Chemistry, and Biology. The system handles student profiling, rigorous subject/content taxonomy, test-taking emulation, and performance analytics.

## Current Architecture
- **Backend:** Python 3.11 / FastAPI / SQLAlchemy 2.0 (Async) / PostgreSQL / Alembic / Redis.
- **Frontend:** React 18 / Vite / TypeScript / Tailwind CSS.
- **Authentication:** JWT-based. Access tokens in payload, Refresh tokens stored in Redis and issued as `HttpOnly`, `Secure`, `SameSite=strict` cookies.
- **Security:** Argon2 password hashing (offloaded to threadpool), Redis-backed rate-limiting (sliding window for failed logins).
- **RBAC:** Dynamic Role-Based Access Control via database associations (`roles`, `permissions`, `role_permissions`, `user_roles`).
- **Asynchronous Tasks:** Celery (Scaffolded, awaiting SMTP implementation).
- **Testing:** Pytest with extensive test coverage logic (`backend/tests/`, `backend/htmlcov/`).

## Feature Inventory
### Backend Domains
1. **Identity (`app/domains/identity`)**: 
   - Core Auth (Register, Login, Refresh, Logout).
   - Profiles (Target Score, Target Exam Year, Preferred Subjects).
   - RBAC (Admin, Teacher, Student roles & granular permissions).
   - Audit Logging.
2. **Content (`app/domains/content`)**:
   - Subjects (CRUD operations with partial active indexes).

### Frontend Modules
1. **Authentication:** Login, Register pages (`authStore.ts` state management, Axios interceptors).
2. **Dashboard:** Dashboard layout and protected routing (`ProtectedRoute.tsx`, `MainLayout.tsx`).
3. **Content Management:** Subjects page (`SubjectsPage.tsx`, `features/content/api.ts`).

## Dependencies & Infrastructure
- PostgreSQL (Primary Data Store)
- Redis (Token rotation, Refresh token mapping, Login rate-limiting)
- Docker (Backend & Frontend Dockerfiles configured)

## Current Phase & Priorities
- **Phase:** Phase 2 - Core Domain & Content Taxonomy.
- **Current State:** Identity domain and Base Content (Subjects) are implemented and tested.
- **Priority 1 (Active):** Expand Content Domain to handle Taxonomy hierarchy (Chapters and Topics linked to Subjects).
- **Priority 2 (Next):** Build Question Bank Domain (Questions, Options, Difficulty, Types).