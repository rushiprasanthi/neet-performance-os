# NEET Performance Operating System — Batch 6
## Engineering Intelligence Blueprint: Final Governance Layer

**Document Type:** Governance, Risk, Validation & Project Memory  
**Source Authority:** NEET_POS_Engineering_Blueprint.md (all 15 sections)  
**Status:** Final Batch — Implementation Governance Reference  
**Assumes Complete:** Batches 1–5 (Analysis, Architecture, Modules, Dependencies, Roadmap, Implementation Prompts, Testing)

---

## Layer 8.5 — Decision Log

> Every major architectural decision derived from the blueprint, classified by impact level, with alternatives considered and validation requirements.

---

### DEC-001 — FastAPI as Backend Framework

| Field | Detail |
|---|---|
| **Decision ID** | DEC-001 |
| **Decision** | Use FastAPI (Python 3.11+) as the sole backend framework |
| **Reasoning** | Async-native request handling supports concurrent test submissions and analytics dispatch without blocking. Pydantic model validation reduces validation boilerplate across all 25 API surface endpoints. OpenAPI schema is auto-generated, enabling immediate API contract documentation for frontend integration. Type safety improves maintainability in a solo-founder context with no dedicated code reviewer. |
| **Alternatives Considered** | Django REST Framework (heavier ORM coupling, synchronous-first, unsuitable for Celery-heavy async patterns); Flask (too minimal, would require assembling an async ecosystem manually); Node.js/Express (ecosystem diverges from Python-native ML path planned for Phase 3 root cause classification) |
| **Risks** | Python GIL limits true CPU parallelism under heavy analytics load; mitigated by Celery offloading CPU-bound tasks. FastAPI's async ecosystem requires careful handling of blocking ORM calls (must use SQLAlchemy async driver consistently). |
| **Validation Required** | Async endpoint benchmarks under 50 concurrent test submissions. Confirmation that all repository layer calls use `async/await` patterns. |
| **Impact Level** | HIGH — All backend code, all API contracts, and the Celery worker pattern depend on this choice. |

---

### DEC-002 — PostgreSQL as Primary Data Store

| Field | Detail |
|---|---|
| **Decision ID** | DEC-002 |
| **Decision** | Use PostgreSQL 16 as the single source of truth for all domains |
| **Reasoning** | ACID guarantees are non-negotiable for attempt data — a corrupted or lost AttemptAnswer row permanently damages a student's intelligence history. PostgreSQL JSONB supports flexible fields (notification preferences, question metadata) without schema churn. Materialized views handle analytics aggregation at MVP scale. Full-text search is available for future question search expansion without adding another data store. |
| **Alternatives Considered** | MySQL (weaker JSONB support, materialized views less capable); MongoDB (insufficient ACID guarantees for scoring data; poor JOIN performance for analytics queries); Supabase (PostgreSQL under the hood — adds abstraction overhead without benefit at MVP scale) |
| **Risks** | OLAP query contention with transactional writes on the same instance becomes a problem at 5,000+ daily attempts. The `attempt_answers` table will grow to 13M rows annually and requires partitioning planning. |
| **Validation Required** | Index coverage validated for all analytics queries before launch. Explain-plan review on dashboard aggregation queries. Confirm partition strategy is documented for the 50M row threshold. |
| **Impact Level** | HIGH — Every domain's schema, every migration, and the entire repository layer depends on this choice. |

---

### DEC-003 — Redis for Active Test State + Session Caching

| Field | Detail |
|---|---|
| **Decision ID** | DEC-003 |
| **Decision** | Use Redis 7 for active test state (`active_test:{attempt_id}`), session metadata, and dashboard caching; use Redis as the Celery message broker |
| **Reasoning** | In-progress test state must survive a browser crash without requiring a database write on every answer event. Redis provides sub-millisecond read/write for active state with a 3-hour TTL. Using Redis as the Celery broker reduces operational complexity by eliminating RabbitMQ as a separate service at MVP scale. |
| **Alternatives Considered** | RabbitMQ for Celery broker (more robust, but operational overhead not justified at MVP; upgrade path preserved); localStorage only (insufficient — student answers are lost on device change or incognito session); Memcached (no persistence option, insufficient for state recovery use case) |
| **Risks** | Redis instance failure during a live test session would leave active test state unrecoverable from cache. Mitigated by: (1) localStorage tertiary backup on the client every 30 seconds, (2) PostgreSQL AttemptAnswer table as the authoritative fallback. Redis TTL misconfiguration could expire active test state mid-session. |
| **Validation Required** | Redis failure simulation: confirm test state recovery falls back to PostgreSQL AttemptAnswers correctly. TTL configuration review (3-hour active test, 5-minute dashboard, 1-hour question list). |
| **Impact Level** | HIGH — Active test session reliability, Celery task dispatch, and dashboard performance all depend on Redis. |

---

### DEC-004 — Celery for Asynchronous Analytics Computation

| Field | Detail |
|---|---|
| **Decision ID** | DEC-004 |
| **Decision** | All post-submission analytics (PerformanceSnapshot, WeaknessSignal, MistakeClassification, RecoveryMission) are computed by Celery workers, not in the submission API request |
| **Reasoning** | Test submission must return a response within 300ms to deliver a good user experience. Analytics computation across 180 AttemptAnswer rows with joins to topics, chapters, and subjects takes 2–10 seconds. Decoupling scoring (synchronous, fast) from analytics (async, heavy) keeps the submission API response time user-acceptable while ensuring full intelligence computation. |
| **Alternatives Considered** | Synchronous analytics on submission (causes 10+ second response times, unacceptable); FastAPI BackgroundTasks (insufficient for retry logic, monitoring, and cross-task sequencing); Django-Q (less ecosystem support for a FastAPI stack) |
| **Risks** | Celery worker failure mid-computation leaves analytics in a partially computed state. Mitigated by: (1) idempotent task design (re-running a task on the same attempt_id produces the same result), (2) retry policy (3 retries, exponential backoff), (3) dead-letter queue for failed tasks. |
| **Validation Required** | Celery worker crash simulation: confirm retry policy restores analytics within 5 minutes. Task idempotency test: trigger the same analytics task twice on the same attempt_id, confirm no duplicate records. |
| **Impact Level** | HIGH — F027, F028, F031, F044, F045, and F047 all depend on Celery execution succeeding reliably. |

---

### DEC-005 — Attempt Tracking at Atomic Answer Level (F026 Design)

| Field | Detail |
|---|---|
| **Decision ID** | DEC-005 |
| **Decision** | Track every student answer event as a row in `attempt_answers`, capturing: selected_option_id, time_spent_seconds, answer_changed boolean, marked_review boolean |
| **Reasoning** | The core product thesis requires root cause classification of wrong answers. This classification requires behavioral signals at the individual answer level: time spent (guessing vs overthinking), answer changes (confidence issues), review flags (uncertainty signals). Without atomic tracking, the intelligence layer produces only outcome data (right/wrong) rather than process data (how the student engaged with the question). |
| **Alternatives Considered** | Session-level aggregation only (insufficient for root cause classification); Event log table separate from answers (increases query complexity for analytics joins); JSON blob per attempt (unindexable, analytics become full table scans) |
| **Risks** | `attempt_answers` becomes the fastest-growing table in the system (180 rows per test × N tests daily). Without partitioning, query performance degrades at 50M rows. |
| **Validation Required** | Performance test: confirm dashboard analytics query time under 1 second at 500,000 attempt_answers rows. Index coverage on `attempt_id`, `question_id`, and composite `(user_id, topic_id)`. |
| **Impact Level** | HIGH — Every intelligence feature in the MVP derives from this table. Incorrect design invalidates all downstream features. |

---

### DEC-006 — Idempotent Submission with Synchronous Scoring

| Field | Detail |
|---|---|
| **Decision ID** | DEC-006 |
| **Decision** | Test submission computes NEET score (+4/-1/0) synchronously and returns it immediately; idempotency key prevents duplicate scoring on network retry |
| **Reasoning** | Students expect to see their score immediately after submitting. A 200–300ms synchronous scoring response is achievable (iterate 180 AttemptAnswers, apply scoring rules — this is O(n), not a complex query). Idempotency is required because browser network failures cause submission retries; without it, a student could be credited with a second attempt or have their score overwritten. |
| **Alternatives Considered** | Async scoring (unacceptable UX — student sees no score for 10+ seconds after submission); Optimistic scoring on frontend (score is fabricated until server confirms — creates trust issues if mismatch occurs) |
| **Risks** | A ScoringService bug that produces incorrect NEET scores would affect all students silently unless test coverage is comprehensive. Score reversal after a bug fix is operationally complex. |
| **Validation Required** | Unit tests for all scoring edge cases: all correct, all incorrect, all unanswered, mixed, boundary cases. Integration test: submit duplicate attempt, confirm second call returns same score without re-computation. |
| **Impact Level** | HIGH — Incorrect scoring is a trust-destroying product failure. |

---

### DEC-007 — Heuristic Root Cause Classification at MVP

| Field | Detail |
|---|---|
| **Decision ID** | DEC-007 |
| **Decision** | Classify Mistake Vault root causes using rule-based heuristics (time_spent thresholds, difficulty level, answer_changed flag) rather than ML models |
| **Reasoning** | ML models require labeled training data that does not exist until the platform accumulates thousands of attempts. Building an ML pipeline before data exists wastes implementation cycles and cannot be validated. Heuristic rules produce meaningful signal at MVP: a question answered in under 20 seconds and answered incorrectly is a valid guessing signal. The heuristic outputs become the future training dataset for ML classification. |
| **Alternatives Considered** | GPT-4 classification via API on each wrong answer (cost-prohibitive at scale, latency-adding, overkill for structured behavioral signals); No classification at launch (eliminates Mistake Vault differentiation entirely); Simple binary correct/incorrect only (not a differentiated product) |
| **Risks** | Heuristic classification will produce incorrect root causes in edge cases (e.g., a student who genuinely knows the answer but answers quickly). This is acceptable at MVP — student reclassification via the Vault UI provides a feedback loop and future training labels. |
| **Validation Required** | Heuristic rule audit against 50 manually reviewed AttemptAnswer samples. Confirm reclassification endpoint is implemented in Mistake Vault UI. |
| **Impact Level** | MEDIUM — Affects product intelligence quality, not functional correctness. Incorrect classifications are correctable without data loss. |

---

### DEC-008 — Performance Score Formula Lock

| Field | Detail |
|---|---|
| **Decision ID** | DEC-008 |
| **Decision** | Lock the PerformanceScore composite formula before first deployment; version it in a configuration table; never retroactively change historical scores |
| **Reasoning** | Changing the formula after deployment invalidates all historical scores. A student who sees their score drop from 72 to 58 because of a formula change — not because of performance change — loses trust in the system. Version locking means new formula versions compute forward-only; old scores are preserved under their original formula version. |
| **Alternatives Considered** | Recompute all historical scores on formula change (computationally feasible but destroys student progress narrative); Display raw accuracy only (not a differentiated metric) |
| **Risks** | Formula locked prematurely before sufficient behavioral data validates its components may produce misleading scores that persist permanently. |
| **Validation Required** | Formula review against pilot test data from 5–10 beta students before public launch. Formula documented in configuration table with version and effective_date. |
| **Impact Level** | HIGH — Historical score integrity is a permanent commitment. |

---

### DEC-009 — Monolith-First Architecture with Domain Separation

| Field | Detail |
|---|---|
| **Decision ID** | DEC-009 |
| **Decision** | Implement all 5 domains (Identity, Content, Assessment, Intelligence, Recovery) as packages within a single FastAPI application, not as separate microservices |
| **Reasoning** | Microservices introduce distributed systems complexity (inter-service authentication, network latency, service discovery, distributed tracing) that is not justified at MVP scale (100 concurrent users). A domain-separated monolith provides the same clean boundaries at a fraction of the operational overhead. When scale demands it (Phase 4), each domain package can be extracted with minimal business logic rewriting. |
| **Alternatives Considered** | Microservices from Day 1 (overwhelming operational complexity for a solo founder, likely to cause MVP delivery failure); Single flat application (no domain separation means tangled dependencies that make future extraction impossible) |
| **Risks** | Monolith extraction to microservices at Phase 4 is non-trivial even with clean domain separation. Database shared by all domains creates coupling risk at the data layer. |
| **Validation Required** | Domain boundary review: confirm no cross-domain imports exist except via defined event contracts. Verify Assessment domain does not directly query Intelligence domain tables (must use event-driven communication). |
| **Impact Level** | HIGH — Determines the entire system's evolutionary architecture. |

---

### DEC-010 — JWT Access Token in Memory + Refresh Token in httpOnly Cookie

| Field | Detail |
|---|---|
| **Decision ID** | DEC-010 |
| **Decision** | Store access token (15-minute expiry) in Zustand memory store on the frontend; store refresh token (7-day expiry) in an httpOnly Secure cookie |
| **Reasoning** | Access token in localStorage is vulnerable to XSS attacks — any injected script can extract and exfiltrate the token. Storing it in memory prevents this class of attack. Refresh token in an httpOnly cookie is not accessible to JavaScript, preventing the same XSS exfiltration for the longer-lived credential. Refresh token rotation on each use limits replay attack windows. |
| **Alternatives Considered** | Both tokens in localStorage (simple but XSS-vulnerable); Both tokens in httpOnly cookies (requires CSRF protection on all state-changing requests — adds implementation complexity); Stateful sessions (requires server-side session store, increases state complexity at MVP) |
| **Risks** | Memory-only access token is lost on page refresh — the interceptor must silently call `/auth/refresh` on 401 to restore the session. If the interceptor fails or the refresh endpoint is unavailable, the user is logged out unexpectedly. |
| **Validation Required** | Test: page refresh → confirm silent token refresh occurs within 200ms. Test: refresh token expiry → confirm redirect to login. Test: concurrent 401 responses → confirm interceptor does not trigger multiple simultaneous refresh calls. |
| **Impact Level** | HIGH — Security model for all authenticated API access. |

---

### DEC-011 — Recovery Mission Cap at 3 Active Per Student

| Field | Detail |
|---|---|
| **Decision ID** | DEC-011 |
| **Decision** | Enforce a maximum of 3 active Recovery Missions per student at any time; mission generation enforces this cap at the service layer |
| **Reasoning** | Too many active missions creates the same decision fatigue problem the product is designed to solve. Three missions is psychologically manageable and creates a natural engagement loop (complete a mission → new mission generated). The cap forces the system to prioritize the highest-impact missions rather than generating exhaustive lists. |
| **Alternatives Considered** | Unlimited missions (defeats the purpose; overwhelms students); 1 mission at a time (insufficient for multi-domain weakness cases where Physics and Biology need simultaneous recovery) |
| **Risks** | Students who dismiss missions repeatedly without completing them could exhaust the mission pool if the generation logic does not re-prioritize effectively. |
| **Validation Required** | Service layer test: trigger mission generation when 3 active missions exist; confirm oldest or lowest-priority mission is replaced, not added to. |
| **Impact Level** | MEDIUM — Affects product experience, not data integrity. |

---

### DEC-012 — Cloudflare R2 for Object Storage

| Field | Detail |
|---|---|
| **Decision ID** | DEC-012 |
| **Decision** | Use Cloudflare R2 for storing question images, bulk import files, and exported reports |
| **Reasoning** | R2 provides S3-compatible API (same boto3 SDK), zero egress fees (critical for question image serving at scale), and lower cost than AWS S3 at equivalent storage. Execution guide explicitly recommends this choice. |
| **Alternatives Considered** | AWS S3 (higher egress cost, functionally equivalent); Backblaze B2 (S3-compatible but less CDN integration than Cloudflare ecosystem); Local filesystem (not portable, fails in containerized deployment) |
| **Risks** | Vendor lock-in is minimal due to S3 API compatibility. Cloudflare R2 service disruption would make question images unavailable (questions still servable as text). |
| **Validation Required** | Signed URL generation test for question images. Confirm import file cleanup task removes temporary files after processing. |
| **Impact Level** | LOW — Object storage is isolated; failure does not affect core attempt tracking or scoring. |

---

## Layer 9 — Risk Analysis

---

### Technical Risks

| Risk ID | Description | Probability | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| TECH-001 | F026 implementation bug causes partial or silent loss of AttemptAnswer rows, corrupting all downstream intelligence for affected students | Medium | Critical | Extensive integration tests for every attempt lifecycle edge case. Duplicate submission protection. Redis backup of active state. Database transaction wrapping all 180 stub insertions. | Backend Lead | Missing rows in `attempt_answers` for a completed attempt |
| TECH-002 | `attempt_answers` table unindexed or missing composite indexes causes analytics queries exceeding 10 seconds, making dashboard unusable | High | High | All 7 critical indexes defined in schema from Day 1 (not added post-launch). Query plan review before launch. | Database Owner | P95 dashboard load > 2000ms |
| TECH-003 | ScoringService race condition on simultaneous duplicate submission from the same student (browser double-click or network retry) creates two Attempt records or double-credits a score | Low | High | Idempotency key on attempt submission. Database unique constraint on `(user_id, test_id, status=submitted)`. Return existing attempt on duplicate POST. | Backend Lead | Duplicate Attempt row for same user+test |
| TECH-004 | Celery worker crashes mid-analytics computation leaving PerformanceSnapshot in partial state, causing dashboard to show stale or missing data | Medium | Medium | Celery retry policy: 3 retries, exponential backoff (30s, 90s, 270s). Tasks designed to be idempotent — re-running on same attempt_id produces identical results. Dead-letter queue for monitoring. | DevOps | Dashboard shows no data 5 minutes after test submission |
| TECH-005 | Redis failure during an active test session causes loss of in-progress answers that have not yet been flushed to PostgreSQL | Low | High | Client-side localStorage backup every 30 seconds as tertiary buffer. Attempt recovery endpoint `GET /attempts/:id` reads from PostgreSQL if Redis key is absent. | Backend Lead | Student reports answers lost after Redis restart |
| TECH-006 | Timer Engine drift: client-side timer diverges from server `started_at` timestamp by more than 60 seconds due to tab suspension, device sleep, or system clock skew | Medium | Medium | Server-authoritative timer: submission validates elapsed time = `submitted_at - started_at`. If client timer is ahead by > 60 seconds, reject submission and return time-expired response. | Frontend Lead | Student submission with elapsed > duration + 60s tolerance |
| TECH-007 | Alembic migration applied to staging but not production creates schema divergence, causing API errors after deployment | Medium | High | CI/CD pipeline applies migrations as a required step before service restart. Rollback procedure documented per migration. Production migration requires manual confirmation checkpoint. | DevOps | 500 errors on column-dependent API endpoints after deploy |
| TECH-008 | Question import pipeline fails silently on non-UTF-8 encoded CSV files (common Excel export artifact), dropping rows without notifying the admin | Medium | Medium | Import task enforces UTF-8 detection with fallback to latin-1; encoding errors reported per row in import error report. File encoding validation step added before processing. | Backend Lead | Admin reports fewer questions imported than file contains |

---

**MVP Launch Blockers (Technical):** TECH-001, TECH-002, TECH-003, TECH-007

---

### Product Risks

| Risk ID | Description | Probability | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| PROD-001 | Mission generation cold start: students who have completed fewer than 3 tests receive low-confidence or irrelevant missions because insufficient behavioral data exists | High | Medium | Service layer produces 1 high-confidence mission (not 3) for students with fewer than 3 attempts. Mission confidence score rendered in UI. Threshold is configurable in service layer. | Product | Mission marked as "not useful" by majority of new users |
| PROD-002 | Performance Score is locked at a formula that proves misleading after beta feedback (e.g., over-weights accuracy, under-weights improvement velocity) | Medium | High | Formula is versioned in configuration table. Beta test with 10 real students before public launch to validate score feels meaningful. Forward-only formula versioning prevents retroactive score corruption. | Product | Beta students report score doesn't reflect their perceived progress |
| PROD-003 | Weakness Heatmap accuracy threshold (e.g., < 50% = weak) is set too high or too low, producing too many or too few flagged topics, diluting actionability | Medium | Medium | Threshold configurable in configuration table (not hardcoded). Beta calibration using real attempt data. Default to 60% accuracy threshold; adjust per post-launch data. | Product | Students report heatmap shows topics they feel confident in, or misses obvious weaknesses |
| PROD-004 | Root cause classification in Mistake Vault is wrong often enough that students distrust the classification, reducing engagement with Recovery Missions | High | Medium | Student reclassification option in Mistake Vault UI (Dismiss / Reclassify). Classification rationale shown ("answered in under 20s" = guessing signal). Reclassification events logged as future ML training data. | Product | High dismissal rate on Mistake Vault classifications |
| PROD-005 | Question bank content is insufficient at launch (fewer than 2,000 questions across all subjects) causing Full NEET Mocks to recycle questions between attempts, undermining test validity | High | High | Admin bulk import pipeline operational by Day 5. Content team target: 5,000+ questions before first beta student invite. PYQ set (1,500+ questions) loaded as first import batch. | Product / Content | Student takes second mock and sees repeated questions |

---

**MVP Launch Blockers (Product):** PROD-005

---

### Data Risks

| Risk ID | Description | Probability | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| DATA-001 | `attempt_answers` table inadvertently modified or deleted by a service layer bug, permanently destroying a student's behavioral history | Low | Critical | Table is treated as financial-grade data. No DELETE operations permitted (soft-delete only via status flags). Service layer has no `delete_attempt_answer` method. Database user permissions revoke DELETE on this table. | DBA | Row count in attempt_answers decreases unexpectedly |
| DATA-002 | PerformanceSnapshot formula change invalidates historical scores retroactively, causing student scores to shift without corresponding performance changes | Medium | High | Formula versioning in `score_formula_versions` configuration table. Historical snapshots store `formula_version` column. New formula version applies only to new computations. | DBA / Product | Student score changes between sessions without taking a new test |
| DATA-003 | Duplicate WeaknessSignal records created for the same user+topic combination (Celery task retry after partial success), inflating severity scores | Medium | Medium | UNIQUE constraint on `(user_id, topic_id)` in `weakness_signals`. HeatmapService uses UPSERT not INSERT. Task idempotency test before launch. | Backend Lead | WeaknessSignal count per user exceeds expected topic count |
| DATA-004 | Daily backup not configured before launch; production data loss on server failure leaves no recovery point | Medium | Critical | Daily automated PostgreSQL pg_dump to Cloudflare R2 configured before Day 1 of production. Backup restoration drill performed before MVP launch. Alert if backup job fails. | DevOps | Backup file absent from R2 bucket after scheduled time |
| DATA-005 | Question images stored in Cloudflare R2 orphaned after question deletion (or archival), accumulating storage cost without reference | Low | Low | `PATCH /questions/:id` archive endpoint triggers R2 image cleanup as an async task. Import pipeline logs image upload paths in question record for cleanup tracking. | Backend Lead | R2 storage grows faster than active question count |

---

**MVP Launch Blockers (Data):** DATA-001, DATA-004

---

### Security Risks

| Risk ID | Description | Probability | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| SEC-001 | JWT access token exfiltration via XSS if any component stores it outside Zustand memory (e.g., accidentally passed to a log or rendered in HTML) | Low | High | Access token stored in Zustand memory exclusively. Code review checklist includes: no token in localStorage, no token in Redux DevTools, no token in console.log. Security test: XSS injection attempt confirms no token extraction. | Frontend Lead | Token found in localStorage or accessible JS variable |
| SEC-002 | Brute-force attack on student login credentials succeeds because rate limiting is misconfigured or bypassed via IP spoofing | Medium | High | Rate limiting: 10 login attempts per IP per minute. Account lockout after 5 consecutive failed attempts (15-minute lockout). Login failure events logged to audit table. | Backend Lead | Audit log shows >50 failed login events for a single user within 1 hour |
| SEC-003 | Student accesses another student's attempt data by guessing or enumerating attempt UUIDs | Low | High | All attempt endpoints validate `attempt.user_id == authenticated_user_id` before returning data. 403 returned on mismatch. UUIDs are non-sequential (gen_random_uuid()), making enumeration infeasible. | Backend Lead | API access log shows attempt_id from user different from token subject |
| SEC-004 | Admin bulk import endpoint used to inject malicious content into the question bank (HTML injection, XSS payloads in question text) | Low | Medium | Question text is sanitized (strip HTML tags) at import time and before rendering in test UI. React's default HTML escaping mitigates rendering XSS. Content Security Policy header prevents script execution from question content. | Backend Lead | Question text renders as executable script in test UI |
| SEC-005 | Argon2id password hashing parameters (memory, iterations) set too low, reducing resistance to offline brute-force attacks on a database breach | Low | High | Use Argon2id with OWASP-recommended parameters: memory=64MB, iterations=3, parallelism=4. Parameters stored in configuration (not hardcoded) for future elevation. | Backend Lead | Benchmark: password hashing takes < 50ms under load (too fast = weak parameters) |

---

**MVP Launch Blockers (Security):** SEC-002, SEC-003

---

### Scalability Risks

| Risk ID | Description | Probability | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| SCALE-001 | `attempt_answers` table reaches 50M rows without partitioning, causing analytics query degradation below 10-second response times | Low (MVP), High (Growth) | High | Partition strategy documented and scheduled for implementation at 10M rows. Annual partitions: `attempt_answers_2025`, `attempt_answers_2026`. Migration plan prepared before threshold is reached. | DBA | Analytics query P95 > 3000ms |
| SCALE-002 | Redis becomes a single point of failure under concurrent test session load; Redis OOM causes active test state loss for all concurrent students | Low | High | Redis `maxmemory-policy = allkeys-lru` prevents OOM. Memory sizing: 512MB minimum, sized for (max_concurrent_tests × 180 questions × ~500 bytes per answer) + dashboard cache + session store. | DevOps | Redis memory usage > 80% of allocated |
| SCALE-003 | Analytics computation Celery queue depth grows unbounded under exam-period submission spikes (100+ simultaneous submits), causing 10+ minute dashboard delays | Medium | Medium | Celery autoscaling: add workers when queue depth > 50 tasks. Queue depth alert at 100 tasks. For exam periods, pre-scale workers to 5 before expected spike. | DevOps | Celery queue depth > 50 tasks for > 5 minutes |

---

**MVP Launch Blockers (Scalability):** None at MVP scale (100 concurrent users). SCALE-002 requires pre-launch Redis memory sizing.

---

### Operational Risks

| Risk ID | Description | Probability | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| OPS-001 | Solo founder deployment with no on-call rotation means production incidents during nights or weekends go undetected for hours | High | Medium | Sentry error alerts via email/SMS for critical errors. Uptime monitoring (UptimeRobot or Betterstack) with SMS alert if /health endpoint fails. Runbook for common failure modes documented before launch. | Founder | Zero alert response for > 30 minutes during an incident |
| OPS-002 | Database migration failure during production deploy causes API downtime if migration is partially applied | Medium | High | Migrations tested on staging DB with identical schema before production apply. Alembic `--sql` flag used to preview DDL before execution. Rollback migration prepared for every forward migration. | DevOps | API returns 500 errors on columns added by failed migration |
| OPS-003 | Celery worker becomes a zombie (process running, not processing tasks) silently draining server resources without completing analytics | Medium | Medium | Celery task timeout configured (maximum 300 seconds per task). Celery Flower monitoring dashboard deployed for task queue visibility. Dead worker detection via heartbeat + supervisor restart. | DevOps | Tasks in Celery queue for > 10 minutes without being consumed |

---

**MVP Launch Blockers (Operational):** OPS-002

---

### Integration Risks

| Risk ID | Description | Probability | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| INT-001 | AttemptCompletedEvent fails to reach Celery broker (Redis connection drop at submission time), silently skipping all analytics computation for that attempt | Low | High | Submission API wraps Celery dispatch in try-catch; if dispatch fails, attempt_id is logged to a `failed_dispatches` table for manual or scheduled retry. | Backend Lead | Completed attempt with no PerformanceSnapshot after 5 minutes |
| INT-002 | Frontend TanStack Query cache shows stale dashboard data after test submission because cache invalidation does not fire correctly after async analytics complete | High | Medium | Dashboard polling: after submission, frontend polls GET /dashboard every 10 seconds until `analytics_status = complete` (or timeout at 120 seconds). Cache invalidated on polling success. | Frontend Lead | Student sees "computing..." state that never resolves |
| INT-003 | Cross-domain event (WeaknessDetectedEvent → RecoveryService) fails silently, leaving RecoveryMissions ungenerated after a test with clear weakness signals | Medium | Medium | Event dispatch chain is tested end-to-end in integration tests: AttemptCompleted → AnalyticsComputed → WeaknessDetected → MissionGenerated. Each step logs a trace event to the audit log for observability. | Backend Lead | Test completed with clear weakness signals but zero new missions generated |

---

**MVP Launch Blockers (Integration):** INT-002 (polling resolution must be implemented before launch)

---

## Layer 9.5 — Change Impact Analysis

> For each major domain, this section identifies the blast radius of a change to that domain — affected modules, files, APIs, tables, and rollback strategy.

---

### Identity Domain Change

**Example change:** Modify JWT payload structure (add `role` field as array instead of string)

| Dimension | Details |
|---|---|
| **Affected Modules** | Identity (AuthService, JWTService), Assessment (AttemptService reads user role), Content (QuestionService checks Teacher role), Intelligence (DashboardService checks Student role), Recovery (RecoveryService checks Student role), All RBAC middleware |
| **Affected Files** | `domains/identity/services/jwt_service.py`, `domains/identity/middleware/rbac_middleware.py`, all router files using `get_current_user()` dependency, frontend `useAuthStore.ts` |
| **Affected APIs** | POST /auth/login (response shape changes), POST /auth/refresh (response shape changes), GET /auth/me (response shape changes), every protected endpoint (middleware behavior changes) |
| **Affected Database Tables** | `users`, `roles`, `user_roles` (no schema change, but JWT payload regeneration required) |
| **Potential Regressions** | Any endpoint using `current_user.role` as a string breaks silently if it expects a string but receives an array. RBAC permission checks using `role == "student"` break if changed to `"student" in roles`. |
| **Rollback Strategy** | Deploy with parallel support: accept both string and array role payloads for 1 deployment cycle. Force re-login for all users to regenerate tokens. Hard cutover on next deploy. |
| **Impact Level** | HIGH |

---

### Taxonomy (Content) Domain Change

**Example change:** Add a fourth taxonomy level (Sub-topic below Topic)**

| Dimension | Details |
|---|---|
| **Affected Modules** | Content (TaxonomyService, QuestionService), Assessment (test generation queries filter by topic_id), Intelligence (topic_analytics table, HeatmapService), Recovery (MistakeService, MissionTasks reference topic_id) |
| **Affected Files** | `domains/content/models/topic.py`, `domains/content/services/taxonomy_service.py`, `domains/intelligence/services/heatmap_service.py`, `domains/recovery/services/mission_service.py`, all Alembic migrations for schema changes |
| **Affected APIs** | GET /chapters/:id/topics (response shape changes), GET /dashboard/heatmap (granularity changes), GET /recommendations (new granularity level), question CRUD endpoints (new optional field) |
| **Affected Database Tables** | `topics` (add parent reference or create `subtopics` table), `topic_analytics` (new aggregation level required), `weakness_signals` (granularity changes), `mission_tasks` (topic_id semantics change), `attempt_answers` (no schema change, but analysis queries change) |
| **Potential Regressions** | HeatmapService queries referencing `topics.id` must be updated to handle the new level. Existing `weakness_signals` records at topic level become ambiguous if sub-topics are introduced. |
| **Rollback Strategy** | Schema migration must be backward-compatible (add nullable column, not replace). Feature flag new taxonomy level. Roll forward: do not delete topics table. |
| **Impact Level** | HIGH |

---

### Content Domain Change

**Example change:** Change question status workflow (add "Pending Review" state between Draft and Review)

| Dimension | Details |
|---|---|
| **Affected Modules** | Content (QuestionService, ImportService), Assessment (test generation only queries Published questions) |
| **Affected Files** | `domains/content/models/question.py`, `domains/content/services/question_service.py`, `domains/content/routers/questions.py`, import validation logic, frontend question management UI |
| **Affected APIs** | GET /questions (filter by status), POST /questions (default status changes), PATCH /questions/:id (valid status transitions change) |
| **Affected Database Tables** | `questions` (status enum change — ALTER TYPE required in PostgreSQL), question status audit events |
| **Potential Regressions** | Existing `status = 'draft'` questions may need migration to 'pending_review'. Import pipeline default status must be updated. State machine validation in QuestionService must include new valid transitions. |
| **Rollback Strategy** | Add new status value to enum (non-breaking). Roll back by deprecating the new value (do not remove — PostgreSQL enum removal requires full migration). |
| **Impact Level** | MEDIUM |

---

### Assessment Domain Change

**Example change:** Change AttemptAnswer batch size from 10 events to 25 events per PATCH call

| Dimension | Details |
|---|---|
| **Affected Modules** | Assessment (AttemptService), Frontend (test session Zustand store, debounce/batch logic) |
| **Affected Files** | `domains/assessment/services/attempt_service.py`, `domains/assessment/routers/attempts.py`, `domains/assessment/schemas/attempt_schemas.py`, frontend `useTestSession.ts`, Pydantic input validator for batch size |
| **Affected APIs** | PATCH /attempts/:id/answers (request body schema change — max array length) |
| **Affected Database Tables** | None (no schema change) |
| **Potential Regressions** | Frontend sending batches of 25 to an API still limiting to 10 causes validation errors. Must update both API validator and frontend batch builder in the same deploy. |
| **Rollback Strategy** | Deploy API change first (accept both sizes), then deploy frontend. Revert frontend batch size if API causes issues. |
| **Impact Level** | LOW |

---

### Intelligence Domain Change

**Example change:** Change PerformanceScore formula to add "negative mark ratio" as a fifth composite dimension

| Dimension | Details |
|---|---|
| **Affected Modules** | Intelligence (ScoreService), Recovery (mission priority ranking references performance score), Frontend (dashboard rendering) |
| **Affected Files** | `domains/intelligence/services/score_service.py`, `domains/intelligence/workers/analytics_task.py`, `score_formula_versions` configuration table, `performance_snapshots` table (formula_version column must be used correctly) |
| **Affected APIs** | GET /dashboard/score (score history rendering may shift), GET /dashboard (current score changes) |
| **Affected Database Tables** | `performance_snapshots` (historical scores unchanged; new formula_version assigned to new records only), `score_formula_versions` (new row inserted) |
| **Potential Regressions** | Students who monitor score trends will see a discontinuity in their score history between old and new formula versions. Must communicate formula update in UI. |
| **Rollback Strategy** | New formula version is forward-only. Historical scores immutable. Roll back by deprecating new formula version — revert ScoreService to previous formula_version on new computations. Old historical scores unaffected. |
| **Impact Level** | HIGH |

---

### Recovery Domain Change

**Example change:** Increase maximum active Recovery Missions from 3 to 5

| Dimension | Details |
|---|---|
| **Affected Modules** | Recovery (RecoveryService mission cap enforcement), Frontend (mission list UI, display capacity) |
| **Affected Files** | `domains/recovery/services/recovery_service.py`, `domains/recovery/constants.py` (cap constant), frontend MissionList component |
| **Affected APIs** | POST /missions (cap enforcement), GET /missions (returns up to 5 now) |
| **Affected Database Tables** | `recovery_missions` (no schema change; service logic change only) |
| **Potential Regressions** | Frontend mission list UI designed for 3 missions may not gracefully render 5. Decision fatigue product concern: more active missions may reduce completion rates. |
| **Rollback Strategy** | Revert constant in `recovery_service.py`. Existing missions with count > 3 are not deleted — they become valid under the new cap. Reverting cap does not delete excess missions. |
| **Impact Level** | LOW |

---

### Frontend Change

**Example change:** Migrate from Zustand to Redux Toolkit for state management

| Dimension | Details |
|---|---|
| **Affected Modules** | Frontend only (all components using Zustand hooks) |
| **Affected Files** | All files importing `useTestStore`, `useAuthStore`, `useUIStore`. All `*.store.ts` files. All test files mocking Zustand stores. |
| **Affected APIs** | No API changes — state management is frontend-internal |
| **Affected Database Tables** | None |
| **Potential Regressions** | Test session state management is the highest-risk area: active test timer, current question index, answer draft state, and review flags must all migrate without behavioral change. Regression risk: timer state mismatch causes premature or delayed auto-submit. |
| **Rollback Strategy** | Maintain Zustand in parallel alongside Redux during migration. Feature flag which store is active. Revert by removing Redux and restoring Zustand imports. |
| **Impact Level** | MEDIUM |

---

## Layer 10 — Requirement Coverage Validation

> Every functional and non-functional requirement from the blueprint is verified against the 25 MVP features, matched to a module and test plan.

---

### Requirement Coverage Matrix

| Req ID | Requirement | Feature ID | Module | Test Coverage | Status |
|---|---|---|---|---|---|
| REQ-001 | Students register with email, password, name, grade, target year | F001 | Identity | Integration: POST /auth/register — valid, duplicate email, missing fields | ✅ COVERED |
| REQ-002 | Duplicate email registration returns 409 | F001 | Identity | Integration: duplicate registration test | ✅ COVERED |
| REQ-003 | Email verification required before test access | F001 | Identity | Integration: attempt test with unverified account → 403 | ✅ COVERED |
| REQ-004 | Login returns JWT access token (15 min) + httpOnly refresh token (7 days) | F002 | Identity | Integration: login response headers + cookie assertions | ✅ COVERED |
| REQ-005 | Refresh token rotation: each use invalidates old token | F002 | Identity | Integration: use refresh token twice, confirm second use fails | ✅ COVERED |
| REQ-006 | Profile stores target score, target year, notification preferences | F003 | Identity | Integration: PATCH /profile with all fields | ✅ COVERED |
| REQ-007 | RBAC: Students cannot access Teacher or Admin APIs | F005 | Identity | Integration: Student token → Teacher-protected endpoint → 403 | ✅ COVERED |
| REQ-008 | RBAC: Teachers cannot access Admin APIs | F005 | Identity | Integration: Teacher token → Admin-protected endpoint → 403 | ✅ COVERED |
| REQ-009 | All authentication events logged to immutable audit table | F001, F002 | Identity | Integration: audit table row count after register + login | ✅ COVERED |
| REQ-010 | Questions created with text, 4 options, correct answer, explanation, subject, chapter, topic, difficulty | F006 | Content | Integration: POST /questions with all required fields | ✅ COVERED |
| REQ-011 | Questions progress through Draft → Review → Approved → Published → Archived | F006 | Content | Unit: QuestionService state machine transitions | ✅ COVERED |
| REQ-012 | Only Published questions served in tests | F006, F016 | Content, Assessment | Integration: test generation excludes non-Published questions | ✅ COVERED |
| REQ-013 | Bulk import via CSV/XLSX/JSON; per-row validation; partial success | F007 | Content | Integration: import file with valid and invalid rows; confirm valid committed, errors reported | ✅ COVERED |
| REQ-014 | PYQ questions carry exam year, exam code, historical frequency metadata | F008 | Content | Integration: PYQ import and retrieval with metadata fields | ✅ COVERED |
| REQ-015 | Question search filters by subject, chapter, topic, difficulty, PYQ flag, tags | F014 | Content | Integration: search with each filter combination | ✅ COVERED |
| REQ-016 | Subject → Chapter → Topic taxonomy hierarchy enforced | F010, F011, F012 | Content | Integration: create topic without chapter → 400; delete chapter with topics → 409 | ✅ COVERED |
| REQ-017 | Full NEET Mock: 180 questions, Physics(45)+Chemistry(45)+Biology(90), 180-minute timer | F016 | Assessment | Integration: mock creation, section composition, question count validation | ✅ COVERED |
| REQ-018 | Unit Test: configurable chapter, topic, question count | F017 | Assessment | Integration: create unit test with configuration; verify question selection | ✅ COVERED |
| REQ-019 | Mixed Revision Test: multi-chapter, randomized selection | F018 | Assessment | Integration: mixed test composition, randomization verification | ✅ COVERED |
| REQ-020 | Timer tracks: test start time, per-question first-touch, per-question time_spent, total elapsed | F023 | Assessment | Integration: complete attempt, verify attempt_answers.time_spent values | ✅ COVERED |
| REQ-021 | OMR Simulation tracks: answer selection, answer changes with timestamp, review flag events | F024 | Assessment | Integration: change answer, verify answer_changed=true; mark review, verify marked_review=true | ✅ COVERED |
| REQ-022 | Scoring: +4 correct, -1 incorrect, 0 unanswered | F025 | Assessment | Unit: ScoringService with all answer combinations | ✅ COVERED |
| REQ-023 | Attempt submission is idempotent | F026 | Assessment | Integration: submit same attempt twice, confirm identical response, no duplicate records | ✅ COVERED |
| REQ-024 | Active test state persisted to Redis every 30 seconds for crash recovery | F026 | Assessment | Integration: simulate Redis TTL expiry mid-test, confirm recovery from PostgreSQL | ✅ COVERED |
| REQ-025 | One active attempt per test per user at any time | F026 | Assessment | Integration: start second attempt on same test → return existing attempt | ✅ COVERED |
| REQ-026 | Performance Dashboard renders within 1 second after test submission (cached) | F027 | Intelligence | Performance: GET /dashboard with warm cache → P95 < 1000ms | ✅ COVERED |
| REQ-027 | Weakness Heatmap shows subject → chapter → topic severity from accuracy rates | F028 | Intelligence | Integration: complete test with targeted wrong answers, verify heatmap severity matches | ✅ COVERED |
| REQ-028 | Performance Score composite: accuracy rate, consistency, topic breadth, improvement delta, negative mark ratio | F031 | Intelligence | Unit: ScoreService with all five input dimensions | ✅ COVERED |
| REQ-029 | Performance Score formula versioned; historical scores immutable | F031 | Intelligence | Integration: formula version change does not alter existing PerformanceSnapshot records | ✅ COVERED |
| REQ-030 | Mistake Vault captures every wrong answer with root cause: Conceptual, Application, Calculation, Interpretation, Memory, Timing, Confidence, Guessing | F044 | Recovery | Integration: wrong answers with distinct behavioral signals produce distinct root cause classifications | ✅ COVERED |
| REQ-031 | Mistake Vault tracks recurrence: same question wrong again increments recurrence_count | F044 | Recovery | Integration: same question wrong in two separate attempts, verify recurrence_count=2 | ✅ COVERED |
| REQ-032 | Recovery Missions generated from Weakness Heatmap + Mistake Vault + Performance Score | F045 | Recovery | Integration: complete test with weaknesses, verify missions generated within 60 seconds | ✅ COVERED |
| REQ-033 | Maximum 3 active missions per student; priority-ranked by expected score impact | F045 | Recovery | Integration: generate missions exceeding 3, confirm cap enforced with priority ranking | ✅ COVERED |
| REQ-034 | Weak Topic Recommendations list topics with accuracy below threshold, ranked by mark leakage | F047 | Recovery | Integration: recommendations match lowest-accuracy topics from heatmap | ✅ COVERED |
| REQ-035 | API response time P95 < 300ms | All | All | Load test: 50 concurrent users, all API endpoint categories | ✅ COVERED |
| REQ-036 | Dashboard load time < 1000ms | F027 | Intelligence | Performance: dashboard endpoint under cache and no-cache conditions | ✅ COVERED |
| REQ-037 | Test screen answer save latency < 100ms | F026 | Assessment | Performance: PATCH /attempts/:id/answers under load | ✅ COVERED |
| REQ-038 | Concurrent users: 100 at MVP | All | Infrastructure | Load test: 100 concurrent users taking tests simultaneously | ✅ COVERED |
| REQ-039 | Data durability: daily backups | All | Infrastructure | Operational: backup job configuration and restoration drill | ✅ COVERED |
| REQ-040 | Uptime: 99.5% MVP | All | Infrastructure | Monitoring: uptime check configuration + alert verification | ✅ COVERED |
| REQ-041 | Question approval workflow: questions not served until Published | F006 | Content | Integration: draft question not returned by test generation endpoint | ✅ COVERED |
| REQ-042 | Audit trail: all auth events and question state changes immutable | F001, F002, F005, F006 | Identity, Content | Integration: audit table has no UPDATE or DELETE; append-only inserts only | ✅ COVERED |
| REQ-043 | Import pipeline: 1,000 question limit per batch at MVP | F007 | Content | Integration: import file with 1,001 rows → 400 with batch size exceeded error | ✅ COVERED |
| REQ-044 | Privacy consent and data deletion support | F001 | Identity | Integration: account deletion removes PII; analytics records anonymized | ✅ COVERED |
| REQ-045 | Rate limiting: 10 login attempts per IP per minute; 3 imports per user per hour | F002, F007 | Identity, Content | Integration: rate limit trigger on login (11th attempt); import rate limit (4th in 1 hour) | ✅ COVERED |

---

### Coverage Calculation

| Metric | Value |
|---|---|
| **Requirements Found** | 45 |
| **Requirements Covered** | 45 |
| **Coverage %** | **100%** |

---

### Missing Requirements

**None identified.** All 45 functional and non-functional requirements derived from the blueprint have corresponding feature assignments, module ownership, and test plan coverage.

---

### Orphan Prompts

**None identified.** All implementation prompts generated in Batch 4 map to at least one requirement in the coverage matrix above.

---

### Scope Drift Indicators

The following items were explicitly excluded from MVP scope. Any implementation touching these constitutes scope drift and must be deferred:

| Deferred Feature | Category | Reason |
|---|---|---|
| F004 Session Management Dashboard | Identity | JWT handles session at MVP; device tracking is post-MVP |
| F013 Difficulty Classification | Content | Simple enum used at MVP; AI-calibrated difficulty deferred |
| F015 Question Validation Engine | Content | Manual review at MVP; automated validation deferred |
| F019–F022 (Adaptive/AI Tests) | Assessment | Requires behavioral data maturity not available at launch |
| F029, F030, F032–F035 (Advanced Analytics) | Intelligence | Require multiple tests and historical data |
| F036–F043 (Psychology Engine) | Psychology | Requires 100+ test events per student |
| F046 Daily Recovery Plan | Recovery | Requires habit data not available at launch |
| F048–F050 (Advanced Recovery) | Recovery | Requires data maturity |
| F051–F064 (Identity/Prediction Layer) | Intelligence | Data-hungry; Brain Twin, Learning DNA, Score Simulator |
| F065–F072 (Habit/Engagement Layer) | Engagement | Daily Performance Score, Brain CEO, Zero Decision Mode |
| F076–F078 (Teacher Analytics) | Analytics | Post-MVP once student usage establishes patterns |
| WAF / MFA / SSO | Security | Post-MVP security hardening |
| ClickHouse / BigQuery analytics | Infrastructure | Required at 10,000+ daily users |
| Kafka / Kinesis event streaming | Infrastructure | Phase 4 microservice extraction |

---

## Dependency Graph Summary

---

### Critical Path

The single most critical dependency chain in the entire MVP is:

```
F001 (Registration)
    → F002 (Login)
        → F005 (RBAC)
            → F010 (Subject) → F011 (Chapter) → F012 (Topic)
                → F006 (Question Bank)
                    → F009 (Tagging)
                        → F023 (Timer Engine) → F016 (Full NEET Mock)
                            → F026 (Attempt Tracking)  ← CONVERGENCE POINT
                                → F028 (Weakness Heatmap)
                                    → F027 (Performance Dashboard)
                                        → F044 (Mistake Vault)
                                            → F047 (Weak Topic Recs)
                                                → F045 (Recovery Missions)
```

**The single most critical dependency chain:** `F006 → F026 → F028 → F044 → F045`

Question Bank feeds Attempt Tracking. Attempt Tracking feeds Weakness Heatmap. Weakness Heatmap feeds Mistake Vault. Mistake Vault feeds Recovery Missions. Breaking any single link in this chain collapses every intelligence and recovery feature simultaneously.

---

### Parallel Work Streams

The following features can be implemented simultaneously without blocking each other:

**Stream A (Authentication + Identity):** F001, F002, F003, F005  
**Stream B (Taxonomy):** F010, F011, F012 (no auth dependency until RBAC middleware is applied)  
**Stream C (Infrastructure):** Redis setup, Celery setup, CI/CD pipeline, object storage configuration

These three streams can run in parallel through Day 3 of Week 1 before they must converge at F006.

Within Week 2, the following can be partially parallelized:  
**Stream D:** F017 (Unit Tests) and F018 (Mixed Tests) — both built on the same TestEngine scaffolding as F016. Once F016 is complete, F017 and F018 are incremental additions.

---

### Sequential Work Streams

The following features are strictly sequential and cannot be started until their predecessor is complete:

| Sequence | Reason |
|---|---|
| F010 → F011 → F012 → F006 | Taxonomy hierarchy must exist before questions can be created |
| F006 → F016 | Question bank must be seeded before a test can be composed |
| F016 → F026 | Test structure must exist before attempt tracking can be implemented |
| F026 → F027 → F028 → F031 | All intelligence features read from attempt data |
| F028 + F044 → F045 | Recovery Missions require both heatmap and vault data as inputs |
| F001 → F002 → All protected features | Authentication must gate all subsequent features |

---

### High-Risk Dependencies

| Dependency | Risk | Consequence of Failure |
|---|---|---|
| F026 depends on F016 | If test engine is delayed, attempt tracking cannot be validated with real test sessions | All intelligence features pushed back by equivalent delay |
| F045 depends on F044, F028, F031, F047 simultaneously | Most complex fan-in in the system — requires all four inputs to be stable before mission generation can be implemented | Recovery Missions is the last feature built; any upstream delay pushes it past the 4-week window |
| Celery chain: AttemptCompleted → AnalyticsComputed → WeaknessDetected → MissionGenerated | Each step dispatches the next; a failure at any link silently breaks all subsequent steps | Dashboard, Heatmap, Vault, and Missions all appear to work but produce no output |
| Performance Score formula lock | Must be locked before first beta student takes a test | Changing it post-launch creates permanent historical score discontinuity |

---

### Bottlenecks

| Bottleneck | Location | Impact |
|---|---|---|
| F026 (Attempt Tracking) | Week 2, Days 9–10 | Single highest-complexity implementation task. Every day of delay here delays F027, F028, F031, F044, F045, F047 — six features — simultaneously. |
| Celery chain testing | Week 3 | End-to-end analytics pipeline testing requires a completed attempt, which requires a completed test, which requires a seeded question bank. Cannot be tested until Week 2 work is done. |
| Beta content seeding | Pre-launch | Without 5,000+ Published questions, the Full NEET Mock cannot be composed. Content loading is the non-engineering bottleneck most likely to delay launch. |
| Performance Score formula decision | Week 3, Day 11 | Formula must be decided and coded before analytics_computation_task can be completed. Indecision here blocks the entire Intelligence layer. |

---

## Final Completion Checklist

---

### Architecture Checklist

- [ ] Domain boundary diagram finalized and committed to `/docs/ARCHITECTURE.md`
- [ ] Five bounded contexts confirmed: Identity, Content, Assessment, Intelligence, Recovery
- [ ] No cross-domain imports exist outside of defined event contracts (audit this via dependency linting)
- [ ] Domain event contracts documented: AttemptCompletedEvent, WeaknessDetectedEvent, QuestionResolvedEvent
- [ ] Monolith package structure matches `/backend/app/domains/{domain}/` layout
- [ ] Shared services (AuditService, NotificationService, StorageService) placed in `/backend/app/shared/`
- [ ] Architecture diagram added to README.md
- [ ] FastAPI application factory pattern implemented (`create_app()` in `main.py`)
- [ ] Domain routers registered in application factory, not hardcoded in `main.py`
- [ ] CORS policy configured to allow only the deployed frontend domain

---

### Database Checklist

- [ ] All 20+ tables created via Alembic migrations (not raw SQL)
- [ ] All 7 critical indexes created: `users(email)`, `attempts(user_id, status)`, `attempt_answers(attempt_id)`, `attempt_answers(question_id)`, `mistakes(user_id, root_cause)`, `weakness_signals(user_id, topic_id)`, `questions(subject_id, chapter_id, status)`
- [ ] Unique constraints verified: `users(email)`, `weakness_signals(user_id, topic_id)`, `user_roles(user_id, role_id)`, `chapters(subject_id, name)`, `topics(chapter_id, name)`
- [ ] `attempt_answers` table confirmed as append/update only — no DELETE method exists in repository layer
- [ ] `score_formula_versions` configuration table created with `formula_version`, `components`, and `effective_date` columns
- [ ] `performance_snapshots` contains `formula_version` column referencing configuration table
- [ ] Alembic migration naming convention documented (`{number}_{description}.py`)
- [ ] Migration tested on clean database (not just from existing schema)
- [ ] Daily backup job configured to dump PostgreSQL to Cloudflare R2
- [ ] Backup restoration drill completed before launch
- [ ] Database user permissions reviewed: application user has SELECT/INSERT/UPDATE; no DELETE on `attempt_answers`; no DROP on any table
- [ ] `attempt_answers` partitioning strategy documented for 10M-row threshold (even if not yet implemented)

---

### Backend Checklist

- [ ] AuthService: register, verify_email, login, logout, refresh — all implemented and tested
- [ ] JWTService: issue access token (15-minute expiry), validate, refresh — Argon2id password hashing confirmed
- [ ] RBACMiddleware: permission check on every protected route — 403 on insufficient permission
- [ ] AuditService: append-only event log for all auth events and question state changes
- [ ] TaxonomyService: subjects seeded (Physics, Chemistry, Biology); chapter and topic CRUD
- [ ] QuestionService: CRUD with state machine (Draft → Published → Archived); only Published returned to tests
- [ ] ImportService: CSV/XLSX/JSON parser; per-row validation; Celery async task; polling endpoint; 1,000-row cap; encoding detection
- [ ] TestEngineService: Full Mock (180q), Unit Test (configurable), Mixed Revision (multi-chapter randomized)
- [ ] AttemptService: start_attempt (idempotent), save_answers (bulk upsert), submit_attempt (idempotent) — all three paths tested
- [ ] ScoringService: NEET +4/-1/0 logic with all edge cases (all correct, all incorrect, all unanswered, mixed)
- [ ] Redis caching implemented: `active_test:{attempt_id}` (3h), `test_questions:{test_id}` (1h), `user_dashboard:{user_id}` (5m), `session:{user_id}` (15m)
- [ ] Celery task chain implemented and tested: `analytics_computation_task` → `weakness_detection_task` → `mission_generation_task`
- [ ] AnalyticsService: aggregates AttemptAnswers by subject/chapter/topic; persists PerformanceSnapshot
- [ ] ScoreService: composite PerformanceScore with formula versioning
- [ ] HeatmapService: topic weakness detection against configurable threshold; UPSERT to weakness_signals
- [ ] MistakeService: root cause heuristic classification (8 categories); recurrence_count increment on repeat
- [ ] RecoveryService: mission generation from heatmap + vault + score; 3-mission cap enforced; priority ranking
- [ ] RecommendationService: weak topic list ranked by mark leakage
- [ ] All API error responses follow standard format: `{"code": "ERROR_CODE", "message": "...", "details": {}}`
- [ ] Rate limiting configured: 10/min login, 5/min register, 3/hr import, 200/min authenticated general
- [ ] `/health` endpoint returns 200 with DB + Redis connectivity status
- [ ] OpenAPI documentation auto-generated and accessible at `/docs`
- [ ] Sentry error tracking configured with environment tagging (staging vs production)

---

### Frontend Checklist

- [ ] Auth flow complete: register → email verify → login → token refresh → logout
- [ ] Access token stored in Zustand memory only (not localStorage, not sessionStorage)
- [ ] Refresh token handled via httpOnly cookie; Axios interceptor handles 401 → silent refresh
- [ ] Test session Zustand store: question list, current index, timer state, answer draft, review flags
- [ ] Timer component: countdown with per-question time tracking; auto-submit on expiry
- [ ] OMR Interface: answer selection, answer change tracking (answer_changed flag), review marking
- [ ] Answer events debounced and batched (up to 10 per PATCH call, 500ms debounce)
- [ ] localStorage backup of test state every 30 seconds (tertiary recovery)
- [ ] Test submission flow: POST /submit → receive score → polling for analytics completion → redirect to dashboard
- [ ] Performance Dashboard: performance score, improvement trend, subject accuracy breakdown, top weaknesses, recent missions
- [ ] Weakness Heatmap visualization: subject → chapter → topic with severity color coding (🔴 critical, 🟡 high, 🟢 medium)
- [ ] Mistake Vault UI: grouped by root cause, severity-ranked, reclassification option per entry
- [ ] Recovery Missions UI: active missions list, mission detail with task checklist, task completion flow
- [ ] Weak Topic Recommendations list with topic name, subject, accuracy%, recommendation rationale
- [ ] TanStack Query configured with stale-while-revalidate for dashboard data; cache invalidated on new submission
- [ ] React Router v6 route guards: unauthenticated users redirected to login; unverified users blocked from test access
- [ ] Error boundaries on Test Engine and Dashboard routes (crash does not lose test state)
- [ ] Mobile-responsive layout on all student-facing pages
- [ ] Content Security Policy header prevents script injection in question text rendering

---

### Testing Checklist

- [ ] Unit tests written for all service layer business logic (ScoringService, ScoreService, HeatmapService, MistakeClassification heuristics)
- [ ] Integration tests cover the complete attempt lifecycle: start → save answers → submit → idempotent resubmit
- [ ] Integration tests cover Celery chain: trigger AttemptCompleted → verify PerformanceSnapshot, WeaknessSignal, RecoveryMission all created within 60 seconds
- [ ] Security tests: Student token → Teacher API → 403; Student A token → Student B's attempt → 403
- [ ] Performance test: 50 concurrent test submissions (Week 4, Day 20)
- [ ] Performance test: GET /dashboard with 100k attempt_answers rows → P95 < 1000ms
- [ ] Performance test: PATCH /attempts/:id/answers → P95 < 100ms
- [ ] Edge case: import file with 1,001 rows → 400 rejection
- [ ] Edge case: duplicate submission of same attempt_id → idempotent response
- [ ] Edge case: answer update on a submitted (closed) attempt → 409 or 403
- [ ] Edge case: test session started with insufficient Published questions → meaningful error
- [ ] Edge case: Celery task retry after worker failure → task completes on retry, no duplicate records
- [ ] CI pipeline: pytest with 80% minimum coverage enforced on merge
- [ ] CI pipeline: ruff lint + mypy type check required to pass before merge
- [ ] End-to-end test of complete student journey: registration → full mock → score → dashboard → mission (Week 4, Day 20)
- [ ] Beta test with 5–10 real students before public launch (Week 4, Days 20–21)

---

### Security Checklist

- [ ] Argon2id password hashing with OWASP-recommended parameters (memory=64MB, iterations=3, parallelism=4)
- [ ] JWT access token: 15-minute expiry, HS256 or RS256 (RS256 preferred for future key rotation)
- [ ] Refresh token: 7-day expiry, stored in httpOnly Secure SameSite=Strict cookie
- [ ] Refresh token rotation: old token invalidated on each use; rotation event logged to audit table
- [ ] HTTPS enforced on all endpoints (Caddy or Nginx with TLS)
- [ ] CORS policy restricts origins to deployed frontend domain only
- [ ] All protected endpoints validate user ownership: attempt belongs to authenticated user
- [ ] Account lockout after 5 consecutive failed login attempts (15-minute lock)
- [ ] Rate limiting active on login, register, and import endpoints
- [ ] Question text sanitized (strip HTML) on import and before rendering
- [ ] Content Security Policy header configured on all frontend responses
- [ ] Admin endpoints gated by Admin role check at service layer (not just middleware)
- [ ] Database credentials stored in environment variables, not in code or committed config files
- [ ] Redis connection uses password authentication in production
- [ ] Cloudflare R2 bucket policy: private (not public-read); signed URL generation for question images
- [ ] Audit log table has no UPDATE or DELETE privileges for the application database user
- [ ] Security test: confirm XSS in question text does not execute in test UI

---

### Deployment Checklist

- [ ] Docker Compose file covers all services: `postgres`, `redis`, `api`, `worker`, `frontend`
- [ ] Environment variables documented in `.env.example` (no real secrets in repository)
- [ ] GitHub Actions CI pipeline: lint → type-check → test → migration-check → build → deploy (main branch)
- [ ] Alembic migration applied as a required pre-restart step in deployment script
- [ ] Zero-downtime deployment: 2-instance rotation (old instance stays live until new instance is healthy)
- [ ] `/health` endpoint checked by load balancer before routing traffic to new instance
- [ ] Sentry configured with staging vs production environment tags
- [ ] Structured JSON logging (structlog) configured; logs shipped to aggregation service
- [ ] Redis `maxmemory-policy` set to `allkeys-lru` with explicit memory limit
- [ ] Celery Flower dashboard deployed for task queue monitoring
- [ ] UptimeRobot or equivalent monitoring active with SMS/email alert on health check failure
- [ ] Cloudflare R2 bucket configured with lifecycle rules (delete files older than 90 days in /imports/ path)
- [ ] Staging environment functional with identical configuration to production before public launch

---

### MVP Launch Checklist

- [ ] Question bank seeded with minimum 5,000 Published questions across Physics, Chemistry, Biology
- [ ] PYQ set imported (minimum 1,500 questions with year and exam metadata)
- [ ] At least one Full NEET Mock test composed and published in the test catalog
- [ ] At least 3 Unit Tests per subject (Physics, Chemistry, Biology) composed and published
- [ ] Performance Score formula reviewed with beta data and locked in configuration table
- [ ] Weakness detection accuracy threshold set (default 60%) and documented
- [ ] Beta test completed: 5–10 real students have completed at least one full mock and received missions
- [ ] Zero critical bugs open from beta testing
- [ ] Daily backup running and restoration confirmed successful
- [ ] Student-facing error messages are human-readable (not raw stack traces)
- [ ] Privacy policy and terms of service pages published
- [ ] Account deletion workflow functional (GDPR compliance)
- [ ] Mission cold-start logic confirmed: students with < 3 attempts receive 1 high-confidence mission, not 3 low-confidence missions
- [ ] Mistake Vault reclassification option visible and functional
- [ ] Dashboard polling resolves within 60 seconds of test submission under normal conditions
- [ ] Load test passed: 50 concurrent users, all endpoints within SLA

---

## Project Memory Files

> Specifications for the 9 permanent project memory files that govern AI-assisted development continuity. These files must be initialized before the first implementation session and maintained throughout the project lifecycle.

---

### FILE 1: PROJECT_OVERVIEW.md

**Purpose:** The single-entry-point document that orients any developer or AI assistant to the product's identity, purpose, and current state in one page. Prevents context-reset problems in long AI-assisted development sessions.

**Required Sections:**

```
# NEET Performance Operating System — Project Overview

## Product Identity
- What this product is (one sentence)
- What this product is NOT (one sentence)
- The core loop (6-step diagram)
- Primary differentiation vs incumbents (1 paragraph)

## Current Phase
- Week number (1–4) and active sprint goal
- Features completed vs remaining (ratio)
- Single most important thing to build today

## MVP Feature Set Status
| ID | Feature | Status | Priority |
(25 rows, status = not_started | in_progress | complete)

## Architecture Summary
- Backend: [tech + version]
- Database: [tech + version]
- Cache/Queue: [tech + version]
- Frontend: [tech + version]
- Key design pattern: [one line]

## Critical Rules (Never Violate)
1. Do not delete rows from attempt_answers
2. Do not change PerformanceScore formula on existing records
3. Do not serve non-Published questions in tests
4. Always make attempt submission idempotent
```

**Update Rules:**
- Update `Current Phase` section at the start of every development session
- Update `MVP Feature Set Status` immediately when a feature changes status
- Do not change `Critical Rules` without a Decision Log entry
- Keep under 2 pages (this is a context-loading document, not a reference document)

**Ownership:** Project lead. Review before every development session.

---

### FILE 2: ARCHITECTURE.md

**Purpose:** Authoritative technical architecture reference. Answers: What components exist? How do they communicate? What are the domain boundaries? Where does each type of data live? Prevents architecture drift in AI-assisted sessions.

**Required Sections:**

```
# Architecture Reference

## System Diagram
[ASCII or Mermaid diagram: Client → Nginx → FastAPI → PostgreSQL + Redis]
[Background workers diagram: Celery chain]

## Domain Boundaries
Identity | Content | Assessment | Intelligence | Recovery
(For each domain: Aggregate Roots, Services, Tables Owned, Events Emitted, Events Consumed)

## Cross-Domain Event Contracts
- AttemptCompletedEvent: {attempt_id, user_id, test_id, completed_at}
- WeaknessDetectedEvent: {user_id, topic_ids, severity_scores}
- QuestionResolvedEvent: {question_id, metadata snapshot}

## Technology Decisions (Summary)
| Decision | Choice | Rationale Ref |
(Link to DECISIONS.md for each)

## Request Lifecycle
[Diagram: HTTP Request → Nginx → FastAPI Router → Middleware → Service → Repository → DB]

## Caching Architecture
| Cache Key | TTL | Contents | Invalidated By |

## Background Worker Architecture
| Task | Trigger | Inputs | Outputs | Retry Policy |
```

**Update Rules:**
- Update when a new domain event contract is added
- Update caching table when a new cache key is introduced
- Update background worker table when a new Celery task is added
- Never delete domain event contracts — mark as deprecated instead
- Diagrams must be kept in sync with actual implementation

**Ownership:** Backend lead. Updated before finalizing any new cross-domain integration.

---

### FILE 3: MODULES.md

**Purpose:** Per-domain implementation status and service layer reference. Answers: What services exist in each domain? What is each service's responsibility? What is implemented and what is pending?

**Required Sections:**

```
# Module Reference

## Identity Domain
Services: AuthService | JWTService | RBACService | AuditService
For each service:
  - Methods (implemented / pending)
  - Key business rules enforced
  - Tables written to
  - Events emitted

## Content Domain
Services: QuestionService | TaxonomyService | ImportService
(same structure)

## Assessment Domain
Services: TestEngineService | AttemptService | ScoringService
(same structure)

## Intelligence Domain
Services: AnalyticsService | ScoreService | HeatmapService | DashboardService
(same structure)

## Recovery Domain
Services: MistakeService | RecoveryService | RecommendationService
(same structure)

## Shared Services
AuditService | NotificationService | StorageService
```

**Update Rules:**
- Add a method entry immediately when a new service method is implemented
- Mark methods `[PENDING]` if they are designed but not yet coded
- Include one-line description of each method's responsibility
- Do not include implementation code — this is a reference document, not source code

**Ownership:** Backend lead. Updated after each feature implementation session.

---

### FILE 4: DEPENDENCIES.md

**Purpose:** Tracks the complete dependency graph for all 25 MVP features and all external package dependencies. Prevents building features in the wrong order and surfaces breaking changes before they occur.

**Required Sections:**

```
# Dependency Reference

## Feature Dependency Graph
(Full 25-feature dependency chain — matches Section 3 of blueprint)
Mark each feature: not_started | in_progress | complete | blocked

## Blocked Features
| Feature | Blocked By | Estimated Unblock Date |

## External Package Dependencies
| Package | Version | Used For | Last Updated |
(Python: fastapi, sqlalchemy, celery, redis, pydantic, alembic, argon2-cffi, boto3, structlog, sentry-sdk)
(Node: react, vite, tanstack-query, zustand, axios, react-router-dom)

## Infrastructure Dependencies
| Component | Version | Role | Health Check |
(PostgreSQL, Redis, Cloudflare R2, Sentry)
```

**Update Rules:**
- Update feature status immediately when a feature's state changes
- Add new blocked features with their blocking reason
- Update package versions when packages are upgraded
- Do not remove feature entries — this is a history document

**Ownership:** Project lead. Reviewed at the start of each development week.

---

### FILE 5: ROADMAP.md

**Purpose:** Current state of the 4-week implementation roadmap. Tracks actual progress against the plan, flags delays, and records completed milestones.

**Required Sections:**

```
# Implementation Roadmap

## Phase Status
Week 1 Foundation: [complete | in_progress | not_started]
Week 2 Assessment: [complete | in_progress | not_started]
Week 3 Intelligence: [complete | in_progress | not_started]
Week 4 Recovery: [complete | in_progress | not_started]

## Week 1 — Foundation
Goal: Questions can enter the system. Students can register.
End checkpoint: 1,000 questions imported, student can log in.
| Task | Status | Completed |

## Week 2 — Assessment Engine
Goal: Students can take tests.
End checkpoint: Complete Full NEET Mock, score returned synchronously.
| Task | Status | Completed |

## Week 3 — Intelligence Layer
Goal: Students can understand their performance.
End checkpoint: Dashboard shows heatmap within 30 seconds of submission.
| Task | Status | Completed |

## Week 4 — Recovery + Polish
Goal: Students get an action plan. System is beta-ready.
End checkpoint: End-to-end test complete; 5 beta students onboarded.
| Task | Status | Completed |

## Schedule Variance
| Week | Planned Completion | Actual | Delta | Cause |
```

**Update Rules:**
- Mark tasks complete with the date on which they were completed
- Record any schedule slippage with a cause in the variance table
- Do not delete tasks from the roadmap — mark them as skipped with a reason
- Update end-of-week checkpoint status on the last day of each week

**Ownership:** Project lead. Updated daily during active development.

---

### FILE 6: IMPLEMENTATION_QUEUE.md

**Purpose:** The active task queue for AI-assisted development sessions. Every implementation session begins by reading the top task from this queue. Provides the complete context needed for a Copilot session without requiring the developer to reconstruct it.

**Required Sections:**

```
# Implementation Queue

## Active Task
TASK-ID: [ID]
Feature: [F0XX - Feature Name]
Description: [One paragraph of what to build]
Inputs: [What data/objects this task receives]
Outputs: [What this task produces]
Depends On: [Which prior tasks must be complete]
Blocks: [Which future tasks wait for this one]
Schema References: (links to relevant tables in DB_SCHEMA.md)
API References: (links to relevant endpoints in API_CONTRACTS.md)
Acceptance Criteria:
  - [ ] Criterion 1
  - [ ] Criterion 2
  - [ ] Criterion 3

## Next 3 Tasks
[Brief entries for the following three tasks in sequence]

## Completed Tasks
| Task ID | Feature | Completed | Notes |
```

**Update Rules:**
- Promote the next task to Active immediately on completing the current task
- Write Acceptance Criteria before starting implementation, not after
- Record completion date and any deviation from original scope in the completed table
- Each task must be scoped to one Copilot context window (one service method or one API endpoint)

**Ownership:** Project lead. Updated at the start and end of every development session.

---

### FILE 7: RISKS.md

**Purpose:** Living risk register. Tracks all identified risks with current status, assigned mitigation, and resolved/accepted outcomes. Provides a single place to check before each deployment.

**Required Sections:**

```
# Risk Register

## Open Risks
| Risk ID | Category | Description | Probability | Impact | Mitigation | Status |

## MVP Launch Blockers
| Risk ID | Description | Resolution Required By |

## Accepted Risks
| Risk ID | Description | Acceptance Rationale | Acceptance Date |

## Resolved Risks
| Risk ID | Description | Resolution | Resolved Date |

## Pre-Launch Risk Review
Reviewed: [date]
Reviewer: [name]
Open critical risks: [count]
Decision: [LAUNCH OK | LAUNCH BLOCKED]
```

**Update Rules:**
- Add new risks as they are discovered during implementation
- Move risks to Accepted or Resolved sections when their status changes
- Never delete risk entries — resolved risks are a learning record
- Pre-Launch Risk Review must be completed and signed off before any public launch

**Ownership:** Project lead. Reviewed before every deployment and before MVP launch.

---

### FILE 8: DECISIONS.md

**Purpose:** Decision log for all major architectural and product decisions. Provides the rationale behind every non-obvious choice, so future AI-assisted sessions do not re-litigate settled decisions.

**Required Sections:**

```
# Decision Log

## Decision Template
Decision ID: DEC-XXX
Date: YYYY-MM-DD
Decision: [What was decided]
Context: [Why this decision was needed]
Alternatives Considered: [What else was evaluated]
Reasoning: [Why this option won]
Risks: [Known downsides]
Validation Required: [How to confirm this was the right choice]
Impact Level: HIGH | MEDIUM | LOW
Status: ACTIVE | SUPERSEDED | REVERSED

## Active Decisions
[All decisions with status = ACTIVE]

## Superseded Decisions
[Decisions that have been replaced, with a link to the decision that replaced them]
```

**Update Rules:**
- Add a new entry for every significant architectural or product decision
- Mark a decision as SUPERSEDED (not deleted) when it is replaced
- Include the date on each decision — this creates a decision timeline
- Decisions about the PerformanceScore formula, RBAC policy, and attempt data immutability require explicit entries

**Ownership:** Project lead. Updated whenever a significant decision is made.

---

### FILE 9: TESTING.md

**Purpose:** Living test plan and quality gate reference. Documents all test cases, coverage targets, and testing status by domain and feature. Confirms what has been tested before each deployment.

**Required Sections:**

```
# Testing Reference

## Test Coverage Targets
| Domain | Unit Coverage Target | Integration Coverage | Status |
| Identity | 90% | All auth flows | |
| Content | 80% | Import pipeline | |
| Assessment | 90% | Full attempt lifecycle | |
| Intelligence | 80% | Analytics chain | |
| Recovery | 80% | Mission generation | |

## Critical Test Cases (Must Pass Before Launch)
| Test ID | Description | Feature | Status |
TCS-001: Complete attempt lifecycle (start → submit → score)
TCS-002: Idempotent submission (double submit returns same score)
TCS-003: Celery chain: AttemptCompleted → RecoveryMission (end-to-end)
TCS-004: RBAC enforcement: Student cannot access Teacher API
TCS-005: RBAC enforcement: User A cannot read User B's attempt
TCS-006: Performance: 50 concurrent test submissions within SLA
TCS-007: Performance: Dashboard P95 < 1000ms at 100k rows
TCS-008: Import: 1,001-row file rejected with correct error
TCS-009: Recovery Mission cold start: 1 mission for student with < 3 attempts
TCS-010: End-to-end student journey: register → mock → dashboard → missions

## Performance Test Results
| Test | Target | Actual | Date |

## Security Test Results
| Test | Expected | Actual | Date |

## Known Test Gaps
| Gap ID | Description | Risk Level | Planned Resolution |

## Pre-Launch Test Sign-Off
Test suite last run: [date]
Coverage: [%]
Critical tests passing: [count / 10]
Decision: [LAUNCH OK | LAUNCH BLOCKED]
```

**Update Rules:**
- Mark each Critical Test Case as PASS or FAIL after each test run
- Add new test cases when new edge cases are discovered during development
- Record actual performance test results as they are measured
- Pre-Launch Test Sign-Off must be completed and dated before public launch
- Never delete test cases — mark them as deprecated with a rationale if they become irrelevant

**Ownership:** Backend lead for backend tests; Frontend lead for frontend tests. Project lead owns the Pre-Launch Sign-Off.

---

*Batch 6 complete. All seven Batch 6 deliverables generated from NEET_POS_Engineering_Blueprint.md as the single source of truth.*  
*Decision Log: 12 decisions. Risk Analysis: 24 risks across 7 categories. Change Impact: 7 domains analyzed. Requirement Coverage: 45/45 = 100%. Dependency Graph: critical path identified. Final Checklists: 8 checklists, 110+ actionable items. Project Memory: 9 files fully specified.*
