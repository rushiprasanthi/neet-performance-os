# CHANGELOG

## [Unreleased]

### Added
- **Backend Infrastructure:** FastAPI, Async SQLAlchemy, PostgreSQL setup, Redis integration, Celery scaffolding. Dockerfile configured.
- **Testing:** Pytest framework configured (`conftest.py`) with domain-specific tests (`test_health.py`, `test_identity.py`, `test_profile.py`, `test_subjects.py`). Coverage reporting via `htmlcov`.
- **Identity Domain:** - `User`, `Profile`, `Role`, `Permission`, `AuditLog` models (Alembic `001`, `002`).
  - Auth routes (`/register`, `/login`, `/refresh`, `/logout`).
  - Profile routes (`GET /me`, `GET /profile`, `PATCH /profile`).
- **Content Domain:**
  - `Subject` model with active partial indexing (Alembic `003`).
  - Subject CRUD routes secured by `subject.*` RBAC permissions.
- **Frontend Scaffolding:**
  - React 18, Vite, TypeScript, Tailwind CSS. Dockerfile configured.
  - Axios client (`api/client.ts`) with automatic token injection.
  - Global authentication state (`authStore.ts`).
  - UI Layouts: `MainLayout.tsx`, `ProtectedRoute.tsx`.
- **Frontend Views:**
  - `LoginPage.tsx`, `RegisterPage.tsx`.
  - `DashboardPage.tsx`.
  - `SubjectsPage.tsx`.

### Changed
- **Security:** Added Redis sliding-window rate limit (5 attempts / 15 minutes) for login.
- **Auth Flow:** Temporarily implemented auto-email-verification for MVP rollout.

### Fixed
- Fixed Starlette CORS crash by dynamically switching to regex when wildcards are required in environments.