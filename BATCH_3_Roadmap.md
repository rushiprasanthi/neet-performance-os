# NEET POS — Execution System · Batch 3 of 6
# Layer 6: Development Roadmap

---

# LAYER 6: EXECUTION ROADMAP

## Overview

| Phase | Week | Goal | Features |
|---|---|---|---|
| Phase 1: Foundation | Week 1 (Days 1–5) | Questions enter system; students can register | F001, F002, F003, F005, F010, F011, F012, F006, F007, F008, F009, F014 |
| Phase 2: Assessment | Week 2 (Days 6–10) | Students can take tests | F016, F017, F018, F023, F024, F025, F026 |
| Phase 3: Intelligence | Week 3 (Days 11–15) | Students understand their performance | F027, F028, F031 |
| Phase 4: Recovery + Polish | Week 4 (Days 16–21) | Students get an action plan; system beta-ready | F044, F045, F047 + hardening |

---

## Phase 1: Foundation (Week 1, Days 1–5)

### Objective
Establish the base infrastructure, authentication, role management, and question system. By end of Week 1, an admin can import questions and a student can register.

### Phase Deliverables

| # | Deliverable | Validates |
|---|---|---|
| D1-1 | PostgreSQL with all identity + taxonomy + content tables (migrations 001–003) | Schema correctness |
| D1-2 | AuthService: register, verify_email, login, logout, refresh | F001, F002 |
| D1-3 | JWTService: issue, validate, refresh | F002 |
| D1-4 | RBACMiddleware: student/teacher/admin permission gates | F005 |
| D1-5 | AuditService: immutable event log | NFR: audit trail |
| D1-6 | TaxonomyService: Physics/Chemistry/Biology hierarchy | F010, F011, F012 |
| D1-7 | QuestionService: CRUD with approval workflow | F006, F008, F009 |
| D1-8 | ImportService + Celery task: CSV/XLSX bulk import | F007 |
| D1-9 | Question Search API | F014 |
| D1-10 | Docker Compose: postgres + redis + api + worker | M01 |

### Day-by-Day Plan

| Day | Tasks | Prompt IDs |
|---|---|---|
| Day 1 | M01: Scaffold project; Docker Compose; Alembic; FastAPI app factory; CI skeleton | P-000 (infra) |
| Day 1 | M02: Migration 001 — identity tables (users, profiles, roles, permissions, user_roles, role_permissions, audit_logs) | P-001 (partial) |
| Day 2 | M02: AuthService, JWTService, RBACService, AuditService; router; integration tests | P-001, P-002, P-003, P-004 |
| Day 3 | M03: Migration 002 — taxonomy tables; TaxonomyService; taxonomy APIs; seed data | P-005 |
| Day 4 | M04: Migration 003 — content tables; QuestionService CRUD; question APIs | P-006 |
| Day 5 | M04: ImportService + Celery import task; import polling API; Search API | P-007, P-008 |

### Phase 1 Dependencies

- Docker Compose must be functional before any backend work begins
- Taxonomy must be seeded before questions can be created (foreign key constraint)
- Celery worker must be running before import can be tested

### Phase 1 Validation Criteria

- [ ] `pytest tests/test_identity/ -v` passes with 0 failures
- [ ] `pytest tests/test_content/ -v` passes with 0 failures
- [ ] Student can register, verify email, and log in via API
- [ ] Admin can import 100 questions from a CSV and see them appear in GET /questions
- [ ] RBAC blocks student from accessing teacher-only endpoints (403)
- [ ] Audit log records LOGIN_SUCCESS and USER_REGISTERED events

---

## Phase 2: Assessment Engine (Week 2, Days 6–10)

### Objective
Build the test taking engine and, critically, the Attempt Tracking system (F026). This is the most important implementation phase — every future intelligence feature depends on the data quality of attempt_answers.

### Phase Deliverables

| # | Deliverable | Validates |
|---|---|---|
| D2-1 | Migration 004 — assessment tables (tests, test_sections, test_questions, attempts, attempt_answers) | Schema |
| D2-2 | TestEngineService: create Full Mock, Unit Test, Mixed Test structures | F016, F017, F018 |
| D2-3 | Seed: one published Full NEET Mock with 180 questions | F016 testable |
| D2-4 | AttemptService: start_attempt — creates Attempt + 180 AttemptAnswer stubs + Redis cache | F026 |
| D2-5 | AttemptService: save_answers — batch upsert of answer events | F026, F023, F024 |
| D2-6 | ScoringService: NEET +4/-1/0 computation at submission | F025 |
| D2-7 | AttemptService: submit_attempt — synchronous scoring + Celery dispatch + idempotency | F026 |
| D2-8 | Attempt recovery: GET /attempts/:id returns current state from Redis + DB | F026 |
| D2-9 | Comprehensive F026 integration tests (every edge case) | Quality gate |

### Day-by-Day Plan

| Day | Tasks | Prompt IDs |
|---|---|---|
| Day 6 | Assessment tables migration; TestEngineService; test listing API; seed one Full Mock | P-009 |
| Day 7 | TestEngineService: Unit Test + Mixed Test variants; test detail API | P-010, P-011 |
| Day 8 | Timer implementation: started_at server reference; time_spent_seconds tracking; auto-submit on expiry | P-012 |
| Day 9 | AttemptService: start_attempt + save_answers (batch upsert); Redis caching; OMR event tracking | P-013, P-015 |
| Day 10 | ScoringService; AttemptService: submit_attempt with idempotency; comprehensive F026 tests | P-014, P-016 |

### Phase 2 Dependencies

- Phase 1 complete (questions must exist in DB)
- Redis must be running (active test state caching)
- Celery must be running (analytics dispatch post-submission — even if analytics tasks are stubs)

### Phase 2 Validation Criteria

- [ ] Student can POST /tests/:id/attempts → receives question list
- [ ] PATCH /attempts/:id/answers correctly upserts per-question events
- [ ] POST /attempts/:id/submit returns correct NEET score (+4/-1/0)
- [ ] Duplicate submit returns same response without re-scoring
- [ ] GET /attempts/:id returns current state (recovery scenario)
- [ ] Redis key `active_test:{attempt_id}` is set on start; invalidated on submit
- [ ] All F026 edge cases covered in test suite (see T-022–T-030)
- [ ] `pytest tests/test_assessment/ -v` passes with 0 failures

### ⚠️ CRITICAL — F026 Edge Cases That Must Be Tested

| Edge Case | Test ID | Expected Behavior |
|---|---|---|
| Student submits twice (network retry) | T-022 | Second submit returns same score without re-computing |
| Student starts same test twice | T-023 | Second POST returns existing in-progress attempt |
| Browser crash — student calls GET /attempts/:id | T-024 | Returns current state from Redis or DB fallback |
| Timer expires mid-test | T-025 | Auto-submit accepted; score computed from answers at expiry |
| Student saves 0 answers then submits | T-026 | Score = 0, all unattempted |
| Student changes answer multiple times | T-027 | Only final selected_option_id is scored; answer_changed = true |
| Student marks review without selecting answer | T-028 | is_marked_review = true; skipped = true; no score impact |
| Concurrent answer saves (race condition) | T-029 | Last write wins; no duplicate rows (UNIQUE constraint on attempt_id + question_id) |
| Answer saved after attempt submitted | T-030 | 409 CONFLICT returned; attempt immutable |

---

## Phase 3: Intelligence Layer (Week 3, Days 11–15)

### Objective
Build the async analytics pipeline that transforms raw attempt_answers into diagnostic intelligence. By end of Week 3, a student sees a Performance Dashboard, Weakness Heatmap, and Performance Score within 30 seconds of test submission.

### Phase Deliverables

| # | Deliverable | Validates |
|---|---|---|
| D3-1 | Migration 005 — intelligence tables (performance_snapshots, subject_analytics, chapter_analytics, topic_analytics, weakness_signals) | Schema |
| D3-2 | analytics_computation_task (Celery) — aggregate attempt_answers → snapshots | F027, F031 |
| D3-3 | ScoreService — composite PerformanceScore formula (locked v1) | F031 |
| D3-4 | weakness_detection_task (Celery) — identify topics < accuracy threshold | F028 |
| D3-5 | DashboardService + GET /dashboard (Redis cached, 5-min TTL) | F027 |
| D3-6 | GET /dashboard/heatmap — weakness_signals by topic | F028 |
| D3-7 | GET /dashboard/score — score history | F031 |
| D3-8 | Frontend: Performance Dashboard component | F027 (UI) |
| D3-9 | Frontend: Weakness Heatmap visualization | F028 (UI) |

### Day-by-Day Plan

| Day | Tasks | Prompt IDs |
|---|---|---|
| Day 11 | Intelligence tables migration; analytics_computation_task (Celery); AnalyticsService (aggregate by topic/chapter/subject); PerformanceSnapshot persistence | P-017 |
| Day 12 | ScoreService: lock PerformanceScore formula v1; score_formula.py with version config; GET /dashboard/score | P-017 (continued) |
| Day 13 | HeatmapService: weakness threshold detection; weakness_signals upsert; weakness_detection_task; GET /dashboard/heatmap | P-019 |
| Day 14 | DashboardService: assemble dashboard response; Redis caching; GET /dashboard; cache invalidation on new attempt | P-018 |
| Day 15 | Frontend: Performance Dashboard + Heatmap UI components; TanStack Query integration | P-024 (partial) |

### PerformanceScore Formula (V1 — Lock Before Day 11)

**Formula Components:**
- accuracy_score = (correct / total_answered) × 100 [weight: 40%]
- consistency_score = (1 - std_dev_accuracy_across_attempts) × 100 [weight: 30%]
- breadth_score = (topics_attempted / total_topics) × 100 [weight: 20%]
- improvement_delta = current_accuracy - previous_accuracy [weight: 10%]

**Composite:** `performance_score = round((0.4 * accuracy_score) + (0.3 * consistency_score) + (0.2 * breadth_score) + (0.1 * improvement_delta))`

**Version:** Stored in `score_formula_config` table with `version=1` and `effective_from` date. All PerformanceSnapshot records reference `formula_version=1`. If formula changes post-launch, new version created; historical scores never recomputed.

> ⚠️ NOTE: This formula is inferred from blueprint description ("accuracy, consistency, and improvement trajectory") and must be explicitly locked by the developer before Day 11 implementation. Blueprint describes dimensions but does not specify exact weights.

### Phase 3 Dependencies

- Phase 2 must be complete (attempt_answers data must exist to test analytics)
- Celery task chain must connect: AttemptCompleted → analytics_computation_task → weakness_detection_task
- Redis must be available for dashboard caching

### Phase 3 Validation Criteria

- [ ] After test submission, analytics_computation_task completes within 30 seconds
- [ ] GET /dashboard returns correct data (not stale) after first Celery computation
- [ ] Weakness Heatmap shows correct subjects/chapters/topics with severity levels
- [ ] PerformanceScore correctly reflects accuracy, consistency, breadth, improvement
- [ ] Dashboard API returns cached response in < 300ms on subsequent calls
- [ ] Cache is invalidated when new attempt is submitted
- [ ] `pytest tests/test_intelligence/ -v` passes with 0 failures

---

## Phase 4: Recovery System + Polish (Week 4, Days 16–21)

### Objective
Build the Mistake Vault and Recovery Missions that deliver the product's core differentiation: "what should I do next?" Beta test with 5–10 real students.

### Phase Deliverables

| # | Deliverable | Validates |
|---|---|---|
| D4-1 | Migration 006 — recovery tables (mistakes, mistake_occurrences, recovery_missions, mission_tasks, weak_topic_recommendations) | Schema |
| D4-2 | MistakeService + classification_task (Celery) — root cause inference | F044 |
| D4-3 | GET /mistakes API — Mistake Vault listing | F044 |
| D4-4 | RecoveryService + mission_generation_task — missions from heatmap + vault + score | F045 |
| D4-5 | Mission lifecycle APIs (start, task completion, complete) | F045 |
| D4-6 | RecommendationService + GET /recommendations | F047 |
| D4-7 | Frontend: Mistake Vault UI | F044 (UI) |
| D4-8 | Frontend: Recovery Missions UI | F045 (UI) |
| D4-9 | End-to-end journey test (registration → test → dashboard → missions) | Full loop |
| D4-10 | Load test (50 concurrent attempt submissions) | NFR |
| D4-11 | Sentry integration; structlog setup | Observability |
| D4-12 | CI pipeline finalization; staging deployment | OBJ-10 |
| D4-13 | Beta testing with 5–10 real students | Validation |

### Day-by-Day Plan

| Day | Tasks | Prompt IDs |
|---|---|---|
| Day 16 | Recovery tables migration; MistakeService; classification_task (Celery); GET /mistakes | P-020 |
| Day 17 | Mistake recurrence detection; GET /mistakes/patterns; Mistake Vault UI | P-020 (continued), P-024 (partial) |
| Day 18 | RecoveryService; mission_generation_task; cold start logic; 3-mission cap | P-021 |
| Day 19 | Mission lifecycle APIs (start, tasks, complete); RecommendationService; GET /recommendations; Missions UI | P-022, P-023, P-024 (partial) |
| Day 20 | End-to-end test; load test; N+1 query fixes; Sentry + structlog | P-025 |
| Day 21 | CI finalization; staging deploy; beta test support; documentation update | P-025 (continued) |

### Phase 4 Dependencies

- Phase 3 must be complete (weakness_signals and performance_snapshots must exist for mission generation)
- Celery task chain must include: WeaknessDetected → classification_task + mission_generation_task
- Cold start rule must be implemented before mission_generation_task is tested

### Phase 4 Validation Criteria

- [ ] Mistake Vault correctly classifies wrong answers by root cause
- [ ] Mission generation produces 1–3 missions from heatmap + vault inputs
- [ ] Mission cap of 3 active missions enforced (4th generation creates new and dismisses oldest or refuses)
- [ ] Student with < 3 attempts receives max 1 mission (cold start rule)
- [ ] Mission completion correctly updates WeaknessSignal severity
- [ ] GET /recommendations returns ordered weak topic list
- [ ] Full loop test passes: register → test → dashboard → missions → mission complete
- [ ] 50 concurrent submissions pass load test without data corruption
- [ ] Sentry captures errors in staging environment
- [ ] `pytest --cov --cov-fail-under=80` passes CI gate

---

## Dependency Graph Summary

### Critical Path (must be completed sequentially)

```
M01 → M02 → M03 → M04 → M05 (F026) → M06 → M07
```

No phase can skip. F026 is the convergence point everything depends on.

### Parallel Work Streams

| Stream | Can Proceed Alongside |
|---|---|
| M08 Frontend (Auth + Profile pages) | During M02 implementation |
| M08 Frontend (Question browsing) | During M04 implementation |
| M09 Observability setup | During M06/M07 implementation |
| Frontend Test Session UI (structure) | During M05, before API is complete (mock data) |

### Major Blockers

| Blocker | Blocked By | Unblocks |
|---|---|---|
| F026 not implemented | M05 not complete | F027, F028, F031, F044, F045, F047 |
| PerformanceScore formula not locked | Developer decision | M06 Day 11 implementation |
| Celery tasks not tested | M01 Celery not running | All async analytics |
| Questions not imported | M04 not complete | F016 (no questions = no test possible) |

### High-Risk Dependencies

| Dependency | Risk | Mitigation |
|---|---|---|
| F026 → all intelligence | CRITICAL | Extensive integration tests (T-022–T-030) before proceeding to M06 |
| Celery task chain | HIGH | Each task individually testable; retry policy configured |
| Score formula lock | HIGH | Decide formula before Day 11; document in score_formula.py comments |
| Import file encoding | MEDIUM | Explicit UTF-8 handling in import parser |

---

## End-to-End Completion Milestones

| Milestone | Day | Gate |
|---|---|---|
| Auth works end-to-end | Day 2 | Student can register + login |
| Question import works | Day 5 | 100 questions imported via CSV |
| Test can be taken | Day 10 | Student completes 180-question mock, gets score |
| Analytics pipeline fires | Day 12 | Dashboard visible < 30s after submission |
| Weakness Heatmap visible | Day 13 | Heatmap shows correct topic severity |
| Missions generated | Day 18 | Student sees 1–3 recovery missions |
| Full loop validated | Day 20 | End-to-end journey test passes |
| Beta ready | Day 21 | Staging deployed; 5–10 students can use system |

---

*Batch 3 of 6 — Continue to BATCH_4_Prompts.md*
