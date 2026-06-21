# NEET POS — Execution System · Batch 1 of 6
# Layer 1: Blueprint Analysis + Layer 2: System Architecture

---

# MASTER INDEX

| Batch | Contents | File |
|---|---|---|
| Batch 1 (this file) | Blueprint Analysis + System Architecture | BATCH_1_Analysis_Architecture.md |
| Batch 2 | Module Breakdown + File Structure + Dependency Map + Traceability Matrix | BATCH_2_Modules_Dependencies.md |
| Batch 3 | Development Roadmap | BATCH_3_Roadmap.md |
| Batch 4 | Atomic Implementation Prompts (P001–P025) | BATCH_4_Prompts.md |
| Batch 5 | Validation & Testing + Decision Log | BATCH_5_Testing_Decisions.md |
| Batch 6 | Risk Analysis + Change Impact + Final Checklist + Project Memory Files | BATCH_6_Risks_Memory.md |

**Requirement ID cross-references preserved throughout. Prompt IDs use format P-NNN.**

---

# LAYER 1: BLUEPRINT ANALYSIS

## 1.1 Project Vision

| Attribute | Detail |
|---|---|
| **Product Name** | NEET Performance Operating System |
| **Document Type** | Production-Grade Architecture & Implementation Blueprint |
| **Source Authority** | Modules 1–4, 6; 78-Feature Catalog; Execution Guide |
| **Status** | MVP First-Launch Engineering Reference |

**Purpose:** A diagnostic and recovery intelligence system for NEET aspirants — not a content platform, not an AI tutor. It explains why a student is losing marks, what the root cause is, and prescribes a recovery action plan.

**Core Value Loop:**
```
Question Bank → Test Engine (behavioral data collection) → Attempt Tracking (event capture at atomic level)
→ Performance Intelligence (diagnosis) → Recovery System (prescription) → Return engagement
```

**Problem Being Solved — Five Compounding Student Pain Points:**
1. **Cognitive:** Content overload with no clarity on score drivers
2. **Analytical:** Platforms report outcomes (score) but not root causes
3. **Behavioral:** Students avoid weak areas and waste energy on daily study decisions
4. **Emotional:** No system converts post-test failure into a structured recovery plan
5. **Operational:** No digital equivalent of the handwritten mistake journal that high-performers maintain

**Target Users:**
- Primary: NEET aspirants (students, age 17–20, preparing for national medical entrance exam)
- Secondary: Teachers (question management)
- Tertiary: Admins (platform administration)

**Business Goals:**
- Differentiate from Physics Wallah / Aakash (content platforms) by offering performance intelligence
- Establish behavioral dataset that future AI features (Brain Twin, Learning DNA) require
- Achieve word-of-mouth retention from a single-session complete loop

---

## 1.2 Core Objectives

### Primary Objectives

| ID | Objective |
|---|---|
| OBJ-01 | Deliver complete functional loop: Question → Test → Tracking → Intelligence → Recovery in MVP |
| OBJ-02 | Capture atomic behavioral data per answer event (F026 is the crown jewel) |
| OBJ-03 | Produce diagnostic intelligence: weakness detection at topic granularity |
| OBJ-04 | Generate prescriptive recovery plans that answer "what to do next" |
| OBJ-05 | Build the behavioral dataset that seeds all post-MVP intelligence features |

### Secondary Objectives

| ID | Objective |
|---|---|
| OBJ-06 | Operational velocity: support bulk import of 5,000–10,000 questions |
| OBJ-07 | Idempotent, corruption-proof attempt recording (financial-grade data) |
| OBJ-08 | Async analytics architecture preventing submission latency |
| OBJ-09 | Scalability foundation for 13M+ annual AttemptAnswer rows |
| OBJ-10 | AI-assisted development structure (PROJECT_BRAIN, task queue, contracts) |

### Success Metrics

| Metric | Target |
|---|---|
| End-to-end loop completion (registration → test → dashboard → missions) | Working on Day 21 |
| F026 integration test coverage | 100% edge cases covered |
| Performance Dashboard latency (cached) | < 300ms |
| Test submission latency (synchronous portion) | < 2 seconds |
| Analytics computation time (async) | < 30 seconds post-submission |
| Beta readiness | 5–10 real students on Day 21 |

---

## 1.3 Functional Requirements

### Module 1 — Authentication (4 features)

| Req ID | Feature | Inputs | Outputs | Dependencies | Priority |
|---|---|---|---|---|---|
| F001 | Student Registration | email, password, first_name, last_name, target_year | user record, profile record, verification email | None | P0 |
| F002 | Login | email, password | access_token (JWT), refresh_token (httpOnly cookie), user_id, role | F001 | P0 |
| F003 | Profile Management | target_score, target_year, avatar_url, notification_prefs | updated profile | F001, F002 | P0 |
| F005 | RBAC | role assignment (student/teacher/admin), resource + action | permission grant/deny | F001, F002 | P0 |

**F002 Business Logic Detail:**
- Verify email_verified=true before issuing tokens
- Log login event to audit table
- Track failed_attempts; lock account after 5 consecutive failures
- Argon2id password comparison; constant-time to prevent timing attacks
- Excluded: F004 Session Management (deferred post-MVP)

### Module 2 — Question System (8 features)

| Req ID | Feature | Inputs | Outputs | Dependencies | Priority |
|---|---|---|---|---|---|
| F006 | Question Bank | question_text, subject_id, chapter_id, topic_id, difficulty, options | stored question with answer_options | F010, F011, F012 | P0 |
| F007 | Question Import Pipeline | CSV/XLSX/JSON file (multipart) | import_id, async processing, error report | F006, Celery | P0 |
| F008 | PYQ Database | is_pyq flag, pyq_year on question | filtered PYQ question set | F006 | P0 |
| F009 | Question Tagging | tag assignments on questions | tagged questions for analytics | F006, F010–F012 | P0 |
| F010 | Subject Classification | subject name, code | subject records (Physics/Chemistry/Biology) | None | P0 |
| F011 | Chapter Classification | chapter name, subject_id | chapter records | F010 | P0 |
| F012 | Topic Classification | topic name, chapter_id | topic records | F011 | P0 |
| F014 | Question Search | filters (subject, chapter, topic, difficulty, is_pyq, status) | paginated question list | F006, F009–F012 | P1 |

**F007 Import Detail:**
- Async via Celery; returns import_id immediately
- Per-row validation; partial success acceptable
- File limit: 10MB; max 1,000 questions per batch
- Handles: non-UTF-8 CSVs, malformed question text, duplicate detection
- Excluded: F013 Difficulty Classification (enum at MVP), F015 Question Validation (manual review)

### Module 3 — Test Engine (7 features)

| Req ID | Feature | Inputs | Outputs | Dependencies | Priority |
|---|---|---|---|---|---|
| F016 | Full NEET Mock | test_id, user_id | attempt_id, 180 questions, duration_seconds, started_at | F006, F026 | P0 |
| F017 | Unit Tests | test_id (unit type), user_id | attempt_id, N questions (chapter-scoped) | F006, F026 | P0 |
| F018 | Mixed Revision Tests | test_id (mixed type), user_id | attempt_id, N questions (multi-chapter) | F006, F026 | P0 |
| F023 | Timer Engine | started_at (server), question interaction events | per-question time_spent_seconds, total time | F026 | P0 |
| F024 | OMR Simulation | answer_changed, marked_review flags | behavioral signals in attempt_answers | F026 | P0 |
| F025 | Negative Marking | selected_option_id, correct answer | total_score (+4/-1/0), raw_correct, raw_incorrect | F026 | P0 |
| F026 | Attempt Tracking | answer events (selection, change, review, skip, time) | attempt_answers rows — the primary analytics source | F016/F017/F018 | P0 |

**F026 Critical Design Rules:**
- Idempotent submission: duplicate submit detection via attempt status
- Test state recovery: answers cached in Redis (`active_test:{attempt_id}`)
- Batch answer upsert: up to 10 events per PATCH call
- attempt_answers is immutable post-submission (append-only)
- Excluded: F019–F022 (adaptive/AI-generated tests — post-MVP)

### Module 4 — Performance Intelligence (3 features)

| Req ID | Feature | Inputs | Outputs | Dependencies | Priority |
|---|---|---|---|---|---|
| F027 | Performance Dashboard | user_id → aggregated snapshots | current_performance_score, last_attempt_summary, top_weaknesses, recent_missions, improvement_trend | F026, Celery analytics | P0 |
| F028 | Weakness Heatmap | topic_analytics per attempt | weakness_signals by subject/chapter/topic with severity (critical/high/medium/low) | F026, F027 | P0 |
| F031 | Performance Score | accuracy_rate, consistency, breadth, improvement_delta | composite score 0–100 | F026, F027 | P0 |

**F031 Critical Rule:** Formula must be locked in a configuration table before first deployment. Formula versioned; historical scores never recomputed retroactively.

### Module 6 — Recovery System (3 features)

| Req ID | Feature | Inputs | Outputs | Dependencies | Priority |
|---|---|---|---|---|---|
| F044 | Mistake Vault | incorrect attempt_answers, root cause inference rules | mistake records classified by root_cause (7 types) | F026 | P0 |
| F045 | Recovery Missions | weakness_signals, mistake patterns, performance_score | up to 3 active recovery_missions with 3–5 mission_tasks each | F026–F028, F031, F044 | P0 |
| F047 | Weak Topic Recommendations | weakness_signals, topic_analytics | ordered list of topics to study | F028, F044 | P0 |

**F044 Root Cause Classification Rules (heuristic):**
- time_spent < 20s → Guessing
- time_spent > 180s AND wrong → Timing/Overthinking
- answer_changed AND wrong → Confidence
- high difficulty + wrong → Conceptual
- medium/easy + wrong → Application or Memory

**F045 Mission Cap:** Maximum 3 active missions per user at any time (enforced at service layer).

**Cold Start Rule:** Student with < 3 test attempts receives max 1 high-confidence mission.

---

## 1.4 Non-Functional Requirements

| Category | Requirement | Source |
|---|---|---|
| **Performance** | Dashboard API < 300ms cached, < 1000ms uncached | Blueprint §8.5 |
| **Performance** | Attempt answer save < 100ms | Blueprint §8.4 |
| **Performance** | Test submission (sync) < 2 seconds | Blueprint §9.1 |
| **Performance** | Analytics computation < 30 seconds (async) | Blueprint §9.1 |
| **Concurrency** | 50 concurrent test-takers (load test target) | Blueprint §13.5 |
| **Scalability** | 13M AttemptAnswer rows annually at 200 tests/day | Blueprint §11.1 |
| **Security** | JWT access tokens, httpOnly refresh cookies, Argon2id hashing | Blueprint §1.6 |
| **Security** | HTTPS, CORS policy, rate limiting | Blueprint §6.1 |
| **Security** | Audit log for all auth events and question state changes | Blueprint §1.8 |
| **Data Integrity** | Attempt records are financial-grade; idempotent submission | Blueprint §1.5 |
| **Data Integrity** | attempt_answers append-only post-submission | Blueprint §7.5 |
| **Data Integrity** | Weakness Signals: upsert (not duplicate) | Blueprint §7.5 |
| **Reliability** | Celery retry: 3 retries, exponential backoff | Blueprint §15.3 |
| **Reliability** | Analytics idempotent (recomputing gives same result) | Blueprint §15.3 |
| **Maintainability** | Domain-separated monolith; OpenAPI docs | Blueprint §11.3 |
| **Observability** | Sentry error tracking; structured JSON logging (structlog) | Blueprint §11.4 |
| **Test Coverage** | pytest coverage ≥ 80% (CI gate) | Blueprint §13.6 |
| **Compliance** | Privacy consent; data deletion support | Blueprint §5 |

---

## 1.5 Constraints

| Type | Constraint |
|---|---|
| **Resource** | Solo founder — sequential module delivery, no parallel team streams |
| **Timeline** | 4-week (21 working day) sprint; Month-1 enforces feature minimalism |
| **Technical** | Analytics features require behavioral data maturity (multiple test attempts) |
| **Dependency** | F026 must be fully operational before any intelligence feature can be validated |
| **Data** | PerformanceScore formula locked pre-deployment; no retroactive recomputation |
| **Scale** | MVP: single FastAPI + PostgreSQL + Redis instance |
| **Platform** | PostgreSQL 16, Redis 7, FastAPI (Python 3.11+), React 18 + Vite |
| **Storage** | Cloudflare R2 for object storage (question images, import files) |
| **Import** | Max 10MB file; max 1,000 questions per import batch |
| **Missions** | Hard cap: 3 active recovery missions per user |

---

## 1.6 User Flows

### Flow 1: First Test Experience

| Step | Entry | User Action | System Response | Exit |
|---|---|---|---|---|
| 1 | Landing page | Register with email + password | Creates User (pending), Profile; sends verification email | Email sent |
| 2 | Verification email | Clicks verification link | Sets email_verified=true, status=active | Account active |
| 3 | Login page | Enters credentials | Issues JWT + httpOnly cookie; logs audit event | Dashboard |
| 4 | Profile setup | Sets target_score=620, target_year | Updates profile | Dashboard |
| 5 | Test listing | Selects Full NEET Mock | Creates Attempt (in_progress), stubs 180 AttemptAnswers, caches to Redis | Test UI |
| 6 | Test UI | Answers questions, marks review | PATCH /attempts/:id/answers (batched); Redis updated | Still in test |
| 7 | Timer expires / Submit | Auto-submit or manual submit | ScoringService computes score (sync); dispatches Celery tasks (async) | Result page |
| 8 | Result page | Views score | GET /attempts/:id/result | Dashboard |
| 9 | Dashboard | Returns next session | GET /dashboard (analytics computed async) | Weekly loop |

### Flow 2: Recovery Mission Execution

| Step | Entry | User Action | System Response | Exit |
|---|---|---|---|---|
| 1 | Dashboard | Views active missions | GET /missions → 3 missions listed | Mission list |
| 2 | Mission detail | Opens "Fix Genetics Mistakes" | GET /missions/:id → 3 tasks shown | Task list |
| 3 | Mission start | Starts mission | POST /missions/:id/start → status=executing | Task view |
| 4 | Task 1 | Marks revision complete | PATCH /missions/:id/tasks/:t1 | Task 2 |
| 5 | Task 2 | Takes unit test (F017) | System links attempt to mission | Task 3 |
| 6 | Completion | Marks mission complete | POST /missions/:id/complete → validates, records outcome, updates WeaknessSignal | Mission archived |

### Flow 3: Question Import (Teacher/Admin)

| Step | Entry | User Action | System Response | Exit |
|---|---|---|---|---|
| 1 | Admin panel | Uploads CSV file | POST /questions/import → Celery task dispatched → import_id returned | Polling view |
| 2 | Polling | Polls GET /imports/:id | Returns status: processing / success count / error count / error rows | Complete |
| 3 | Review | Reviews error rows | Fixes errors, re-imports if needed | Done |

---

## 1.7 Risks and Unknowns

| Category | Item | Severity | Status |
|---|---|---|---|
| **Missing** | PerformanceScore formula exact weights not specified | HIGH | Must define before Day 1 of Week 3 |
| **Missing** | Weakness threshold (accuracy < X% = weak) not specified | MEDIUM | Default to 50%; make configurable |
| **Missing** | Email service provider not specified | LOW | Assume SendGrid/SMTP at MVP |
| **Ambiguous** | "3-mission cap" enforcement timing (on creation or display?) | MEDIUM | Enforce at service layer on creation |
| **Ambiguous** | Mission task "revise_topic" — does system track actual revision or trust student self-report? | MEDIUM | Trust self-report at MVP; manual completion |
| **Technical** | AttemptAnswer partitioning — not implemented at MVP but must be architected for | HIGH | Index strategy from Day 1; partition at 50M rows |
| **Technical** | Cold start: student with < 3 attempts has sparse mission data | MEDIUM | Generate max 1 mission; documented rule |
| **Integration** | Cloudflare R2 configuration not detailed | LOW | S3-compatible; standard boto3 pattern |
| **Assumption** | Analytics eventual consistency is acceptable (not real-time) | LOW | Confirmed by blueprint |
| **Assumption** | CSVs imported from Excel may not be UTF-8 | LOW | Handle in import parser explicitly |

---

# LAYER 2: SYSTEM ARCHITECTURE

## 2.1 Architecture Style

**Style: Modular Monolith → Microservices migration path**

- MVP: Single FastAPI application with domain-separated modules (not services)
- Domains map 1:1 with future microservice extraction boundaries
- Communication within MVP: direct service-layer function calls
- Communication for async work: Celery task queue (Redis broker)
- Future: Kafka/Kinesis replaces Celery for cross-service events at Phase 4

This is explicitly supported by the blueprint and must not be changed to microservices at MVP.

---

## 2.2 Major Systems

### Frontend (React/Vite SPA)

| Aspect | Detail |
|---|---|
| Framework | React 18 + Vite |
| Server State | TanStack Query (stale-while-revalidate caching) |
| Client State | Zustand (active test session; auth state in memory) |
| Routing | React Router v6 |
| Rendering | SPA; static assets via CDN; no SSR at MVP |
| Auth | access_token in Zustand memory; refresh_token in httpOnly cookie |
| Test Backup | Zustand → localStorage every 30 seconds (tertiary to Redis) |

### API Gateway Layer

| Component | Technology |
|---|---|
| Reverse proxy | Nginx or Caddy |
| TLS termination | At proxy level |
| Rate limiting | Per-IP and per-user |
| CORS policy | Configured at proxy and FastAPI level |

### Backend (FastAPI)

| Component | Technology |
|---|---|
| Framework | FastAPI (Python 3.11+) |
| Architecture | Router → Service → Repository → DB |
| Validation | Pydantic models |
| Auth middleware | JWT decode → user_id extraction |
| RBAC middleware | Permission check → 403 if denied |
| Docs | OpenAPI auto-generated |

**Request lifecycle:**
```
HTTP Request → Nginx → FastAPI Router → Pydantic Validation
→ Auth Middleware → RBAC Middleware → Route Handler
→ Service Layer (business logic) → Repository Layer (data access)
→ PostgreSQL / Redis → Output DTO → HTTP Response
```

### Data Layer

| Store | Technology | Purpose |
|---|---|---|
| Primary DB | PostgreSQL 16 | All domain data, analytics, audit, snapshots |
| Cache | Redis 7 | Active test state, session cache, dashboard cache |
| Queue broker | Redis 7 | Celery task broker |
| Object storage | Cloudflare R2 | Question images, import files, reports |

### Background Workers (Celery)

| Task | Trigger | Purpose |
|---|---|---|
| analytics_computation_task | AttemptCompleted event | Aggregate attempt_answers; create snapshots |
| weakness_detection_task | AnalyticsComputed event | Identify weak topics; create WeaknessSignals |
| mission_generation_task | WeaknessDetected event | Create RecoveryMissions + MissionTasks |
| import_processing_task | ImportUploaded event | Parse CSV/XLSX; validate; bulk insert |
| email_notification_task | System events | Send verification, notification emails |

---

## 2.3 Component Breakdown

### Auth Domain

| Component | Responsibilities | Inputs | Outputs | Deps |
|---|---|---|---|---|
| AuthService | register, verify_email, login, logout, refresh | credentials, tokens | JWT tokens, user records | UserRepo, JWTService, AuditService |
| JWTService | issue, validate, refresh tokens | user_id, role | access_token, refresh_token | None |
| RBACService | check permission for resource+action | user_id, resource, action | allow/deny | RoleRepo |
| AuditService | append-only event log | event_type, user_id, metadata | audit_log row | DB |

### Content Domain

| Component | Responsibilities | Inputs | Outputs | Deps |
|---|---|---|---|---|
| QuestionService | CRUD, approval workflow | question data | question records | QuestionRepo, TaxonomyService |
| TaxonomyService | subject/chapter/topic management | taxonomy data | hierarchy records | SubjectRepo, ChapterRepo, TopicRepo |
| ImportService | CSV/XLSX parsing, bulk insert | file + import_id | import result | QuestionService, Celery |

### Assessment Domain

| Component | Responsibilities | Inputs | Outputs | Deps |
|---|---|---|---|---|
| TestEngineService | create/manage test structures | test config | test + test_questions | QuestionRepo |
| AttemptService | start, save_answers, submit | attempt events | attempt + attempt_answers | TestRepo, ScoringService, Redis |
| ScoringService | NEET +4/-1/0 computation | attempt_answers | total_score, correct/incorrect/unattempted | AttemptAnswerRepo |

### Intelligence Domain

| Component | Responsibilities | Inputs | Outputs | Deps |
|---|---|---|---|---|
| AnalyticsService | aggregate attempt_answers by subject/chapter/topic | attempt_id | topic_analytics rows | AttemptAnswerRepo |
| DashboardService | assemble dashboard response | user_id | dashboard DTO | SnapshotRepo, WeaknessRepo, Redis |
| HeatmapService | detect weak topics (accuracy < threshold) | topic_analytics | weakness_signals | TopicAnalyticsRepo |
| ScoreService | compute composite PerformanceScore | accuracy, consistency, breadth, delta | score 0–100 | SnapshotRepo |

### Recovery Domain

| Component | Responsibilities | Inputs | Outputs | Deps |
|---|---|---|---|---|
| MistakeService | classify wrong answers by root cause | incorrect attempt_answers | mistake records | AttemptAnswerRepo |
| RecoveryService | generate missions, enforce cap, track completion | weakness_signals, mistakes, score | recovery_missions + mission_tasks | MistakeRepo, WeaknessRepo |
| RecommendationService | derive weak topic list | weakness_signals | ordered topic list | WeaknessRepo |

---

## 2.4 API Route Structure

All routes follow: `/api/v1/{domain}/{resource}`

### Authentication
- POST /api/v1/auth/register
- POST /api/v1/auth/verify-email
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- GET /api/v1/auth/me
- GET /api/v1/profile
- PATCH /api/v1/profile

### Question System
- GET/POST /api/v1/questions
- GET/PATCH /api/v1/questions/:id
- DELETE /api/v1/questions/:id
- POST /api/v1/questions/import
- GET /api/v1/questions/search
- GET /api/v1/subjects
- GET /api/v1/subjects/:id/chapters
- GET /api/v1/chapters/:id/topics
- GET /api/v1/imports/:id (polling)

### Test Engine
- GET /api/v1/tests
- GET /api/v1/tests/:id
- POST /api/v1/tests (Admin)
- POST /api/v1/tests/:id/attempts
- GET /api/v1/attempts/:id
- PATCH /api/v1/attempts/:id/answers
- POST /api/v1/attempts/:id/submit
- GET /api/v1/attempts/:id/result

### Analytics
- GET /api/v1/dashboard
- GET /api/v1/dashboard/heatmap
- GET /api/v1/dashboard/score
- GET /api/v1/dashboard/attempts
- GET /api/v1/dashboard/attempts/:id

### Recovery
- GET /api/v1/mistakes
- GET /api/v1/mistakes/patterns
- GET /api/v1/missions
- GET /api/v1/missions/:id
- POST /api/v1/missions/:id/start
- PATCH /api/v1/missions/:id/tasks/:tid
- POST /api/v1/missions/:id/complete
- GET /api/v1/recommendations

---

## 2.5 Data Architecture Highlights

### Critical Tables (ordered by importance)

1. **attempt_answers** — source of all intelligence; never delete; partition at 50M rows
2. **attempts** — idempotent; immutable post-submission
3. **weakness_signals** — upserted (not duplicated); drives recovery
4. **performance_snapshots** — versioned; immutable historical records
5. **mistakes** — append-only; resolved via resolved_at timestamp (no deletion)

### Caching Strategy

| Key Pattern | TTL | Content |
|---|---|---|
| `active_test:{attempt_id}` | 3 hours | In-progress answer draft |
| `test_questions:{test_id}` | 1 hour | Full question set |
| `user_dashboard:{user_id}` | 5 minutes | Aggregated dashboard |
| `session:{user_id}` | 15 minutes | JWT session metadata |
| `question_search:{hash}` | 10 minutes | Search result sets |

### Indexing (Critical from Day 1)

```
users(email)
attempts(user_id, status)
attempt_answers(attempt_id)
attempt_answers(question_id)
mistakes(user_id, root_cause)
weakness_signals(user_id, topic_id)
questions(subject_id), questions(chapter_id), questions(status)
```

---

*Batch 1 of 6 — Continue to BATCH_2_Modules_Dependencies.md*
