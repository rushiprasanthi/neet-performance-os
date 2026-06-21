# PROJECT_STATE.md

## Current Phase
Phase 1 – Foundation (Content Domain)

## Overall Progress
**18% Complete** (Calculated via actual code implementation vs. 25-feature MVP scope).

## Current Status
* **Infrastructure:** Complete
* **Identity Domain:** Complete
* **Authentication:** Complete
* **Authorization (RBAC):** Complete
* **Content Domain (Subjects):** Complete
* **Frontend UI:** Not Started

---

## Completed Modules

### M01 Infrastructure & Project Setup
Status: Complete
* Docker Compose (Postgres, Redis).
* Alembic asynchronous migrations.
* Pytest isolated environment (`NullPool` fix).

### M02 Identity Domain
Status: Complete
* F001 Registration
* F002 Login (JWT + Redis Refresh)
* F003 Profile Management
* F005 RBAC (Role-Based Access Control)
* Audit Logging

### M03 Content Domain (Part 1)
Status: Partially Complete
* F010 Subjects (CRUD, validation, soft-delete).

---

## Current Active Feature
**F011 Chapters (Domain: Content)**

## Current Active Task
**TASK-006: Implement F011 Chapters**

---

## Blockers & Risks
* **Blocker:** None currently.
* **Risk:** Building backend APIs without parallel frontend consumption increases the risk of contract mismatch.

## Current Assessment
* **Architecture:** Complete (Staff-level maturity)
* **Infrastructure:** Complete
* **Backend Identity:** Complete
* **Backend Content:** 33% Complete
* **Frontend:** 1% Complete
* **Assessment Engine:** Not Started
* **Analytics:** Not Started

## Last Updated
Audited: Identity Domain verified. Content Domain (Subjects) verified. Moving to Chapters.
# PROJECT STATE

## Overall Progress
**Estimated Completion:** 27%

## Current Active Phase
**Phase 2:** Core Domain Development (Content & Question Taxonomy)

## Current Active Feature
**Content Taxonomy Expansion:** Extending the content domain beyond base Subjects to include hierarchical Chapters and Topics.

## Current Active Task
- **BACKEND-015:** Draft database schema and SQLAlchemy models for `Chapter` and `Topic` in `backend/app/domains/content/models.py`. Ensure ForeignKey relations to `Subject`.

## Completed Features
### Backend
- Scaffolded FastAPI app with clean domain-driven routing (`identity`, `content`).
- Cross-Origin Resource Sharing (CORS) dynamic wildcard configuration.
- Redis rate limiting (5 attempts / 15 mins) and token lifecycle management.
- Argon2 password hashing & secure cookie (HttpOnly) delivery.
- RBAC framework evaluated efficiently in single SQL queries.
- DB Migrations: `001_initial_identity`, `002_profile_extended`, `003_subjects`.
- Pytest testing suite spanning Auth, Profile, and Subjects.

### Frontend
- Vite + React + TS environment with Tailwind configuration.
- Routing context protected by `ProtectedRoute.tsx`.
- Custom API Client with Axios interceptors (`api/client.ts`).
- Auth State Management (`authStore.ts`).
- Auth Pages (`LoginPage.tsx`, `RegisterPage.tsx`).
- Basic Dashboard & Content Pages (`DashboardPage.tsx`, `SubjectsPage.tsx`).

## Blockers & Risks
- **Email Verification Bypass:** Currently `user.email_verified = True` is hardcoded in the MVP registration flow. Real SMTP Celery tasks must be implemented prior to production rollout.
- **Schema Complexity for Questions:** Handling diverse NEET question formats (MCQ, Assertion-Reason, Matching) requires careful JSONB or polymorphic model planning.