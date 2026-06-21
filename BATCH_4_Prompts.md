# NEET POS — Execution System · Batch 4 of 6
# Layer 7: Atomic Implementation Prompts

---

> INSTRUCTIONS FOR AI CODING ASSISTANT:
> Each prompt below is self-contained. Paste the entire prompt block (including Context, Schema, and Tasks) as your input to the AI assistant.
> Execute prompts in P-number order. Do not skip.
> Reference BATCH_2_Modules_Dependencies.md for file paths.
> Reference BATCH_5_Testing_Decisions.md for tests after each implementation.

---

## P-000 — Project Infrastructure & Docker Setup

**Prompt ID:** P-000
**Module:** M01
**Roadmap:** Week 1, Day 1
**Requirement IDs:** Infrastructure (non-feature)

### Objective
Scaffold the complete project repository: backend FastAPI skeleton, frontend Vite/React skeleton, Docker Compose with all services, Alembic migration system, CI skeleton.

### Context
This is a FastAPI (Python 3.11+) + React 18/Vite + PostgreSQL 16 + Redis 7 + Celery 5 project. The backend is a domain-separated monolith with 5 domains: identity, content, assessment, intelligence, recovery. All code lives in a monorepo. No microservices at MVP.

### Files to Create
- `docker-compose.yml`
- `backend/pyproject.toml`
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/alembic.ini`
- `backend/migrations/env.py`
- `backend/.env.example`
- `backend/Dockerfile`
- `frontend/package.json`
- `frontend/vite.config.ts`
- `.github/workflows/ci.yml`

### Tasks
1. Create Docker Compose with services: postgres (16), redis (7-alpine), api (FastAPI), worker (Celery), frontend (Vite dev server). Map ports: postgres:5432, redis:6379, api:8000, frontend:5173.
2. Create FastAPI app factory in `main.py` with CORS middleware, rate limiting hooks (placeholder), and domain router registration stubs.
3. Create `config.py` using Pydantic `BaseSettings` reading from env vars: DATABASE_URL, REDIS_URL, SECRET_KEY, ALGORITHM (HS256), ACCESS_TOKEN_EXPIRE_MINUTES (15), REFRESH_TOKEN_EXPIRE_DAYS (7), FRONTEND_URL.
4. Create `database.py` with SQLAlchemy async engine + `AsyncSession` factory + `get_db` dependency.
5. Create Alembic `env.py` configured for async migrations using `asyncpg` driver.
6. Create GitHub Actions CI: lint (ruff + mypy), test (pytest with coverage gate ≥ 80%), build (Docker).
7. Create frontend with Vite + React 18 + TypeScript. Install: axios, @tanstack/react-query, zustand, react-router-dom.

### What Not To Do
- Do NOT generate any domain-specific code (no auth, no models) — only infrastructure
- Do NOT use sync SQLAlchemy — async only
- Do NOT put secrets in docker-compose.yml — use env_file references

### Expected Result
`docker-compose up` starts all 5 services. FastAPI root returns `{"status": "ok"}`. Alembic can run empty migration.

### Success Criteria
- [ ] `docker-compose up` starts without errors
- [ ] GET http://localhost:8000/ returns 200
- [ ] `alembic revision --autogenerate` runs without error
- [ ] GitHub Actions CI workflow file passes syntax validation

---

## P-001 — Identity: User Registration (F001)

**Prompt ID:** P-001
**Module:** M02
**Roadmap:** Week 1, Day 1-2
**Requirement IDs:** F001

### Objective
Implement student registration: schema migration, UserRepository, AuthService.register(), registration API endpoint.

### Context
Users have: id (UUID), email (unique), password_hash (Argon2id), email_verified (bool), status (pending/active/suspended). A Profile is created alongside the user. After registration, an email verification token is dispatched. Audit event USER_REGISTERED is logged.

### Schema (from blueprint)
```sql
users: id UUID PK, email VARCHAR(255) UNIQUE, password_hash TEXT, email_verified BOOLEAN DEFAULT FALSE, status VARCHAR(20) DEFAULT 'pending', created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
profiles: id UUID PK, user_id UUID FK → users, first_name, last_name, target_score INTEGER (0-720), target_year INTEGER, avatar_url TEXT, notification_prefs JSONB DEFAULT '{}'
audit_logs: id UUID PK, user_id UUID, event_type VARCHAR(100), metadata JSONB, created_at TIMESTAMPTZ
```

### Files to Create/Modify
- `backend/migrations/versions/001_create_identity_tables.py`
- `backend/app/domains/identity/models.py`
- `backend/app/domains/identity/repository.py` (UserRepo, ProfileRepo)
- `backend/app/domains/identity/service.py` (AuthService.register)
- `backend/app/domains/identity/schemas.py` (RegisterInput, RegisterResponse)
- `backend/app/domains/identity/router.py` (POST /api/v1/auth/register)

### Inputs
`{"email": "string", "password": "string (8+ chars)", "first_name": "string", "last_name": "string", "target_year": "int"}`

### Outputs
`{"message": "Verification email sent", "user_id": "uuid"}`

### Tasks
1. Create Alembic migration 001 creating: users, profiles, roles, user_roles, permissions, role_permissions, audit_logs tables with all indexes from blueprint §7.2.
2. Create SQLAlchemy models for all identity tables.
3. Implement `UserRepo`: create_user(email, password_hash), get_by_email(email), get_by_id(id), update_status(id, status).
4. Implement `AuthService.register()`: validate email uniqueness → hash password with argon2-cffi → create User (status=pending) → create Profile → generate verification token (UUID, store in Redis with 24hr TTL) → log USER_REGISTERED audit event → dispatch email_notification_task (stub OK at this stage).
5. Create Pydantic schemas for input validation (email format, password length ≥ 8).
6. Create router with POST /api/v1/auth/register. Return 409 CONFLICT if email already exists.

### What Not To Do
- Do NOT store tokens in the users table — use Redis for verification tokens
- Do NOT return the password_hash in any response
- Do NOT auto-verify email — verification must happen via the /verify-email endpoint

### Architecture Constraints
- Password hashing: argon2-cffi only (no bcrypt, no sha256)
- Token storage: Redis, not PostgreSQL
- Audit log: immutable append-only (no update/delete on audit_logs)

### Success Criteria
- [ ] POST /api/v1/auth/register with valid data returns 201
- [ ] Duplicate email returns 409
- [ ] Password is stored as Argon2id hash (not plaintext)
- [ ] audit_logs contains USER_REGISTERED row after registration
- [ ] Test: `test_identity/test_auth.py::test_register_success` passes
- [ ] Test: `test_identity/test_auth.py::test_register_duplicate_email` passes

---

## P-002 — Identity: Login + JWT (F002)

**Prompt ID:** P-002
**Module:** M02
**Roadmap:** Week 1, Day 2
**Requirement IDs:** F002

### Objective
Implement login: JWT access token (15 min, in response body) + refresh token (7 days, httpOnly cookie). Implement token refresh and logout. Implement GET /auth/me.

### Context
Access token in response body → stored in Zustand memory. Refresh token in httpOnly cookie (Secure, SameSite=Strict) → sent automatically by browser. On 401, frontend interceptor calls /auth/refresh. Failed login increments a counter; 5 consecutive failures locks the account. Login only allowed for email_verified=true accounts.

### Files to Create/Modify
- `backend/app/domains/identity/service.py` (AuthService.login, AuthService.refresh, AuthService.logout)
- `backend/app/domains/identity/service.py` (JWTService.issue, JWTService.validate, JWTService.refresh)
- `backend/app/domains/identity/router.py` (POST /auth/login, POST /auth/refresh, POST /auth/logout, GET /auth/me)
- `backend/app/domains/identity/middleware.py` (JWT decode middleware / dependency)

### Inputs
Login: `{"email": "string", "password": "string"}`
Refresh: httpOnly cookie `refresh_token`
Logout: Bearer header

### Outputs
Login: `{"access_token": "jwt", "expires_in": 900, "user_id": "uuid", "role": "student"}` + Set-Cookie: refresh_token
Refresh: `{"access_token": "jwt", "expires_in": 900}`
Me: `{"user_id": "uuid", "email": "string", "role": "student", "permissions": [...]}`

### Tasks
1. Implement `JWTService`: issue_access_token(user_id, role) → JWT with exp=15min; issue_refresh_token(user_id) → opaque UUID stored in Redis with 7-day TTL; validate_access_token(token) → decoded payload or raise; rotate_refresh_token(old_token) → validate old → issue new → revoke old in Redis.
2. Implement `AuthService.login()`: get_by_email → verify password (Argon2id, constant-time) → check email_verified → check status=active → check failed_attempts < 5 → issue tokens → log LOGIN_SUCCESS audit event → return response.
3. Implement failed attempt tracking: Redis counter `login_attempts:{email}` with 15-min TTL. Lock account after 5.
4. Create `get_current_user` FastAPI dependency: decode Bearer token → return user_id + role.
5. Implement POST /auth/refresh: validate refresh token from cookie → rotate → return new access token.
6. Implement POST /auth/logout: invalidate refresh token in Redis → log LOGOUT event.
7. Implement GET /auth/me: return current user info + resolved permissions.

### What Not To Do
- Do NOT store access tokens in httpOnly cookie — access token goes in response body; refresh token goes in cookie
- Do NOT use symmetric HS256 if the config specifies RS256 — use config.ALGORITHM
- Do NOT skip constant-time comparison for password verification (prevent timing attacks)

### Architecture Constraints
- Access token: JWT, 15 minutes, in response body
- Refresh token: opaque UUID, 7 days, in Redis, set as httpOnly Secure SameSite=Strict cookie
- Failed attempts: Redis counter per email, NOT stored in users table

### Success Criteria
- [ ] POST /auth/login with valid credentials returns 200 with access_token in body and refresh_token cookie
- [ ] POST /auth/login with unverified email returns 403
- [ ] POST /auth/login after 5 failed attempts returns 429 (account locked)
- [ ] GET /auth/me with valid Bearer token returns user data
- [ ] POST /auth/refresh rotates token (old token no longer valid)
- [ ] POST /auth/logout invalidates refresh token

---

## P-003 — Identity: Profile Management (F003)

**Prompt ID:** P-003
**Module:** M02
**Roadmap:** Week 1, Day 2
**Requirement IDs:** F003

### Objective
Implement profile retrieval and update. Profile includes: first_name, last_name, target_score (0–720), target_year, avatar_url, notification_prefs (JSONB).

### Files to Create/Modify
- `backend/app/domains/identity/router.py` (GET /api/v1/profile, PATCH /api/v1/profile)
- `backend/app/domains/identity/service.py` (ProfileService.get, ProfileService.update)
- `backend/app/domains/identity/schemas.py` (ProfileResponse, ProfileUpdate)
- `backend/app/domains/identity/repository.py` (ProfileRepo.get_by_user_id, ProfileRepo.update)

### Inputs
PATCH: `{"first_name": "string?", "last_name": "string?", "target_score": "int? (0-720)", "target_year": "int?", "avatar_url": "string?", "notification_prefs": "object?"}`

### Tasks
1. Implement `ProfileRepo.get_by_user_id(user_id)` and `ProfileRepo.update(user_id, updates)`.
2. Implement GET /api/v1/profile: requires Bearer auth → return profile for current user → 404 if profile missing.
3. Implement PATCH /api/v1/profile: partial update (only provided fields change) → invalidate any profile cache → return updated profile.
4. Validate target_score between 0 and 720 at Pydantic schema level.

### What Not To Do
- Do NOT allow updating user email or password via this endpoint
- Do NOT allow a student to update another student's profile

### Success Criteria
- [ ] GET /profile returns profile for authenticated user
- [ ] PATCH /profile with target_score=750 returns 422 (out of range)
- [ ] PATCH /profile updates only provided fields (partial update)

---

## P-004 — Identity: RBAC (F005)

**Prompt ID:** P-004
**Module:** M02
**Roadmap:** Week 1, Day 2
**Requirement IDs:** F005

### Objective
Implement role-based access control: roles (student/teacher/admin/mentor), permission assignment, RBAC middleware that gates routes by role.

### Context
Roles and permissions are defined in the database. user_roles maps users to roles. role_permissions maps roles to permissions. Each permission is a (resource, action) pair. The RBAC middleware checks current user's permissions against required permission for each route.

### Files to Create/Modify
- `backend/app/domains/identity/models.py` (Role, Permission, UserRole, RolePermission)
- `backend/app/domains/identity/service.py` (RBACService.has_permission, RBACService.seed_roles)
- `backend/app/domains/identity/middleware.py` (RBACMiddleware, `require_permission` dependency)
- `backend/app/domains/identity/repository.py` (RoleRepo.get_user_permissions)

### Tasks
1. Implement `RBACService.seed_roles()`: create roles: student, teacher, admin, mentor. Define permissions: students can (questions:read, tests:read, attempts:write), teachers can + (questions:write), admins can + (questions:admin, users:admin, imports:write).
2. Implement `RBACService.has_permission(user_id, resource, action)`: query user_roles → role_permissions → return bool.
3. Create `require_permission(resource, action)` FastAPI dependency factory. Raises 403 FORBIDDEN if user lacks permission.
4. Apply `require_permission` to relevant routes: question creation (Teacher+), question deletion (Admin), import (Admin), user management (Admin).
5. Register student role assignment during user registration.

### Architecture Constraints
- Permissions cached in Redis per user for 15 minutes (key: `user_perms:{user_id}`)
- When user role changes, invalidate their permission cache

### Success Criteria
- [ ] Student cannot POST /questions (403)
- [ ] Teacher can POST /questions (201)
- [ ] Admin can DELETE /questions/:id (200)
- [ ] Student can POST /attempts/:id/submit (200)

---

## P-005 — Taxonomy: Subject/Chapter/Topic Hierarchy (F010, F011, F012)

**Prompt ID:** P-005
**Module:** M03
**Roadmap:** Week 1, Day 3
**Requirement IDs:** F010, F011, F012

### Objective
Create the subject/chapter/topic taxonomy hierarchy. Seed NEET taxonomy (Physics, Chemistry, Biology with their chapters and key topics). Create taxonomy APIs.

### Schema
```sql
subjects: id UUID PK, name VARCHAR(100) UNIQUE, code VARCHAR(10) UNIQUE
chapters: id UUID PK, subject_id UUID FK, name VARCHAR(200), code VARCHAR(20), sequence INTEGER
topics: id UUID PK, chapter_id UUID FK, name VARCHAR(200), sequence INTEGER
```

### Files to Create/Modify
- `backend/migrations/versions/002_create_taxonomy_tables.py`
- `backend/app/domains/content/models.py` (Subject, Chapter, Topic)
- `backend/app/domains/content/repository.py` (SubjectRepo, ChapterRepo, TopicRepo)
- `backend/app/domains/content/service.py` (TaxonomyService)
- `backend/app/domains/content/router.py` (GET /subjects, GET /subjects/:id/chapters, GET /chapters/:id/topics)
- `backend/app/domains/content/schemas.py` (SubjectResponse, ChapterResponse, TopicResponse)

### Tasks
1. Create Alembic migration 002 for subjects, chapters, topics tables with indexes.
2. Implement CRUD repositories for each taxonomy level.
3. Implement `TaxonomyService.seed_neet_taxonomy()`: seed Physics (chapters: Mechanics, Thermodynamics, Waves, Optics, Modern Physics, Electricity + topics), Chemistry (Physical, Organic, Inorganic chapters + topics), Biology (Botany, Zoology chapters + topics). Use at minimum 10 chapters and 30 topics for a functional test.
4. Implement GET /subjects — returns all subjects.
5. Implement GET /subjects/:id/chapters — returns chapters for subject, ordered by sequence.
6. Implement GET /chapters/:id/topics — returns topics for chapter, ordered by sequence.
7. Run seed on startup if taxonomy tables are empty (check before seeding).

### What Not To Do
- Do NOT allow topics to have sub-topics (3-level hierarchy is the limit at MVP)
- Do NOT seed via a migration — seed via a startup service call

### Success Criteria
- [ ] GET /subjects returns Physics, Chemistry, Biology
- [ ] GET /subjects/:physics_id/chapters returns Mechanics, Thermodynamics, etc.
- [ ] GET /chapters/:mechanics_id/topics returns motion, Newton's laws, etc.
- [ ] Seeding is idempotent (running twice doesn't create duplicates)

---

## P-006 — Content: Question Bank (F006, F008, F009)

**Prompt ID:** P-006
**Module:** M04
**Roadmap:** Week 1, Day 4
**Requirement IDs:** F006, F008, F009

### Objective
Implement the full Question Bank: CRUD operations, answer options management, PYQ flag support, question tagging, status workflow (draft → review → approved → published → archived).

### Schema
```sql
questions: id UUID PK, subject_id FK, chapter_id FK, topic_id FK, question_text TEXT, explanation TEXT, difficulty (easy/medium/hard/trap), is_pyq BOOLEAN, pyq_year INTEGER, status (draft/review/approved/published/archived), author_id FK users, version INTEGER DEFAULT 1
answer_options: id UUID PK, question_id FK, option_text TEXT, is_correct BOOLEAN, display_order INTEGER
question_tags: question_id FK, tag_id FK; tags: id UUID PK, name VARCHAR(100)
```

### Files to Create/Modify
- `backend/migrations/versions/003_create_content_tables.py`
- `backend/app/domains/content/models.py` (Question, AnswerOption, Tag, QuestionTag)
- `backend/app/domains/content/repository.py` (QuestionRepo)
- `backend/app/domains/content/service.py` (QuestionService)
- `backend/app/domains/content/schemas.py` (QuestionCreate, QuestionResponse, QuestionUpdate)
- `backend/app/domains/content/router.py` (GET/POST /questions, GET/PATCH/DELETE /questions/:id)

### Tasks
1. Create Alembic migration 003 for questions, answer_options, tags, question_tags with all indexes from blueprint §7.3.
2. Implement `QuestionRepo`: create, get_by_id, list_with_filters (subject_id, chapter_id, topic_id, status, is_pyq, difficulty), update, soft_delete (set status=archived).
3. Implement `QuestionService`: create_question (validates taxonomy FKs exist, creates answer_options), update_question, publish_question (status → published; validates exactly one is_correct option exists per question), archive_question.
4. Create `QuestionCreate` schema with nested `answer_options: List[AnswerOptionCreate]`. Validate 4 answer options, exactly 1 marked correct.
5. Implement GET /questions with cursor-based pagination and filter params: subject_id, chapter_id, topic_id, status, is_pyq, difficulty.
6. Implement POST /questions (Teacher+ permission).
7. Implement PATCH /questions/:id (Teacher+ permission). Only published questions cannot have question_text changed.
8. Implement DELETE /questions/:id (Admin permission): sets status=archived, not physical delete.

### What Not To Do
- Do NOT physically delete questions — archive them
- Do NOT serve draft/archived questions in test generation (status filter: published only)
- Do NOT allow zero or multiple correct answers per question

### Success Criteria
- [ ] POST /questions creates question with 4 answer options
- [ ] Question with 0 or 2 correct answers returns 422
- [ ] PATCH /questions/:id/status (publish) fails if question in draft with no correct answer
- [ ] GET /questions?is_pyq=true returns only PYQ questions
- [ ] Archived questions excluded from default list

---

## P-007 — Content: Import Pipeline (F007)

**Prompt ID:** P-007
**Module:** M04
**Roadmap:** Week 1, Day 5
**Requirement IDs:** F007

### Objective
Implement bulk question import via CSV/XLSX/JSON file upload. Import runs as Celery async task. Per-row validation with error report. Partial success acceptable.

### Context
File upload via multipart form. Max 10MB file size. Max 1,000 questions per import batch. Async: return import_id immediately; poll GET /imports/:id for status. Non-UTF-8 Excel CSVs must be handled. Malformed rows collected in error report; valid rows committed.

### Files to Create/Modify
- `backend/app/domains/content/router.py` (POST /questions/import, GET /imports/:id)
- `backend/app/domains/content/service.py` (ImportService)
- `backend/app/workers/import_tasks.py` (import_processing_task)
- `backend/app/shared/storage/r2.py` (R2 upload helper)

### CSV Column Format
`question_text, subject_code, chapter_name, topic_name, difficulty, is_pyq (bool), pyq_year (int or empty), explanation, option_a, option_b, option_c, option_d, correct_option (A/B/C/D)`

### Tasks
1. Implement POST /questions/import: validate file size (reject > 10MB); validate extension (csv/xlsx/json); upload file to R2; create import record in DB (status=queued); dispatch import_processing_task to Celery; return `{"import_id": "uuid", "status": "processing"}`.
2. Implement `import_processing_task(import_id)`: fetch file from R2; detect encoding (try UTF-8, fallback to latin-1); parse CSV/XLSX/JSON; validate row count (reject > 1,000); for each row: validate fields, resolve taxonomy FKs, create Question + AnswerOptions, collect errors; update import record with success_count, error_count, error_rows; set status=completed or failed.
3. Implement per-row validation: required fields present, subject_code exists, chapter_name exists under subject, difficulty valid enum, exactly one correct option.
4. Implement GET /imports/:id: return status + success_count + error_count + error_rows (JSON array of {row, error}).
5. Handle duplicate detection: question_text + subject_id combination — skip with warning if duplicate.

### What Not To Do
- Do NOT process imports synchronously in the API handler
- Do NOT fail entire import if some rows are invalid (partial success is correct behavior)
- Do NOT store import files permanently on R2 — set 7-day expiry

### Success Criteria
- [ ] Upload 100-row CSV → import_id returned immediately
- [ ] GET /imports/:id shows progress/completion
- [ ] Valid rows committed; invalid rows in error_rows report
- [ ] Non-UTF-8 CSV (Excel default encoding) handled correctly
- [ ] File > 10MB rejected at upload time (413)
- [ ] 1,001-row file rejects after counting (validation in task)

---

## P-008 — Content: Question Search (F014)

**Prompt ID:** P-008
**Module:** M04
**Roadmap:** Week 1, Day 5
**Requirement IDs:** F014

### Objective
Implement question search with multi-filter support for teachers and admins to locate questions without direct DB access.

### Files to Create/Modify
- `backend/app/domains/content/router.py` (GET /api/v1/questions/search)
- `backend/app/domains/content/service.py` (QuestionService.search)
- `backend/app/domains/content/schemas.py` (SearchFilter, SearchResponse)

### Inputs (query params)
`q` (text search in question_text), `subject_id`, `chapter_id`, `topic_id`, `difficulty`, `is_pyq` (bool), `status`, `cursor` (UUID), `limit` (default 20, max 100)

### Tasks
1. Implement text search via PostgreSQL `ILIKE '%query%'` on question_text. Full-text search is post-MVP; ILIKE sufficient at MVP scale.
2. Build composable filter query: each filter param adds a WHERE clause. All filters combined with AND.
3. Cursor-based pagination: `WHERE id > cursor ORDER BY id LIMIT limit`. Return `next_cursor` in response.
4. Cache common search results in Redis: key = `question_search:{sha256(filter_string)}`, TTL = 10 minutes. Invalidate on any question write.
5. Apply `require_permission(questions:read)` — Teacher+ only.

### Success Criteria
- [ ] GET /questions/search?q=photosynthesis returns matching questions
- [ ] GET /questions/search?subject_id=X&difficulty=hard returns filtered results
- [ ] Cursor pagination returns correct next_cursor
- [ ] Student role gets 403

---

## P-009 — Assessment: Test Structures (F016)

**Prompt ID:** P-009
**Module:** M05
**Roadmap:** Week 2, Day 6
**Requirement IDs:** F016

### Objective
Create test structure tables, TestEngineService for Full NEET Mock creation, seed one published Full Mock with 180 questions, implement test listing and detail APIs.

### Schema
```sql
tests: id UUID PK, title VARCHAR(255), test_type (full_mock/unit_test/mixed_revision), duration_mins INTEGER DEFAULT 180, total_marks INTEGER, status (draft/published), created_by FK users
test_sections: id UUID PK, test_id FK, subject_id FK, name VARCHAR(100), sequence INTEGER
test_questions: id UUID PK, test_id FK, section_id FK, question_id FK, marks INTEGER DEFAULT 4, sequence INTEGER
```

### Files to Create/Modify
- `backend/migrations/versions/004_create_assessment_tables.py` (tests, test_sections, test_questions — attempts and attempt_answers in P-015)
- `backend/app/domains/assessment/models.py` (Test, TestSection, TestQuestion)
- `backend/app/domains/assessment/repository.py` (TestRepo)
- `backend/app/domains/assessment/service.py` (TestEngineService)
- `backend/app/domains/assessment/router.py` (GET /tests, GET /tests/:id, POST /tests)
- `backend/app/domains/assessment/schemas.py` (TestResponse, TestCreate)

### Tasks
1. Create Alembic migration for tests, test_sections, test_questions with indexes.
2. Implement `TestEngineService.create_full_mock(title, created_by)`: creates Test (type=full_mock, duration_mins=180, total_marks=720) with 3 sections (Physics/Chemistry/Biology); fetches 60 published questions per subject; creates test_questions.
3. Implement `TestEngineService.get_published_tests()`: returns all published tests with section summary.
4. Implement `TestEngineService.get_test_detail(test_id)`: returns test + sections (without question content — questions are loaded at attempt start).
5. Seed one published Full NEET Mock on startup if no published full_mock tests exist.
6. Implement GET /tests (paginated), GET /tests/:id, POST /tests (Admin only).

### Success Criteria
- [ ] GET /tests returns seeded Full NEET Mock
- [ ] GET /tests/:id returns test with sections
- [ ] Seeded test has 180 questions total (3 sections × 60)
- [ ] POST /tests by Student → 403

---

## P-010 — Assessment: Unit Tests (F017)

**Prompt ID:** P-010
**Module:** M05
**Roadmap:** Week 2, Day 7
**Requirement IDs:** F017

### Objective
Extend TestEngineService to support Unit Tests (chapter-scoped, 30–45 questions, 60-minute duration).

### Context
Unit Test = test covering one chapter. Questions drawn from that chapter's topics. Duration: 60 minutes. Total marks = questions × 4.

### Tasks
1. Implement `TestEngineService.create_unit_test(chapter_id, title, question_count, created_by)`: creates Test (type=unit_test, duration_mins=60); creates one section; fetches `question_count` published questions from the given chapter_id; creates test_questions.
2. Expose via POST /tests with `test_type=unit_test` and `chapter_id` in request body.
3. Ensure Unit Tests appear in GET /tests with test_type filter.

### Success Criteria
- [ ] POST /tests creates unit test for a specific chapter
- [ ] Unit test has duration_mins=60
- [ ] Questions all belong to specified chapter

---

## P-011 — Assessment: Mixed Revision Tests (F018)

**Prompt ID:** P-011
**Module:** M05
**Roadmap:** Week 2, Day 7
**Requirement IDs:** F018

### Objective
Extend TestEngineService to support Mixed Revision Tests (cross-chapter, configurable question count, 90-minute default).

### Context
Mixed Revision = questions from multiple chapters/subjects. Purpose: retention testing and multi-subject behavioral data. Duration: 90 minutes default.

### Tasks
1. Implement `TestEngineService.create_mixed_revision_test(topic_ids: List[UUID], question_count, created_by)`: creates Test (type=mixed_revision, duration_mins=90); selects questions proportionally from given topic_ids; creates test_questions.
2. If topic_ids is empty, draw randomly from all published questions.
3. Expose via POST /tests with `test_type=mixed_revision` and `topic_ids` in request body.

### Success Criteria
- [ ] Mixed revision test created with questions from multiple topics
- [ ] Duration is 90 minutes
- [ ] Questions draw from specified topic_ids

---

## P-012 — Assessment: Timer Engine (F023)

**Prompt ID:** P-012
**Module:** M05
**Roadmap:** Week 2, Day 8
**Requirement IDs:** F023

### Objective
Implement server-side timer enforcement: track started_at on attempt creation; compute elapsed time on each answer save; enforce timer expiry on submission.

### Context
Timer is frontend-driven countdown. Server stores started_at (UTC) at attempt creation. Per-question time_spent_seconds tracked in attempt_answers. On submission, server validates time limit not exceeded. If timer has expired server-side, auto-accept submission (student already saw timeout on frontend).

### Files to Create/Modify
- `backend/app/domains/assessment/timer.py`
- `backend/app/domains/assessment/service.py` (integrate timer checks)

### Tasks
1. Implement `timer.py`: `is_time_expired(started_at, duration_mins)` → bool; `remaining_seconds(started_at, duration_mins)` → int; `validate_submission_timing(started_at, duration_mins)` → raise if > 5 min past expiry (grace period for network delays).
2. On answer save (PATCH /attempts/:id/answers): pass time_spent_seconds from client; validate it is reasonable (non-negative, not > remaining time); update attempt_answers.time_spent_seconds.
3. On submission: check if timer is expired. If expired but < 5-minute grace, accept. If > 5-minute grace, reject (abuse detection).
4. Frontend receives remaining_seconds in attempt start response.

### Success Criteria
- [ ] Attempt started at T; submission at T+185min (5-minute grace) → accepted
- [ ] Submission at T+200min → rejected (timer abuse)
- [ ] time_spent_seconds negative → 422 validation error

---

## P-013 — Assessment: OMR Simulation (F024)

**Prompt ID:** P-013
**Module:** M05
**Roadmap:** Week 2, Day 9
**Requirement IDs:** F024

### Objective
Ensure answer change tracking (answer_changed) and review flag (is_marked_review) are correctly persisted as behavioral signals in attempt_answers.

### Context
OMR behaviors: students can change answers (behavioral signal: confidence), mark questions for review (behavioral signal: uncertainty), and skip (behavioral signal: difficulty). These flags are the raw data for root cause classification in F044.

### Files to Create/Modify
- `backend/app/domains/assessment/schemas.py` (AnswerEvent schema)
- `backend/app/domains/assessment/service.py` (AttemptService.save_answers — ensure OMR flags handled)

### Tasks
1. Ensure `AnswerEvent` schema includes: question_id, selected_option_id (nullable), time_spent (seconds), changed (bool), marked_review (bool).
2. On upsert of AttemptAnswer: if existing answer differs from new selected_option_id → set `answer_changed=true`. If selected_option_id is null → set `skipped=true`.
3. `is_marked_review` is set directly from client event.
4. Track `first_touched_at` (when question was first opened) and `answered_at` (when answer was selected).
5. Ensure all OMR fields are included in the attempt state returned by GET /attempts/:id (for session recovery).

### Success Criteria
- [ ] Changing an answer sets answer_changed=true in DB
- [ ] Unmarking an answer (setting to null) sets skipped=true
- [ ] Marking review without selecting answer: is_marked_review=true, skipped=true
- [ ] GET /attempts/:id returns all OMR fields correctly

---

## P-014 — Assessment: Negative Marking Scoring (F025)

**Prompt ID:** P-014
**Module:** M05
**Roadmap:** Week 2, Day 9-10
**Requirement IDs:** F025

### Objective
Implement NEET standard scoring: +4 correct, -1 incorrect, 0 unanswered. Implement ScoringService.

### Files to Create/Modify
- `backend/app/domains/assessment/service.py` (ScoringService)
- `backend/app/domains/assessment/schemas.py` (SubmitResponse)

### Tasks
1. Implement `ScoringService.compute_neet_score(attempt_id)`:
   - Fetch all attempt_answers for the attempt
   - For each answer: if selected_option_id is null → score = 0 (unattempted); if selected_option_id.is_correct → score = +4; else → score = -1
   - Return: total_score, raw_correct, raw_incorrect, raw_unattempted
2. Persist scores to attempts table: total_score, raw_correct, raw_incorrect, raw_unattempted.
3. Also set `is_correct` on each attempt_answer row during scoring (allows fast analytics queries).
4. Maximum possible score for 180-question mock: 720. Minimum: -45 (all wrong). Unattempted ceiling: 0.

### What Not To Do
- Do NOT allow total_score below -45 for a 180-question test
- Do NOT compute score without looking up is_correct from answer_options (client data is untrusted)

### Success Criteria
- [ ] 135 correct, 0 wrong, 45 unattempted → 540
- [ ] 100 correct, 45 wrong, 35 unattempted → 355
- [ ] 0 correct, 180 wrong → -45
- [ ] is_correct correctly set on all attempt_answers after scoring

---

## P-015 — Assessment: Attempt Lifecycle — Start + Save Answers (F026)

**Prompt ID:** P-015
**Module:** M05
**Roadmap:** Week 2, Day 9-10
**Requirement IDs:** F026

### Objective
Implement the two most critical API operations: POST /tests/:id/attempts (start attempt with Redis caching + AttemptAnswer stub creation) and PATCH /attempts/:id/answers (batch answer event upsert).

### Schema (additions to migration 004)
```sql
attempts: id UUID PK, user_id FK, test_id FK, status (in_progress/submitted/abandoned), started_at TIMESTAMPTZ, submitted_at TIMESTAMPTZ, total_score INTEGER, raw_correct/incorrect/unattempted INTEGER
attempt_answers: id UUID PK, attempt_id FK, question_id FK, selected_option_id FK nullable, is_correct BOOLEAN, is_marked_review BOOLEAN, answer_changed BOOLEAN, time_spent_seconds INTEGER, first_touched_at TIMESTAMPTZ, answered_at TIMESTAMPTZ, skipped BOOLEAN
UNIQUE (attempt_id, question_id)
```

### Tasks
1. Add attempts and attempt_answers tables to migration 004. Add all indexes from blueprint §7.3.
2. Implement `AttemptService.start_attempt(user_id, test_id)`:
   - Check test exists and is published (404 if not)
   - Check no active attempt exists for this user+test (return existing if in_progress)
   - Create Attempt record (status=in_progress, started_at=now())
   - Fetch test_questions (ordered by sequence)
   - Bulk INSERT attempt_answer stubs (selected_option_id=null for all 180 questions)
   - Cache question list to Redis: `test_questions:{test_id}` (1hr TTL)
   - Cache attempt state to Redis: `active_test:{attempt_id}` (3hr TTL)
   - Return: attempt_id, questions (id, question_text, options, sequence), duration_seconds, started_at
3. Implement `AttemptService.save_answers(attempt_id, user_id, events: List[AnswerEvent])`:
   - Validate attempt belongs to user and is in_progress (403 if not)
   - Bulk UPSERT attempt_answers (ON CONFLICT (attempt_id, question_id) DO UPDATE)
   - Handle OMR flags (answer_changed, is_marked_review, skipped) per P-013
   - Update Redis cache with new answer state
   - Return 200 OK
4. Implement GET /attempts/:id (session recovery): validate ownership → check Redis first → fallback to DB → return current state including all answer events.

### What Not To Do
- Do NOT compute score in save_answers
- Do NOT allow save_answers if attempt status=submitted
- Do NOT use individual INSERTs for stub creation — use bulk INSERT

### Architecture Constraints
- PATCH /attempts/:id/answers must target < 100ms (bulk upsert, not N individual queries)
- Redis cache is the source of truth for active tests; DB is durable backup

### Success Criteria
- [ ] POST /tests/:id/attempts creates attempt + 180 stubs + Redis cache
- [ ] Second POST returns existing in-progress attempt (idempotent)
- [ ] PATCH /answers updates DB and Redis in < 100ms
- [ ] GET /attempts/:id returns full state with all current answer events
- [ ] PATCH /answers on submitted attempt returns 409

---

## P-016 — Assessment: Submit Attempt — Idempotent (F026)

**Prompt ID:** P-016
**Module:** M05
**Roadmap:** Week 2, Day 10
**Requirement IDs:** F026

### Objective
Implement POST /attempts/:id/submit — the most critical single API in the system. Synchronous scoring. Idempotent. Dispatches Celery analytics chain.

### Tasks
1. Implement `AttemptService.submit_attempt(attempt_id, user_id)`:
   - Validate attempt belongs to user
   - If status=submitted already → return existing result (idempotency)
   - If status=in_progress → proceed
   - Call `ScoringService.compute_neet_score(attempt_id)` synchronously
   - Update Attempt: total_score, raw_correct, raw_incorrect, raw_unattempted, status=submitted, submitted_at=now()
   - Invalidate Redis `active_test:{attempt_id}` key
   - Invalidate Redis `user_dashboard:{user_id}` cache
   - Dispatch `analytics_computation_task.delay(attempt_id)` to Celery
   - Return: `{"score": int, "correct": int, "incorrect": int, "unattempted": int, "analytics_status": "computing"}`
2. Implement POST /attempts/:id/submit route with `force=true` flag support (for timer auto-submit).
3. Ensure submission is wrapped in a DB transaction (scoring + status update atomic).

### What Not To Do
- Do NOT dispatch analytics synchronously — async via Celery only
- Do NOT allow re-scoring on second submit call
- Do NOT delete AttemptAnswer rows after submission — they are permanent

### Success Criteria
- [ ] Submit with correct scores returns 200 with correct score breakdown
- [ ] Submit called twice → second call returns same result, attempt NOT re-scored
- [ ] Celery task dispatched after submission (verify via Celery inspect)
- [ ] Attempt status = submitted after call
- [ ] Redis active_test key invalidated after submit

---

## P-017 — Intelligence: Analytics Computation + Score (F027, F031)

**Prompt ID:** P-017
**Module:** M06
**Roadmap:** Week 3, Day 11-12
**Requirement IDs:** F027, F031

### Objective
Implement analytics_computation_task (Celery): aggregate attempt_answers by topic/chapter/subject, compute PerformanceScore, persist PerformanceSnapshot and analytics records.

### Schema
```sql
performance_snapshots: id UUID PK, user_id FK, attempt_id FK, performance_score INTEGER, accuracy_rate NUMERIC(5,2), computed_at TIMESTAMPTZ
topic_analytics: id UUID PK, user_id FK, attempt_id FK, topic_id FK, questions_seen INT, questions_correct INT, accuracy_pct NUMERIC(5,2), avg_time_seconds NUMERIC(7,2)
(also subject_analytics, chapter_analytics with similar structure per-subject/per-chapter)
```

### Files to Create/Modify
- `backend/migrations/versions/005_create_intelligence_tables.py`
- `backend/app/domains/intelligence/models.py`
- `backend/app/domains/intelligence/service.py` (AnalyticsService, ScoreService)
- `backend/app/domains/intelligence/score_formula.py` (PerformanceScore formula v1)
- `backend/app/workers/analytics_tasks.py` (analytics_computation_task)

### Tasks
1. Create migration 005: performance_snapshots, subject_analytics, chapter_analytics, topic_analytics, weakness_signals.
2. Implement `analytics_computation_task(attempt_id)`:
   - Fetch all attempt_answers with JOINs to questions, topics, chapters, subjects
   - For each topic: compute questions_seen, questions_correct, accuracy_pct, avg_time_seconds
   - For each chapter: aggregate topic-level data
   - For each subject: aggregate chapter-level data
   - Bulk INSERT into topic_analytics, chapter_analytics, subject_analytics
   - Call ScoreService.compute_performance_score(user_id, attempt_id)
   - Dispatch `weakness_detection_task.delay(attempt_id)` on completion
3. Implement `ScoreService.compute_performance_score(user_id, attempt_id)`:
   - Compute accuracy_score from this attempt
   - Compute consistency_score from last 5 attempts (std dev of accuracy)
   - Compute breadth_score (topics attempted / total topics in test)
   - Compute improvement_delta (current - previous attempt accuracy; 0 for first attempt)
   - Apply formula from score_formula.py → performance_score integer 0–100
   - Persist PerformanceSnapshot with formula_version=1
4. Implement `score_formula.py`: define formula with version constant. Lock formula at v1.

### Architecture Constraints
- analytics_computation_task must be idempotent (safe to re-run)
- Do NOT query raw attempt_answers in the dashboard — use pre-aggregated analytics tables
- Celery retry: max_retries=3, exponential backoff

### Success Criteria
- [ ] After submit, PerformanceSnapshot created within 30 seconds
- [ ] topic_analytics rows created for all topics in the test
- [ ] ScoreService produces score 0–100
- [ ] Running analytics_computation_task twice does NOT create duplicate records

---

## P-018 — Intelligence: Dashboard API (F027)

**Prompt ID:** P-018
**Module:** M06
**Roadmap:** Week 3, Day 14
**Requirement IDs:** F027

### Objective
Implement DashboardService and GET /dashboard API with Redis caching (5-minute TTL, invalidated on new attempt submission).

### Files to Create/Modify
- `backend/app/domains/intelligence/service.py` (DashboardService)
- `backend/app/domains/intelligence/router.py` (GET /dashboard, GET /dashboard/attempts, GET /dashboard/attempts/:id)
- `backend/app/domains/intelligence/schemas.py` (DashboardResponse)

### Dashboard Response Shape
```json
{
  "current_performance_score": 62,
  "last_attempt_summary": {"attempt_id": "...", "score": 540, "correct": 135, "incorrect": 0, "unattempted": 45, "submitted_at": "iso"},
  "top_weaknesses": [{"topic_id": "...", "topic_name": "...", "severity": "critical", "accuracy_pct": 23.5}],
  "recent_missions": [{"mission_id": "...", "title": "...", "status": "active"}],
  "improvement_trend": [{"attempt_id": "...", "performance_score": 55, "computed_at": "iso"}, ...]
}
```

### Tasks
1. Implement `DashboardService.get_dashboard(user_id)`: check Redis cache → if hit return cached; if miss → assemble from DB → cache with 5-min TTL → return.
2. Assemble dashboard: fetch latest PerformanceSnapshot → top 5 WeaknessSignals by severity → last 5 PerformanceSnapshots for trend → latest 3 active RecoveryMissions.
3. Cache invalidation: called in AttemptService.submit_attempt (already in P-016).
4. Implement GET /dashboard/attempts: paginated list of user's attempts with score summary.
5. Implement GET /dashboard/attempts/:id: single attempt analytics (snapshot + topic breakdown).

### Success Criteria
- [ ] GET /dashboard returns 200 with all required fields
- [ ] GET /dashboard called twice → second call served from Redis (< 300ms)
- [ ] GET /dashboard after new submission reflects new data
- [ ] Returns 200 with empty/default data for user with no attempts yet

---

## P-019 — Intelligence: Weakness Heatmap (F028)

**Prompt ID:** P-019
**Module:** M06
**Roadmap:** Week 3, Day 13
**Requirement IDs:** F028

### Objective
Implement weakness_detection_task and GET /dashboard/heatmap. Detect topics below accuracy threshold; upsert WeaknessSignals with severity levels.

### Severity Thresholds
- `critical`: accuracy_pct < 30%
- `high`: accuracy_pct 30–50%
- `medium`: accuracy_pct 50–65%
- `low`: accuracy_pct 65–80%
- No signal created for accuracy_pct > 80%

### Files to Create/Modify
- `backend/app/domains/intelligence/service.py` (HeatmapService)
- `backend/app/workers/analytics_tasks.py` (weakness_detection_task)
- `backend/app/domains/intelligence/router.py` (GET /dashboard/heatmap)
- `backend/app/domains/intelligence/schemas.py` (HeatmapResponse)

### Tasks
1. Implement `weakness_detection_task(attempt_id)`:
   - Fetch topic_analytics for this attempt
   - For each topic: classify severity using thresholds above
   - UPSERT weakness_signals (ON CONFLICT (user_id, topic_id) → update severity, accuracy_pct, attempts_count++)
   - Dispatch `mission_generation_task.delay(user_id)` on completion
2. Implement GET /dashboard/heatmap: return weakness_signals grouped by subject → chapter → topic, with severity color coding.
3. Heatmap response shape: `{"subjects": [{"name": "Biology", "chapters": [{"name": "Genetics", "topics": [{"name": "Mendelian Genetics", "severity": "critical", "accuracy_pct": 23.5}]}]}]}`.
4. Threshold configurable via config.py (allow future tuning without code change).

### Success Criteria
- [ ] After test with < 30% accuracy on topic, weakness_signal created with severity=critical
- [ ] Second attempt on same topic updates existing weakness_signal (not duplicate)
- [ ] GET /dashboard/heatmap returns correctly nested structure
- [ ] Topic with > 80% accuracy produces no weakness_signal

---

## P-020 — Recovery: Mistake Vault (F044)

**Prompt ID:** P-020
**Module:** M07
**Roadmap:** Week 4, Day 16-17
**Requirement IDs:** F044

### Objective
Implement root cause classification of wrong answers, Mistake Vault persistence, and GET /mistakes API.

### Root Cause Rules (heuristic)
- `guessing`: time_spent < 20s AND wrong
- `timing`: time_spent > 180s AND wrong
- `confidence`: answer_changed AND wrong (changed to wrong answer)
- `conceptual`: difficulty=hard AND wrong (and none of above)
- `application`: difficulty=medium AND wrong (and none of above)
- `memory`: difficulty=easy AND wrong (and none of above)
- `unknown`: none of above match (fallback)

### Files to Create/Modify
- `backend/migrations/versions/006_create_recovery_tables.py`
- `backend/app/domains/recovery/models.py` (Mistake, MistakeOccurrence, RecoveryMission, MissionTask, WeakTopicRecommendation)
- `backend/app/domains/recovery/classifier.py` (root cause inference)
- `backend/app/domains/recovery/service.py` (MistakeService)
- `backend/app/domains/recovery/repository.py` (MistakeRepo)
- `backend/app/workers/mission_tasks.py` (classification_task)
- `backend/app/domains/recovery/router.py` (GET /mistakes, GET /mistakes/patterns)

### Tasks
1. Create migration 006: mistakes, mistake_occurrences, recovery_missions, mission_tasks, weak_topic_recommendations.
2. Implement `classifier.py`: `infer_root_cause(time_spent, answer_changed, difficulty)` → returns root_cause enum. Rules applied in priority order listed above.
3. Implement `classification_task(attempt_id)`:
   - Fetch all incorrect attempt_answers (is_correct=false) with joined question difficulty and timing data
   - For each: call infer_root_cause → upsert Mistake (ON CONFLICT (user_id, question_id) → recurrence_count++, last_seen_at=now())
   - Create MistakeOccurrence linked to this attempt
4. Implement GET /mistakes: return user's mistakes paginated, filterable by root_cause, severity, resolved.
5. Implement GET /mistakes/patterns: aggregate by root_cause showing counts and percentages.

### What Not To Do
- Do NOT delete resolved mistakes — set resolved_at timestamp
- Do NOT expose raw classification probabilities to user — show only the classified root cause

### Success Criteria
- [ ] Wrong answer < 20s → classified as guessing
- [ ] Same question wrong twice → recurrence_count = 2
- [ ] GET /mistakes?root_cause=conceptual returns only conceptual mistakes
- [ ] GET /mistakes/patterns shows correct counts per root cause

---

## P-021 — Recovery: Mission Generation (F045)

**Prompt ID:** P-021
**Module:** M07
**Roadmap:** Week 4, Day 18
**Requirement IDs:** F045

### Objective
Implement mission_generation_task: orchestrate inputs from WeaknessSignals, Mistake patterns, and PerformanceSnapshot to generate up to 3 recovery missions with 3–5 tasks each.

### Context
Mission types: 1 per top critical weakness topic, 1 per most frequent mistake root cause, 1 for lowest-performing subject.
Task types: revise_topic (self-reported revision), retry_questions (take from vault), take_mini_test (F017 unit test).
Cap: 3 active missions per user. Cold start: < 3 attempts → max 1 mission.

### Files to Create/Modify
- `backend/app/domains/recovery/service.py` (RecoveryService)
- `backend/app/workers/mission_tasks.py` (mission_generation_task)
- `backend/app/domains/recovery/schemas.py` (MissionCreate, MissionResponse, MissionTaskResponse)

### Tasks
1. Implement `mission_generation_task(user_id)`:
   - Check attempt count; if < 3 → set max_missions=1 (cold start rule)
   - Check current active mission count; if >= 3 (or >= max_missions) → skip generation (don't overwrite)
   - Fetch top 5 WeaknessSignals by severity
   - Fetch mistake pattern summary (root_cause counts from last 5 attempts)
   - Fetch latest PerformanceSnapshot
   - Generate missions using RecoveryService (returns up to 3 - current_active missions)
   - Persist RecoveryMission + MissionTask records
2. Implement `RecoveryService.generate_missions(weakness_signals, mistake_patterns, snapshot, available_slots)`:
   - If critical weakness → create mission: title="Fix [topic_name] Gaps", tasks=[revise_topic, retry_top_5_wrong_questions, take_mini_test]
   - If top mistake type = guessing → create mission: title="Improve Answer Confidence", tasks=[revise_methodology, retry_questions_with_time_pressure]
   - Assign priority_score and expected_gain (estimated marks recovery, heuristic)
   - Return list of MissionCreate objects

### Cold Start Rule
If user has < 3 attempts: `max_missions=1`. Generate only the highest-priority mission (worst weakness). Do not generate mistake pattern or subject missions yet — insufficient signal.

### Success Criteria
- [ ] User with 1 attempt → max 1 mission generated
- [ ] User with critical weakness → mission created with revise + retry + test tasks
- [ ] 3 active missions already exist → no new missions generated
- [ ] missions table has correct mission + tasks after task runs

---

## P-022 — Recovery: Mission Execution Lifecycle (F045)

**Prompt ID:** P-022
**Module:** M07
**Roadmap:** Week 4, Day 19
**Requirement IDs:** F045

### Objective
Implement mission execution APIs: POST /missions/:id/start, PATCH /missions/:id/tasks/:tid (complete task), POST /missions/:id/complete (finalize mission).

### Tasks
1. Implement POST /missions/:id/start: set mission status=executing, return mission + tasks.
2. Implement PATCH /missions/:id/tasks/:tid: validate task belongs to mission, validate task is in order (enforce sequence), set task status=completed. Return updated task list.
3. Implement POST /missions/:id/complete: validate all tasks completed → set mission status=completed, completed_at=now() → record RecoveryOutcome (accuracy before vs after related topic tests) → downgrade WeaknessSignal severity if improved → archive mission.
4. Implement GET /missions: return active missions with task list.
5. Implement GET /missions/:id: full mission detail.

### Success Criteria
- [ ] Mission start → status=executing
- [ ] Task completion in order succeeds; out-of-order task rejected (409)
- [ ] Mission complete with all tasks done → status=completed
- [ ] WeaknessSignal severity decremented after mission complete (if student improved)

---

## P-023 — Recovery: Weak Topic Recommendations (F047)

**Prompt ID:** P-023
**Module:** M07
**Roadmap:** Week 4, Day 19
**Requirement IDs:** F047

### Objective
Implement RecommendationService and GET /recommendations API. Derive ordered weak topic list from weakness_signals.

### Context
Recommendations = ordered list of topics the student should study next, based on severity and accuracy. Higher severity + lower accuracy = higher rank. Different from missions (recommendations are prescriptive suggestions, not structured action plans).

### Tasks
1. Implement `RecommendationService.get_weak_topic_recommendations(user_id, limit=10)`:
   - Fetch user's weakness_signals (not resolved)
   - Rank by: severity weight (critical=4, high=3, medium=2, low=1) × (1 - accuracy_pct/100)
   - Return top `limit` topics with: topic_id, topic_name, chapter_name, subject_name, severity, accuracy_pct, recommended_action.
2. Implement GET /recommendations: call service → return ranked list.
3. Exclude topics where weakness_signal.resolved_at is set.

### Success Criteria
- [ ] GET /recommendations returns topics ordered by severity + accuracy
- [ ] Resolved weakness signals excluded from recommendations
- [ ] Empty response (no weaknesses) returns 200 with empty list

---

## P-024 — Frontend: Core Features (All modules — UI layer)

**Prompt ID:** P-024
**Module:** M08
**Roadmap:** Week 2–4 (progressive)
**Requirement IDs:** All 25 features (UI)

### Objective
Implement the React/Vite frontend: authentication flow, test session UI, performance dashboard, weakness heatmap, mistake vault, recovery missions.

### Key Frontend Architecture Rules (from blueprint §6.3)
- Auth: access_token in Zustand memory (NOT localStorage); refresh_token in httpOnly cookie
- Axios interceptor: attach Bearer token; on 401 → call /auth/refresh → retry
- Test session state: Zustand `testSessionStore` persisted to localStorage every 30 seconds
- Server state: TanStack Query for all API data (stale-while-revalidate)
- Test timer: frontend countdown from duration_seconds; auto-submit on expiry

### Critical Components to Build

**Auth (build with P-002):**
- LoginForm with email/password → POST /auth/login → store token in Zustand
- RegisterForm → POST /auth/register → email verification notice
- Protected route wrapper using auth state

**Test Session (build with P-015):**
- TestList page: GET /tests → display available tests
- TestSession page: Zustand store with {attempt_id, questions, answers, timeRemaining}
- Timer component: countdown from duration_seconds; dispatches auto-submit at 0
- OMR Panel: mark/change/skip answers → debounced PATCH /attempts/:id/answers (500ms debounce)
- Submit handler: POST /attempts/:id/submit → navigate to Results page

**Dashboard (build with P-018):**
- PerformanceDashboard: GET /dashboard → display score, trend, top weaknesses
- WeaknessHeatmap: GET /dashboard/heatmap → nested subject/chapter/topic grid with severity colors

**Recovery (build with P-020 + P-022):**
- MistakeVault: GET /mistakes → grouped by root_cause; filterable
- MissionList: GET /missions → mission cards with task progress
- MissionDetail: GET /missions/:id → task list with completion checkboxes

### Success Criteria
- [ ] Student can register, verify email, and log in
- [ ] Test session: selecting answers syncs to server (verify via Network tab)
- [ ] Timer counts down; auto-submits at 0
- [ ] Dashboard shows score, heatmap, missions after test
- [ ] Mistake vault groups wrong answers by root cause
- [ ] Mission tasks can be marked complete

---

## P-025 — Observability, Load Testing, and Beta Hardening (M09)

**Prompt ID:** P-025
**Module:** M09
**Roadmap:** Week 4, Days 20-21
**Requirement IDs:** Non-functional requirements

### Objective
Add Sentry error tracking, structured logging, run load test (50 concurrent submissions), fix N+1 queries, finalize CI, deploy to staging.

### Tasks
1. Integrate Sentry SDK: capture all unhandled exceptions + Celery task failures + performance transactions for API endpoints.
2. Implement structlog: JSON-formatted logs with: timestamp, level, request_id, user_id (when authed), duration_ms, endpoint, status_code.
3. Run end-to-end test: script complete student journey (register → import questions → create test → take test → verify dashboard → verify missions).
4. Load test with locust or k6: 50 concurrent virtual users simultaneously submitting tests. Target: 0% data corruption, < 5% error rate, P95 submission time < 3 seconds.
5. Fix N+1 queries: analytics aggregation must use JOINs + GROUP BY, not per-topic individual queries. Use EXPLAIN ANALYZE to verify.
6. Finalize GitHub Actions CI: lint (ruff, mypy), test (pytest --cov --cov-fail-under=80), build Docker image.
7. Staging deployment: docker-compose up on staging server; run migrations; seed taxonomy; smoke test all endpoints.
8. Beta documentation: update docs/PROJECT_STATE.md to reflect all 25 features complete.

### Success Criteria
- [ ] Sentry captures test exception (trigger manually)
- [ ] Logs are JSON-formatted and include request_id
- [ ] Load test: 50 concurrent submits complete with 0 data corruption
- [ ] `pytest --cov` coverage ≥ 80%
- [ ] All 25 features listed as complete in PROJECT_STATE.md
- [ ] Staging environment accessible and functional

---

*Batch 4 of 6 — Continue to BATCH_5_Testing_Decisions.md*
