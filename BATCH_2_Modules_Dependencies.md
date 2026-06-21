# NEET POS — Execution System · Batch 2 of 6
# Layer 3: Module Breakdown + Layer 4: File Structure + Layer 5: Dependency Map + Layer 5.5: Traceability Matrix

---

# LAYER 3: MODULE DECOMPOSITION

## Module List (Ordered by Implementation Sequence)

### M01 — Infrastructure & Project Setup

| Attribute | Detail |
|---|---|
| **Purpose** | Bootstrap repository, Docker Compose, CI/CD skeleton, Alembic setup |
| **Responsibilities** | Project scaffolding; dependency management; environment config; Docker services |
| **Internal Components** | docker-compose.yml; Alembic config; GitHub Actions workflow; pyproject.toml; .env.example |
| **Dependencies** | None (first to be built) |
| **Associated Req IDs** | OBJ-09, OBJ-10 (non-functional) |
| **Risk** | LOW — standard scaffolding; well-understood patterns |

### M02 — Identity Domain (Auth + RBAC)

| Attribute | Detail |
|---|---|
| **Purpose** | User authentication, authorization, profile management, audit logging |
| **Responsibilities** | Register, email verification, login, JWT issuance/refresh, RBAC permission checks, audit log |
| **Internal Components** | AuthService, JWTService, RBACService, AuditService, RBACMiddleware, UserRepo, ProfileRepo, RoleRepo |
| **Dependencies** | M01 (database), email service |
| **Associated Req IDs** | F001, F002, F003, F005 |
| **Risk** | MEDIUM — JWT lifecycle, token rotation, audit log must be airtight |

### M03 — Taxonomy Domain

| Attribute | Detail |
|---|---|
| **Purpose** | Subject → Chapter → Topic hierarchy management |
| **Responsibilities** | Seed taxonomy data; CRUD for hierarchy levels; serve taxonomy APIs |
| **Internal Components** | TaxonomyService, SubjectRepo, ChapterRepo, TopicRepo |
| **Dependencies** | M02 (auth for protected routes) |
| **Associated Req IDs** | F010, F011, F012 |
| **Risk** | LOW — simple hierarchical data; seeding is one-time operation |

### M04 — Content Domain (Question Bank + Import)

| Attribute | Detail |
|---|---|
| **Purpose** | Question management, bulk import pipeline, PYQ support, search |
| **Responsibilities** | CRUD questions + answer_options; approval workflow (draft→review→published); import CSV/XLSX; search with filters |
| **Internal Components** | QuestionService, ImportService, QuestionRepo, import_processing_task (Celery), import polling API |
| **Dependencies** | M02 (auth/RBAC), M03 (taxonomy foreign keys), M01 (Celery, object storage) |
| **Associated Req IDs** | F006, F007, F008, F009, F014 |
| **Risk** | MEDIUM — import pipeline edge cases (encoding, malformed rows); question status state machine |

### M05 — Assessment Domain (Test Engine + Attempt Tracking)

| Attribute | Detail |
|---|---|
| **Purpose** | Test structure management, attempt lifecycle, scoring, OMR tracking, timer |
| **Responsibilities** | Create/manage test structures; start attempts; batch-save answer events; idempotent submission; NEET scoring |
| **Internal Components** | TestEngineService, AttemptService, ScoringService, TestRepo, AttemptRepo, AttemptAnswerRepo, Redis state management |
| **Dependencies** | M02, M03, M04 (all content must exist before tests run) |
| **Associated Req IDs** | F016, F017, F018, F023, F024, F025, F026 |
| **Risk** | CRITICAL — F026 is the single most important feature; data corruption here breaks all downstream intelligence |

### M06 — Intelligence Domain (Analytics + Dashboard + Heatmap)

| Attribute | Detail |
|---|---|
| **Purpose** | Post-attempt analytics computation, performance scoring, weakness detection, dashboard API |
| **Responsibilities** | Async aggregation of attempt_answers; topic/chapter/subject accuracy; composite score; heatmap generation; dashboard assembly |
| **Internal Components** | AnalyticsService, DashboardService, HeatmapService, ScoreService, SnapshotRepo, WeaknessRepo, analytics_computation_task, weakness_detection_task |
| **Dependencies** | M05 (attempt data), M01 (Celery), Redis (dashboard cache) |
| **Associated Req IDs** | F027, F028, F031 |
| **Risk** | HIGH — composite score formula must be locked; heuristics produce some inaccurate classifications; N+1 query risk in analytics aggregation |

### M07 — Recovery Domain (Mistake Vault + Missions + Recommendations)

| Attribute | Detail |
|---|---|
| **Purpose** | Root cause classification, mission generation, topic recommendations |
| **Responsibilities** | Classify wrong answers by root cause; generate missions (max 3 active); create mission tasks; derive topic recommendations |
| **Internal Components** | MistakeService, RecoveryService, RecommendationService, MistakeRepo, MissionRepo, classification_task, mission_generation_task |
| **Dependencies** | M05 (attempt_answers), M06 (weakness_signals, performance_snapshot) |
| **Associated Req IDs** | F044, F045, F047 |
| **Risk** | HIGH — most complex orchestration; cold start problem; root cause classification accuracy is a known limitation |

### M08 — Frontend

| Attribute | Detail |
|---|---|
| **Purpose** | React/Vite SPA — student interface for all features |
| **Responsibilities** | Auth flow; test UI (Zustand + timer); dashboard visualizations; weakness heatmap; mistake vault; mission UI |
| **Internal Components** | Auth feature; Question browsing; Test session (Zustand store); Performance Dashboard; Heatmap visualization; Mistake Vault; Recovery Missions UI; TanStack Query layer |
| **Dependencies** | M02–M07 (all API endpoints must exist) |
| **Associated Req IDs** | All 25 features (UI layer) |
| **Risk** | MEDIUM — test session state management complexity; timer sync; Zustand ↔ server state consistency |

### M09 — Observability & Hardening

| Attribute | Detail |
|---|---|
| **Purpose** | Production readiness: error tracking, structured logging, CI hardening |
| **Responsibilities** | Sentry integration; structlog setup; load testing; N+1 query fixes; beta deployment |
| **Internal Components** | Sentry config; structlog config; locust/k6 load test scripts; GitHub Actions CI |
| **Dependencies** | M01–M08 (all features complete) |
| **Associated Req IDs** | Non-functional: OBJ-09, all reliability/observability NFRs |
| **Risk** | LOW — additive to existing code |

---

## Implementation Order

```
M01 → M02 → M03 → M04 → M05 → M06 → M07 → M08 → M09
(sequential; each unlocks the next)

M08 (Frontend) can begin in parallel with M06 for auth/content pages,
but Test UI and Dashboard require M05 and M06 to be complete first.
```

---

# LAYER 4: FILE STRUCTURE PLAN

## Backend Directory Structure

```
backend/
├── app/
│   ├── main.py                          # FastAPI app factory; middleware; routers
│   ├── config.py                        # Settings (Pydantic BaseSettings, env vars)
│   ├── database.py                      # SQLAlchemy async engine + session factory
│   ├── dependencies.py                  # Shared FastAPI dependencies (get_db, get_current_user)
│   │
│   ├── domains/
│   │   ├── identity/                    # M02
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # /auth/* and /profile routes
│   │   │   ├── service.py               # AuthService, JWTService, RBACService, AuditService
│   │   │   ├── repository.py            # UserRepo, ProfileRepo, RoleRepo
│   │   │   ├── models.py                # SQLAlchemy: User, Profile, Role, UserRole, Permission, RolePermission, AuditLog
│   │   │   ├── schemas.py               # Pydantic: RegisterInput, LoginInput, ProfileUpdate, TokenResponse
│   │   │   ├── middleware.py            # JWTMiddleware, RBACMiddleware
│   │   │   └── exceptions.py            # AuthException hierarchy
│   │   │
│   │   ├── content/                     # M03 + M04
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # /subjects, /chapters, /topics, /questions, /imports
│   │   │   ├── service.py               # QuestionService, TaxonomyService, ImportService
│   │   │   ├── repository.py            # QuestionRepo, SubjectRepo, ChapterRepo, TopicRepo
│   │   │   ├── models.py                # SQLAlchemy: Subject, Chapter, Topic, Question, AnswerOption, QuestionTag, Tag
│   │   │   ├── schemas.py               # Pydantic: QuestionCreate, QuestionResponse, ImportRequest, SearchFilter
│   │   │   └── exceptions.py
│   │   │
│   │   ├── assessment/                  # M05
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # /tests, /attempts
│   │   │   ├── service.py               # TestEngineService, AttemptService, ScoringService
│   │   │   ├── repository.py            # TestRepo, AttemptRepo, AttemptAnswerRepo
│   │   │   ├── models.py                # SQLAlchemy: Test, TestSection, TestQuestion, Attempt, AttemptAnswer
│   │   │   ├── schemas.py               # Pydantic: AttemptStart, AnswerEvent, SubmitResponse, AttemptResult
│   │   │   ├── timer.py                 # Timer validation utilities (server-side enforcement)
│   │   │   └── exceptions.py
│   │   │
│   │   ├── intelligence/                # M06
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # /dashboard/* routes
│   │   │   ├── service.py               # AnalyticsService, DashboardService, HeatmapService, ScoreService
│   │   │   ├── repository.py            # SnapshotRepo, TopicAnalyticsRepo, WeaknessRepo
│   │   │   ├── models.py                # SQLAlchemy: PerformanceSnapshot, SubjectAnalytics, ChapterAnalytics, TopicAnalytics, WeaknessSignal
│   │   │   ├── schemas.py               # Pydantic: DashboardResponse, HeatmapResponse, ScoreHistory
│   │   │   ├── score_formula.py         # Locked PerformanceScore formula (versioned config)
│   │   │   └── exceptions.py
│   │   │
│   │   └── recovery/                    # M07
│   │       ├── __init__.py
│   │       ├── router.py                # /mistakes, /missions, /recommendations
│   │       ├── service.py               # MistakeService, RecoveryService, RecommendationService
│   │       ├── repository.py            # MistakeRepo, MissionRepo
│   │       ├── models.py                # SQLAlchemy: Mistake, MistakeOccurrence, RecoveryMission, MissionTask, WeakTopicRecommendation
│   │       ├── schemas.py               # Pydantic: MistakeResponse, MissionResponse, MissionTask, RecommendationResponse
│   │       ├── classifier.py            # Root cause inference rules (heuristic logic)
│   │       └── exceptions.py
│   │
│   ├── shared/
│   │   ├── audit/
│   │   │   └── service.py               # AuditService (shared across domains)
│   │   ├── storage/
│   │   │   └── r2.py                    # Cloudflare R2 client wrapper
│   │   ├── cache/
│   │   │   └── redis.py                 # Redis client + helpers
│   │   ├── pagination.py                # Cursor-based pagination utility
│   │   └── exceptions.py               # Base exception classes + HTTP error handler
│   │
│   └── workers/
│       ├── __init__.py
│       ├── celery_app.py                # Celery app factory
│       ├── analytics_tasks.py           # analytics_computation_task, weakness_detection_task
│       ├── mission_tasks.py             # mission_generation_task, classification_task
│       ├── import_tasks.py              # import_processing_task
│       └── notification_tasks.py        # email_notification_task
│
├── migrations/                          # Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_create_identity_tables.py
│       ├── 002_create_taxonomy_tables.py
│       ├── 003_create_content_tables.py
│       ├── 004_create_assessment_tables.py
│       ├── 005_create_intelligence_tables.py
│       └── 006_create_recovery_tables.py
│
├── tests/
│   ├── conftest.py                      # Fixtures: test DB, test client, mock Redis
│   ├── test_identity/
│   │   ├── test_auth.py                 # F001, F002, F005 integration tests
│   │   └── test_profile.py             # F003 tests
│   ├── test_content/
│   │   ├── test_questions.py           # F006, F008, F009, F014 tests
│   │   └── test_import.py              # F007 tests
│   ├── test_assessment/
│   │   ├── test_attempt_lifecycle.py   # F026 comprehensive tests (most critical)
│   │   ├── test_scoring.py             # F025 tests
│   │   └── test_test_engine.py         # F016, F017, F018 tests
│   ├── test_intelligence/
│   │   ├── test_analytics.py           # F027, F028, F031 tests
│   │   └── test_dashboard.py           # Dashboard API tests
│   └── test_recovery/
│       ├── test_mistakes.py            # F044 tests
│       └── test_missions.py            # F045, F047 tests
│
├── pyproject.toml                       # Dependencies + tool config
├── alembic.ini
├── Dockerfile
└── .env.example
```

## Frontend Directory Structure

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── router.tsx                       # React Router v6 routes
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/              # LoginForm, RegisterForm, EmailVerification
│   │   │   ├── hooks/                   # useAuth, useLogin, useRegister
│   │   │   └── store/                   # authStore (Zustand)
│   │   │
│   │   ├── profile/
│   │   │   └── components/              # ProfileForm
│   │   │
│   │   ├── tests/
│   │   │   ├── components/              # TestList, TestCard
│   │   │   └── hooks/                   # useTests
│   │   │
│   │   ├── test-session/
│   │   │   ├── components/              # TestUI, OMRPanel, QuestionCard, Timer, ReviewPanel
│   │   │   ├── hooks/                   # useTestSession, useTimer, useAnswerSync
│   │   │   └── store/                   # testSessionStore (Zustand — critical state)
│   │   │
│   │   ├── dashboard/
│   │   │   ├── components/              # PerformanceDashboard, ScoreCard, ImprovementTrend
│   │   │   └── hooks/                   # useDashboard
│   │   │
│   │   ├── heatmap/
│   │   │   ├── components/              # WeaknessHeatmap, SubjectHeatmap, TopicCell
│   │   │   └── hooks/                   # useHeatmap
│   │   │
│   │   ├── mistakes/
│   │   │   ├── components/              # MistakeVault, MistakeCard, RootCauseFilter
│   │   │   └── hooks/                   # useMistakes
│   │   │
│   │   └── missions/
│   │       ├── components/              # MissionList, MissionCard, TaskList, TaskItem
│   │       └── hooks/                   # useMissions, useMissionTasks
│   │
│   ├── shared/
│   │   ├── api/
│   │   │   ├── client.ts               # Axios instance + interceptors (auth, refresh)
│   │   │   └── endpoints.ts            # All API endpoint constants
│   │   ├── components/                  # Button, Input, Modal, Spinner, ErrorBoundary
│   │   ├── hooks/                       # usePagination, useDebounce
│   │   └── types/                       # Shared TypeScript types / DTOs
│   │
│   └── pages/
│       ├── LoginPage.tsx
│       ├── RegisterPage.tsx
│       ├── DashboardPage.tsx
│       ├── TestListPage.tsx
│       ├── TestSessionPage.tsx
│       ├── ResultsPage.tsx
│       ├── MistakesPage.tsx
│       └── MissionsPage.tsx
│
├── tests/
│   └── (Vitest unit tests per feature)
│
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## Project Root Structure

```
/
├── backend/
├── frontend/
├── docs/
│   ├── PROJECT_BRAIN.md                 # Authoritative project memory
│   ├── PROJECT_STATE.md                 # Current implementation status
│   ├── API_CONTRACTS.md                 # Full API reference
│   ├── DB_SCHEMA.md                     # Canonical database schema
│   ├── CHANGELOG.md                     # Version history
│   └── TASK_QUEUE.md                    # Active implementation task queue
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml                       # lint + test + build + deploy
└── README.md
```

---

# LAYER 5: DEPENDENCY MAP

## Internal Dependencies (Build Order)

```
M01 (Infrastructure)
  ↓
M02 (Identity) — requires DB, Redis, email service
  ↓
M03 (Taxonomy) — requires M02 auth middleware
  ↓
M04 (Content) — requires M02 (auth), M03 (taxonomy FKs), M01 (Celery, R2)
  ↓
M05 (Assessment) — requires M02, M03, M04 (questions must exist)
  ↓
M06 (Intelligence) — requires M05 (attempt_answers data), M01 (Celery)
  ↓
M07 (Recovery) — requires M05 (attempt_answers), M06 (weakness_signals, snapshots)
  ↓
M08 (Frontend) — requires all API endpoints from M02–M07
  ↓
M09 (Observability) — runs alongside and after M08
```

## Critical Convergence Points

| Point | Description |
|---|---|
| F026 (Attempt Tracking) | Every intelligence feature (F027, F028, F031, F044, F045, F047) derives from attempt_answers. If this is broken, nothing downstream works. |
| Celery task chain | analytics_computation_task → weakness_detection_task → mission_generation_task. Each triggers the next. If any fails, recovery requires retry logic. |
| PerformanceScore formula | Must be defined before M06 implementation begins. Changing post-launch invalidates historical scores. |

## External Dependencies

| Dependency | Version | Purpose | Risk if Unavailable |
|---|---|---|---|
| FastAPI | Latest stable | Backend framework | HIGH — replace with Flask (significant rework) |
| SQLAlchemy | 2.x (async) | ORM + migrations | HIGH |
| Alembic | Latest | Database migrations | HIGH |
| Pydantic | v2 | Request/response validation | HIGH |
| Celery | 5.x | Async task queue | MEDIUM — inline sync fallback possible at cost |
| Redis | 7.x | Cache + Celery broker | MEDIUM — task queue degraded without it |
| PostgreSQL | 16 | Primary database | HIGH — no substitute |
| argon2-cffi | Latest | Password hashing | HIGH — security requirement |
| python-jose | Latest | JWT handling | MEDIUM |
| boto3 | Latest | Cloudflare R2 (S3-compatible) | LOW — question images are optional at MVP |
| structlog | Latest | Structured logging | LOW |
| sentry-sdk | Latest | Error tracking | LOW |
| React | 18 | Frontend framework | HIGH |
| Vite | Latest | Build tool | LOW |
| TanStack Query | v5 | Server state management | MEDIUM |
| Zustand | Latest | Client state | LOW |
| React Router | v6 | Routing | MEDIUM |
| Axios | Latest | HTTP client | LOW |

---

# LAYER 5.5: REQUIREMENT TRACEABILITY MATRIX

| Req ID | Description | Feature | Module | Key Files | Roadmap Phase | Prompt IDs | Test IDs |
|---|---|---|---|---|---|---|---|
| F001 | Student Registration | Registration | M02 | identity/service.py, identity/router.py, migration 001 | Week 1, Day 1-2 | P-001 | T-001, T-002 |
| F002 | Login | Authentication | M02 | identity/service.py, identity/router.py | Week 1, Day 1-2 | P-002 | T-003, T-004 |
| F003 | Profile Management | Profile | M02 | identity/service.py, identity/router.py | Week 1, Day 1-2 | P-003 | T-005 |
| F005 | RBAC | Authorization | M02 | identity/middleware.py, identity/service.py | Week 1, Day 1-2 | P-004 | T-006, T-007 |
| F010 | Subject Classification | Taxonomy | M03 | content/service.py, migration 002 | Week 1, Day 3 | P-005 | T-008 |
| F011 | Chapter Classification | Taxonomy | M03 | content/service.py, migration 002 | Week 1, Day 3 | P-005 | T-008 |
| F012 | Topic Classification | Taxonomy | M03 | content/service.py, migration 002 | Week 1, Day 3 | P-005 | T-008 |
| F006 | Question Bank | Questions | M04 | content/service.py, content/router.py, migration 003 | Week 1, Day 4-5 | P-006 | T-009, T-010 |
| F007 | Import Pipeline | Bulk Import | M04 | content/service.py, workers/import_tasks.py | Week 1, Day 4-5 | P-007 | T-011, T-012 |
| F008 | PYQ Database | PYQ Flag | M04 | content/models.py (is_pyq field) | Week 1, Day 4-5 | P-006 | T-013 |
| F009 | Question Tagging | Tags | M04 | content/models.py (question_tags), content/service.py | Week 1, Day 4-5 | P-006 | T-014 |
| F014 | Question Search | Search | M04 | content/router.py, content/service.py | Week 1, Day 5 | P-008 | T-015 |
| F016 | Full NEET Mock | Test Engine | M05 | assessment/service.py, migration 004 | Week 2, Day 6-7 | P-009 | T-016 |
| F017 | Unit Tests | Test Engine | M05 | assessment/service.py | Week 2, Day 6-7 | P-010 | T-017 |
| F018 | Mixed Revision Tests | Test Engine | M05 | assessment/service.py | Week 2, Day 6-7 | P-011 | T-018 |
| F023 | Timer Engine | Timer | M05 | assessment/timer.py, assessment/models.py | Week 2, Day 8 | P-012 | T-019 |
| F024 | OMR Simulation | OMR | M05 | assessment/models.py (answer_changed, marked_review) | Week 2, Day 9-10 | P-013 | T-020 |
| F025 | Negative Marking | Scoring | M05 | assessment/service.py (ScoringService) | Week 2, Day 9-10 | P-014 | T-021 |
| F026 | Attempt Tracking | Attempt Lifecycle | M05 | assessment/service.py, assessment/repository.py, workers/analytics_tasks.py | Week 2, Day 9-10 | P-015, P-016 | T-022–T-030 |
| F027 | Performance Dashboard | Dashboard | M06 | intelligence/service.py, intelligence/router.py, workers/analytics_tasks.py | Week 3, Day 11-12 | P-017, P-018 | T-031, T-032 |
| F028 | Weakness Heatmap | Heatmap | M06 | intelligence/service.py (HeatmapService), workers/analytics_tasks.py | Week 3, Day 13 | P-019 | T-033 |
| F031 | Performance Score | Score | M06 | intelligence/score_formula.py, intelligence/service.py | Week 3, Day 11-12 | P-017 | T-034 |
| F044 | Mistake Vault | Mistakes | M07 | recovery/service.py, recovery/classifier.py, workers/mission_tasks.py | Week 4, Day 16-17 | P-020 | T-035, T-036 |
| F045 | Recovery Missions | Missions | M07 | recovery/service.py, workers/mission_tasks.py, migration 006 | Week 4, Day 18-19 | P-021, P-022 | T-037, T-038 |
| F047 | Weak Topic Recommendations | Recommendations | M07 | recovery/service.py (RecommendationService) | Week 4, Day 18-19 | P-023 | T-039 |

## Coverage Statistics

| Metric | Count |
|---|---|
| Requirements Identified | 25 (MVP feature set per blueprint) |
| Requirements Mapped to Modules | 25 |
| Requirements Mapped to Files | 25 |
| Requirements Mapped to Prompt IDs | 25 |
| Requirements Mapped to Test IDs | 25 |
| **Coverage Percentage** | **100%** |

## Unmapped Items

**None.** All 25 MVP features have:
- Module assignment
- File assignment
- Prompt ID assignment
- Test ID assignment

## Orphan Check

| Prompt ID Range | Maps To Requirements | Verified |
|---|---|---|
| P-001 | F001 | ✅ |
| P-002 | F002 | ✅ |
| P-003 | F003 | ✅ |
| P-004 | F005 | ✅ |
| P-005 | F010, F011, F012 | ✅ |
| P-006 | F006, F008, F009 | ✅ |
| P-007 | F007 | ✅ |
| P-008 | F014 | ✅ |
| P-009 | F016 | ✅ |
| P-010 | F017 | ✅ |
| P-011 | F018 | ✅ |
| P-012 | F023 | ✅ |
| P-013 | F024 | ✅ |
| P-014 | F025 | ✅ |
| P-015 | F026 (start attempt, save answers) | ✅ |
| P-016 | F026 (submit attempt — idempotent) | ✅ |
| P-017 | F027, F031 (analytics computation + score) | ✅ |
| P-018 | F027 (dashboard API + caching) | ✅ |
| P-019 | F028 (heatmap + weakness detection) | ✅ |
| P-020 | F044 (mistake classification) | ✅ |
| P-021 | F045 (mission generation) | ✅ |
| P-022 | F045 (mission execution lifecycle) | ✅ |
| P-023 | F047 (recommendations) | ✅ |
| P-024 | M08 (frontend test session + auth) | ✅ |
| P-025 | M09 (observability + hardening) | ✅ |

---

*Batch 2 of 6 — Continue to BATCH_3_Roadmap.md*
