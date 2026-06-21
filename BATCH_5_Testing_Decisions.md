# NEET POS — Execution System · Batch 5 of 6
# Layer 8: Validation & Testing + Layer 8.5: Decision Log

---

# LAYER 8: VALIDATION AND TESTING SYSTEM

## Testing Architecture

| Layer | Tool | Coverage Target | Run Trigger |
|---|---|---|---|
| Unit tests | pytest | ≥ 80% lines | Every commit (CI) |
| Integration tests | pytest + httpx (async test client) | All API endpoints | Every commit (CI) |
| Celery task tests | pytest + Celery eager mode | All tasks | Every commit |
| Load tests | locust or k6 | 50 concurrent users | Pre-release only |
| E2E journey tests | Manual script / pytest | Full loop | Pre-release |

**Test file structure:** See BATCH_2_Modules_Dependencies.md → Backend File Structure → tests/

---

## T-001 — Registration: Happy Path

**Prompt:** P-001 | **Req:** F001

### Unit Tests
- `test_register_success`: valid payload → 201, user_id returned, no password in response
- `test_password_hashed_with_argon2`: verify stored hash starts with `$argon2`
- `test_profile_created_on_register`: profile row exists after registration

### Integration Tests
- POST /auth/register with valid payload → 201
- POST /auth/register with existing email → 409

### Edge Cases
- Email with uppercase → normalized to lowercase
- Password exactly 8 chars → accepted
- Password 7 chars → 422
- target_year missing → 422

### Failure Cases
- DB connection down → 503
- Email service down → 201 (registration succeeds; email failure logged but not surfaced to user)

---

## T-002 — Registration: Audit Log

**Prompt:** P-001 | **Req:** F001

### Integration Tests
- After registration: `audit_logs` table contains row with event_type=USER_REGISTERED, user_id matching new user
- audit_logs row cannot be updated (verify no UPDATE endpoint exists)

---

## T-003 — Login: Happy Path

**Prompt:** P-002 | **Req:** F002

### Unit Tests
- `test_jwt_access_token_issued`: token decodes with correct user_id and role
- `test_refresh_token_in_redis`: after login, refresh token UUID exists in Redis
- `test_login_audit_event`: LOGIN_SUCCESS in audit_logs after successful login

### Integration Tests
- POST /auth/login → 200, access_token in body, refresh_token cookie set
- Decode access_token: exp = ~15 minutes from now

### Edge Cases
- Login with unverified email → 403 (FORBIDDEN, not 401)
- Login with correct email, wrong password → 401
- Account suspended → 403

### Failure Cases
- 5th consecutive failed login → 429 (account locked)
- Login after lock: correct password → still 429 (must wait for timeout)

---

## T-004 — Token Refresh + Rotation

**Prompt:** P-002 | **Req:** F002

### Integration Tests
- POST /auth/refresh with valid cookie → 200, new access_token returned
- POST /auth/refresh after logout → 401 (refresh token revoked)
- POST /auth/refresh: old refresh token not reusable after rotation (replay prevention)

### Security Checks
- Access token not stored in cookie (only in response body)
- Refresh token is opaque UUID (not JWT — cannot be decoded for info)

---

## T-005 — Profile Management

**Prompt:** P-003 | **Req:** F003

### Integration Tests
- GET /profile without auth → 401
- GET /profile → returns correct profile for authenticated user
- PATCH /profile `{"target_score": 750}` → 422 (out of range 0-720)
- PATCH /profile partial update → only changed fields updated, others preserved
- PATCH /profile: student cannot update another student's profile → 403

---

## T-006 — RBAC: Permission Enforcement

**Prompt:** P-004 | **Req:** F005

### Integration Tests
- Student POST /questions → 403
- Teacher POST /questions → 201
- Student DELETE /questions/:id → 403
- Admin DELETE /questions/:id → 200
- Student POST /tests/:id/attempts → 200 (allowed)
- Unauthenticated GET /tests → 401

---

## T-007 — RBAC: Role Assignment

**Prompt:** P-004 | **Req:** F005

### Unit Tests
- New user via registration → student role auto-assigned
- `RBACService.has_permission(student_id, "questions", "write")` → False
- `RBACService.has_permission(teacher_id, "questions", "write")` → True

---

## T-008 — Taxonomy Seeding

**Prompt:** P-005 | **Req:** F010, F011, F012

### Integration Tests
- GET /subjects → 3 subjects (Physics, Chemistry, Biology)
- GET /subjects/:id/chapters → chapters ordered by sequence
- GET /chapters/:id/topics → topics ordered by sequence
- Double seeding → no duplicate subjects created (idempotent)

### Edge Cases
- Missing subject_id in chapter request → 404
- Missing chapter_id in topic request → 404

---

## T-009 — Question Bank: CRUD

**Prompt:** P-006 | **Req:** F006, F008, F009

### Integration Tests
- POST /questions with 4 options (1 correct) → 201
- POST /questions with 0 correct options → 422
- POST /questions with 2 correct options → 422
- GET /questions returns published questions only (excludes draft)
- PATCH /questions/:id → updates fields; version incremented
- DELETE /questions/:id → sets status=archived (not physical delete)
- GET /questions/:archived_id → question still retrievable (with archived status)

### Edge Cases
- question_text empty → 422
- subject_id not found → 404
- topic_id belonging to different chapter than chapter_id → 422 (consistency check)

---

## T-010 — Question Status Workflow

**Prompt:** P-006 | **Req:** F006

### Unit Tests
- `test_question_publish_without_correct_answer`: publish attempt on question with no correct option → raises BusinessError
- `test_question_status_transitions`: draft → review → approved → published → archived (valid)
- `test_question_status_reverse_invalid`: published → draft is NOT allowed

---

## T-011 — Import Pipeline: Happy Path

**Prompt:** P-007 | **Req:** F007

### Integration Tests
- Upload 100-row valid CSV → 202, import_id returned
- Poll GET /imports/:id → status=processing initially
- Poll after task completes → status=completed, success_count=100
- GET /questions → 100 new questions exist

### Performance Checks
- Upload 1,000-row CSV → task completes within 120 seconds

---

## T-012 — Import Pipeline: Error Handling

**Prompt:** P-007 | **Req:** F007

### Integration Tests
- Upload file > 10MB → 413 at upload time
- Upload 1,001-row CSV → error_rows contains count error, 0 committed
- CSV with 90 valid rows + 10 invalid rows → success_count=90, error_count=10, error_rows has 10 entries
- Non-UTF-8 CSV (latin-1 encoding) → parsed correctly (encoding fallback)
- Unsupported file extension (.doc) → 400

---

## T-013 — PYQ Database

**Prompt:** P-006 | **Req:** F008

### Integration Tests
- POST /questions with is_pyq=true, pyq_year=2023 → persisted correctly
- GET /questions?is_pyq=true → only PYQ questions returned
- GET /questions?is_pyq=true&pyq_year=2023 → year-filtered

---

## T-014 — Question Tagging

**Prompt:** P-006 | **Req:** F009

### Integration Tests
- POST /questions with tags=[...] → question created with tags
- GET /questions/:id → includes tag list
- GET /questions?tags=genetics → returns questions tagged with genetics

---

## T-015 — Question Search

**Prompt:** P-008 | **Req:** F014

### Integration Tests
- GET /questions/search?q=photosynthesis → returns questions containing "photosynthesis"
- GET /questions/search?subject_id=X&difficulty=hard → filtered results
- GET /questions/search with cursor → pagination works correctly
- Student role GET /questions/search → 403

### Performance Checks
- Search on 1,000 questions database → < 200ms

---

## T-016 — Full NEET Mock Structure

**Prompt:** P-009 | **Req:** F016

### Integration Tests
- GET /tests → seeded Full NEET Mock appears
- GET /tests/:id → returns 3 sections (Physics/Chemistry/Biology)
- Section summary shows 60 questions per section
- POST /tests as Student → 403

---

## T-017 — Unit Test Structure

**Prompt:** P-010 | **Req:** F017

### Integration Tests
- POST /tests `{"test_type": "unit_test", "chapter_id": ":id", "question_count": 30}` → 201
- GET /tests/:new_id → duration_mins=60
- All questions in unit test belong to specified chapter_id

---

## T-018 — Mixed Revision Test Structure

**Prompt:** P-011 | **Req:** F018

### Integration Tests
- POST /tests `{"test_type": "mixed_revision", "topic_ids": [...], "question_count": 45}` → 201
- GET /tests/:new_id → duration_mins=90
- Questions span multiple topics from provided topic_ids

---

## T-019 — Timer Engine

**Prompt:** P-012 | **Req:** F023

### Unit Tests
- `test_timer_not_expired`: started 60 min ago, 180 min test → not expired
- `test_timer_expired`: started 185 min ago, 180 min test + 5 min grace → accepted
- `test_timer_abuse`: started 200 min ago → rejected

### Integration Tests
- Attempt start response includes `duration_seconds=10800`
- time_spent_seconds negative in PATCH → 422

---

## T-020 — OMR Simulation

**Prompt:** P-013 | **Req:** F024

### Integration Tests
- PATCH answers with `changed=true` (different option) → attempt_answer.answer_changed=true
- PATCH answer with `selected_option_id=null` → skipped=true
- PATCH with `marked_review=true` → is_marked_review=true in DB
- GET /attempts/:id → all OMR fields present

---

## T-021 — Negative Marking Scoring

**Prompt:** P-014 | **Req:** F025

### Unit Tests
- 135 correct, 0 wrong, 45 unattempted → score=540
- 100 correct, 45 wrong, 35 unattempted → score=355
- 0 answers → score=0
- All 180 wrong → score=-45

### Integration Tests
- POST /attempts/:id/submit → response includes correct, incorrect, unattempted breakdown
- is_correct=true set on correct attempt_answers in DB post-scoring

### Security Checks
- Client-provided "is_correct" value is ignored; truth comes from answer_options.is_correct lookup

---

## T-022 — F026: Duplicate Submission Prevention

**Prompt:** P-016 | **Req:** F026

### Integration Tests
- POST /attempts/:id/submit → 200
- POST /attempts/:id/submit again → 200 with same score (not re-computed)
- Database: attempt scored only once (verify by checking audit or timestamps)

---

## T-023 — F026: Duplicate Attempt Start Prevention

**Prompt:** P-015 | **Req:** F026

### Integration Tests
- POST /tests/:id/attempts → creates attempt (201)
- POST /tests/:id/attempts again → returns existing in-progress attempt (200, NOT 201)
- Two attempts for same user+test should not exist in DB (UNIQUE constraint)

---

## T-024 — F026: Session Recovery

**Prompt:** P-015 | **Req:** F026

### Integration Tests
- Start attempt → save 50 answers → flush Redis (simulate crash) → GET /attempts/:id → returns 50 answers from DB
- Start attempt → save 50 answers → GET /attempts/:id → Redis hit (50 answers returned fast)

### Edge Cases
- GET /attempts/:id for attempt belonging to different user → 403

---

## T-025 — F026: Timer Expiry Auto-Submit

**Prompt:** P-012, P-016 | **Req:** F026, F023

### Integration Tests
- Simulate timer expiry (mock started_at to be 185 min ago): POST /attempts/:id/submit?force=true → 200
- started_at 200 min ago + force=true → 403 (abuse detection)

---

## T-026 — F026: Zero Answers Submission

**Prompt:** P-016 | **Req:** F026

### Integration Tests
- Start attempt → submit immediately (0 answers saved) → score=0, unattempted=180

---

## T-027 — F026: Answer Change Tracking

**Prompt:** P-013, P-015 | **Req:** F026, F024

### Integration Tests
- Save answer for Q1 (option A) → save answer for Q1 (option B) → attempt_answers: answer_changed=true, selected_option_id=option_B
- Scoring: Q1 scored on option_B (final selection), not option_A

---

## T-028 — F026: Review Flag Without Answer

**Prompt:** P-013 | **Req:** F026, F024

### Integration Tests
- PATCH answers: Q1 with marked_review=true, selected_option_id=null → is_marked_review=true, skipped=true, score contribution = 0

---

## T-029 — F026: Concurrent Answer Save Race Condition

**Prompt:** P-015 | **Req:** F026

### Integration Tests
- Simulate 2 concurrent PATCH requests for same question → no duplicate rows (UNIQUE constraint enforced)
- Final state should be one of the two answers (last write wins)

### Performance Checks
- 10 concurrent PATCH requests to same attempt → all return 200, < 100ms each

---

## T-030 — F026: Answer After Submission

**Prompt:** P-015, P-016 | **Req:** F026

### Integration Tests
- POST submit → attempt status=submitted
- PATCH answers after submit → 409 CONFLICT
- attempt_answers table: no rows added after submission timestamp (immutability check)

---

## T-031 — Analytics Computation

**Prompt:** P-017 | **Req:** F027, F031

### Integration Tests
- Submit attempt → wait for Celery → GET /dashboard → performance_score present
- topic_analytics rows exist for all topics in the test
- PerformanceSnapshot created with formula_version=1
- Running analytics task twice → same result, no duplicate snapshots

### Performance Checks
- Analytics computation completes within 30 seconds on 180-question test

---

## T-032 — Dashboard API + Caching

**Prompt:** P-018 | **Req:** F027

### Integration Tests
- GET /dashboard with no attempts → 200 with empty/zero data
- GET /dashboard after test completion → populated data
- GET /dashboard twice in 5 minutes → second response served from Redis
- Submit new attempt → GET /dashboard → cache invalidated (fresh data)

### Performance Checks
- Cached GET /dashboard → < 300ms response time

---

## T-033 — Weakness Heatmap

**Prompt:** P-019 | **Req:** F028

### Unit Tests
- accuracy_pct=25% → severity=critical
- accuracy_pct=45% → severity=high
- accuracy_pct=60% → severity=medium
- accuracy_pct=75% → severity=low
- accuracy_pct=85% → no weakness_signal created

### Integration Tests
- After test submission + Celery tasks: GET /dashboard/heatmap → correct nested structure
- Second test with same topic: upsert (not duplicate) weakness_signal

---

## T-034 — Performance Score Formula

**Prompt:** P-017 | **Req:** F031

### Unit Tests
- `test_score_formula_deterministic`: same inputs always produce same score
- `test_score_in_range`: score always 0–100
- `test_score_version_1_used`: PerformanceSnapshot.formula_version = 1

### Integration Tests
- Score changes correctly after multiple attempts (trend direction correct)
- First attempt: consistency_score = 100 (no prior std dev)

---

## T-035 — Mistake Vault: Classification

**Prompt:** P-020 | **Req:** F044

### Unit Tests
- `test_classify_guessing`: time_spent=15, wrong → guessing
- `test_classify_timing`: time_spent=200, wrong → timing
- `test_classify_confidence`: answer_changed=true, wrong → confidence (higher priority than difficulty rules)
- `test_classify_conceptual`: difficulty=hard, time=60, not changed → conceptual
- `test_classify_application`: difficulty=medium, time=60, not changed → application

### Integration Tests
- After attempt with 30 wrong answers → GET /mistakes → 30 mistakes classified
- Same question wrong in 2 attempts → recurrence_count=2
- GET /mistakes/patterns → root_cause breakdown with correct counts

---

## T-036 — Mistake Vault: Recurrence + Resolution

**Prompt:** P-020 | **Req:** F044

### Integration Tests
- Mistake resolved via mission completion → resolved_at set
- GET /mistakes → resolved mistakes not in default list (unless filter=all)
- Physical delete of mistake: NOT possible (append-only verified)

---

## T-037 — Mission Generation

**Prompt:** P-021 | **Req:** F045

### Integration Tests
- User with 1 attempt → max 1 mission generated
- User with 3+ attempts, 3 critical weaknesses → 3 missions generated
- User already has 3 active missions → no new missions (cap enforced)
- Mission tasks: each mission has 3–5 tasks of correct task_types

---

## T-038 — Mission Execution Lifecycle

**Prompt:** P-022 | **Req:** F045

### Integration Tests
- POST /missions/:id/start → status=executing
- PATCH /missions/:id/tasks/:t2 before completing t1 → 409 (sequence enforced)
- Complete all tasks → POST /missions/:id/complete → status=completed
- WeaknessSignal severity decremented after mission complete

---

## T-039 — Weak Topic Recommendations

**Prompt:** P-023 | **Req:** F047

### Integration Tests
- GET /recommendations → topics ordered by severity weight × (1 - accuracy)
- Resolved weakness_signals excluded from recommendations
- Empty weaknesses → GET /recommendations → 200 with empty list

---

## Load and Performance Testing (pre-beta)

### Load Test Scenario: 50 Concurrent Submissions

```
Setup: 50 virtual users, each with in-progress attempt with 180 answers saved
Action: All 50 call POST /attempts/:id/submit simultaneously
Assertions:
  - All 50 return 200 (no 500 errors)
  - All 50 scores are correct (verify against known answer keys)
  - No duplicate PerformanceSnapshot records
  - All 50 Celery analytics tasks queued (verify queue depth)
Success Criteria:
  - 0% data corruption
  - < 5% error rate
  - P95 response time < 3 seconds
```

---

# LAYER 8.5: DECISION LOG

All assumptions, interpretations, and inferences from the blueprint are recorded here. Each is flagged by risk level.

---

## DEC-001 — PerformanceScore Formula Weights

**Decision ID:** DEC-001
**Assumption:** The blueprint describes PerformanceScore as based on "accuracy, consistency, and improvement trajectory" but does not specify exact weights or formula.
**Interpretation Applied:** Assigned weights: accuracy=40%, consistency=30%, breadth=20%, improvement_delta=10%. Four components used.
**Reasoning:** These weights reflect the blueprint's stated priority order (accuracy first, trajectory secondary) and align with standard educational assessment weighting.
**Potential Risk:** Formula may produce scores that don't match product owner's mental model. Stakeholder may want different weighting.
**Validation Needed:** Product owner must review and approve formula weights BEFORE Day 11 implementation.
**Impact Level:** HIGH
**Documented In:** intelligence/score_formula.py, BATCH_3_Roadmap.md §Phase 3 formula section

---

## DEC-002 — Weakness Detection Thresholds

**Decision ID:** DEC-002
**Assumption:** Blueprint describes severity levels (critical/high/medium/low) but does not specify accuracy thresholds for each level.
**Interpretation Applied:** critical < 30%, high 30–50%, medium 50–65%, low 65–80%, no signal > 80%.
**Reasoning:** NEET is a high-stakes exam; 50% accuracy is considered poor. Thresholds reflect this domain context.
**Potential Risk:** Thresholds may be too strict (too many critical flags) or too loose, causing student anxiety or complacency.
**Validation Needed:** Beta test feedback from 5–10 students needed to calibrate.
**Impact Level:** MEDIUM
**Documented In:** intelligence/service.py (HeatmapService), config.py (configurable)

---

## DEC-003 — Email Service Provider

**Decision ID:** DEC-003
**Assumption:** Blueprint requires email verification but does not specify an email service provider.
**Interpretation Applied:** Assume SendGrid (industry standard) or SMTP via environment configuration.
**Reasoning:** Email service is external and can be swapped without code changes if abstracted via a NotificationService.
**Potential Risk:** If the founder has a preferred provider, integration may need minor adaptation.
**Validation Needed:** Confirm email provider before implementing email_notification_task.
**Impact Level:** LOW
**Documented In:** workers/notification_tasks.py

---

## DEC-004 — Mission Cap Enforcement — Creation vs Display

**Decision ID:** DEC-004
**Assumption:** Blueprint states "RecoveryMissions are capped at 3 active per user" but doesn't specify if this is enforced at generation time or display time.
**Interpretation Applied:** Enforced at generation time. mission_generation_task checks active mission count before creating new ones. If count = 3, no new mission is created (not dismissed).
**Reasoning:** Generating missions the student never sees wastes compute. Better to not generate than to generate and hide.
**Potential Risk:** If missions are generated but hidden, students get fresh missions faster. Current approach may feel "stuck."
**Validation Needed:** Monitor if students dismiss missions regularly; if yes, consider auto-generation on dismissal.
**Impact Level:** MEDIUM
**Documented In:** recovery/service.py (RecoveryService), P-021

---

## DEC-005 — Cold Start Threshold

**Decision ID:** DEC-005
**Assumption:** Blueprint identifies cold start as a risk for students with "sparse data." The threshold (< 3 attempts) and behavior (1 mission max) are inferred.
**Interpretation Applied:** < 3 completed attempts = cold start. Generate max 1 mission (highest priority weakness only).
**Reasoning:** 3 attempts provides sufficient signal for pattern detection (mistake recurrence, consistency computation).
**Potential Risk:** Overly conservative; students may want more missions after first test.
**Validation Needed:** Track mission dismissal rates and mission completion rates at 1 vs 3 attempts.
**Impact Level:** MEDIUM
**Documented In:** workers/mission_tasks.py, P-021

---

## DEC-006 — Root Cause Classification Priority Order

**Decision ID:** DEC-006
**Assumption:** Blueprint provides 7 root cause types and their inference rules but does not specify priority when multiple rules match simultaneously.
**Interpretation Applied:** Priority order: 1. guessing (time < 20s), 2. timing (time > 180s), 3. confidence (answer_changed), 4. conceptual/application/memory (difficulty-based). If time < 20s AND answer_changed → classified as guessing (time signal dominates).
**Reasoning:** Behavioral signals (timing extremes, changes) are stronger indicators than difficulty-based heuristics.
**Potential Risk:** Overlapping cases may be misclassified. Blueprint notes classification accuracy is "acceptable at MVP."
**Validation Needed:** Student feedback on Mistake Vault accuracy; add "Reclassify" feature at MVP per blueprint note.
**Impact Level:** LOW
**Documented In:** recovery/classifier.py, P-020

---

## DEC-007 — Dashboard Analytics Eventual Consistency

**Decision ID:** DEC-007
**Assumption:** Blueprint says "near-real-time (post-submission computation) is acceptable." Target time not specified.
**Interpretation Applied:** Target: analytics available within 30 seconds of submission. Acceptable: up to 60 seconds.
**Reasoning:** Celery with 2 workers should compute 180-answer analytics in well under 30 seconds.
**Potential Risk:** High-concurrency periods (many students submitting simultaneously) could delay analytics computation beyond 30 seconds.
**Validation Needed:** Load test analytics computation time under 50 concurrent submissions.
**Impact Level:** MEDIUM
**Documented In:** BATCH_3_Roadmap.md, Phase 3 validation criteria

---

## DEC-008 — Taxonomy Seeding Approach

**Decision ID:** DEC-008
**Assumption:** Blueprint requires NEET taxonomy (Physics/Chemistry/Biology hierarchy) but does not specify exact chapters/topics to seed.
**Interpretation Applied:** Seed 3 subjects, 10+ chapters, 30+ topics covering major NEET areas. Exact topic list is a content decision, not an engineering decision.
**Reasoning:** The engineering concern is the seeding mechanism; the content (specific chapter/topic names) should be provided by the product owner.
**Potential Risk:** Seeded taxonomy may not match the question import CSV column values, causing import failures.
**Validation Needed:** Confirm taxonomy list before question import is tested.
**Impact Level:** MEDIUM
**Documented In:** content/service.py (TaxonomyService.seed_neet_taxonomy), P-005

---

## DEC-009 — Redis Active Test Cache Size

**Decision ID:** DEC-009
**Assumption:** Blueprint specifies `active_test:{attempt_id}` with 3-hour TTL but does not specify what data to cache.
**Interpretation Applied:** Cache the full current answer state as JSON: {attempt_id, question_ids (ordered), current_answers: [{question_id, selected_option_id, time_spent, is_marked_review}]}.
**Reasoning:** Caching the full answer state enables fast session recovery without DB query. 180 answers × ~200 bytes ≈ 36KB per active test — well within Redis capacity.
**Validation Needed:** Verify Redis memory usage at 100 concurrent active tests.
**Impact Level:** LOW
**Documented In:** shared/cache/redis.py, P-015

---

## DEC-010 — Score History Depth

**Decision ID:** DEC-010
**Assumption:** GET /dashboard/score and improvement_trend are mentioned but trend depth (how many historical attempts to show) is not specified.
**Interpretation Applied:** Default: last 10 attempts for trend chart. Default: last 5 for improvement_delta calculation.
**Reasoning:** 10 attempts provides meaningful trend visualization; 5 is sufficient for consistency score calculation without being too computationally expensive.
**Potential Risk:** Students early in prep (< 5 attempts) see sparse trend charts.
**Validation Needed:** UI feedback on trend chart readability with < 5 data points.
**Impact Level:** LOW
**Documented In:** intelligence/service.py (DashboardService), P-018

---

*Batch 5 of 6 — Continue to BATCH_6_Risks_Memory.md*
