# NEET Performance Operating System — Engineering Intelligence Blueprint

**Document Type:** Production-Grade Architecture & Implementation Blueprint  
**MVP Scope:** 25 Core Features — F001, F002, F003, F005, F006, F007, F008, F009, F010, F011, F012, F014, F016, F017, F018, F023, F024, F025, F026, F027, F028, F031, F044, F045, F047  
**Source Authority:** Modules 1, 2, 3, 4, 6 (primary) | 78-Feature Catalog (reference) | Execution Guide (supplementary)  
**Status:** MVP First-Launch Engineering Reference

---

## Table of Contents

1. Executive Project Analysis  
2. MVP Feature Selection Summary  
3. Feature Dependency and Risk Matrix  
4. Domain-Driven Architecture Blueprint  
5. Functional & Non-Functional Requirements  
6. Production-Grade Architecture Design  
7. Advanced Data Architecture  
8. API & Backend Engineering Blueprint  
9. End-to-End Execution Workflow  
10. Engineering Decision Analysis  
11. Scalability & Production Evolution  
12. AI-Assisted Development Structuring  
13. Step-by-Step Implementation Roadmap  
14. README & GitHub Presentation Blueprint  
15. Architecture Validation Review  

---

## Section 1 — Executive Project Analysis

### 1.1 Product Purpose

The system is a **NEET Performance Operating System** — not a test platform, not a content platform, and not an AI tutor. The confirmed product vision, derived from all five source modules, is:

> A system that explains why a student is losing marks, why they are stuck, what they should do next, how likely improvement is, and how their performance evolves over time.

The source research repeatedly and unambiguously establishes this positioning. Physics Wallah and other incumbents provide content. This system provides **diagnostic intelligence and recovery intelligence** built on top of behavioral data produced by test-taking.

### 1.2 Real-World Problem Being Solved

NEET aspirants face five compounding problems that no existing platform addresses in combination:

**Cognitive:** Students drown in content (lectures, PDFs, DPPs, PYQs, coaching notes) but lack clarity on what actually controls their score. They cannot see why they lost marks — only that they did.

**Analytical:** Platforms report outcomes (score = 510, accuracy = 67%) but do not explain root causes. Students cannot distinguish between conceptual gaps, execution errors, timing failures, and confidence collapses from a single metric.

**Behavioral:** Students avoid weak areas, repeat mistakes without tracking them, and waste decision energy daily on "what should I study today?" rather than studying. Decision fatigue compounds preparation inefficiency.

**Emotional:** After poor mock tests, students experience shame, panic, and motivation collapse. Platforms show a score and stop there. No system converts failure into a structured recovery plan.

**Operational:** High-performing students maintain handwritten mistake journals and revision logs. This system automates and scales that behavior into a data-driven intelligence layer.

### 1.3 Core Engineering Objectives

The MVP must deliver exactly one complete functional loop:

```
Question Bank
    ↓
Test Engine (behavioral data collection)
    ↓
Attempt Tracking (event capture at atomic level)
    ↓
Performance Intelligence (diagnosis)
    ↓
Recovery System (prescription)
    ↓
Return engagement
```

Every feature in the MVP exists to establish or advance this loop. Features outside this loop are explicitly deferred.

### 1.4 Operational Workflow Summary

A student registers, creates a profile, takes a test (Full Mock, Unit Test, or Mixed Revision), and the system captures every behavioral event — answer selection, answer changes, time per question, review flags. After submission, the Performance Dashboard synthesizes that data into a score explanation, a Weakness Heatmap showing chapter-level failure points, and a Performance Score representing readiness trajectory rather than raw marks. The Mistake Vault classifies every wrong answer by root cause. Recovery Missions translate that classification into a structured action plan for the next study session.

### 1.5 Technical Complexity Assessment

| Dimension | Assessment |
|---|---|
| Data Volume | AttemptAnswer table becomes the fastest-growing table; every question event generates a row |
| Query Complexity | Aggregation queries across attempts, answers, subjects, and topics are analytically heavy |
| State Complexity | Test sessions require distributed state (active attempt, timer, answer draft) |
| Business Logic | Weakness detection, performance scoring, and mission generation require multi-factor computation |
| Concurrency | Multiple students taking tests simultaneously; submission must be idempotent |
| Consistency | Attempt records are financial-grade data — they determine scores and must never be corrupted |

### 1.6 Critical Engineering Requirements

**Confirmed from source modules:**

- JWT-based authentication with refresh token rotation (Module 1)
- RBAC with Student, Teacher, Admin roles (Module 1)
- Question taxonomy: Subject → Chapter → Topic hierarchy (Module 2)
- Bulk question import via CSV/XLSX/JSON (Module 2)
- NEET scoring: +4 correct, -1 incorrect, 0 unanswered (Module 3)
- Timer engine with per-question time tracking (Module 3)
- Attempt tracking at atomic answer level (Module 3)
- Performance dashboard driven by aggregated attempt data (Module 4)
- Weakness detection operating across subject/chapter/topic dimensions (Module 4)
- Mistake classification by root cause type (Module 6)
- Recovery mission generation from analytics inputs (Module 6)

**Inferred from architecture (labeled as inferred):**

- PostgreSQL as primary data store (consistent recommendation across execution guide)
- Redis for active test state caching (execution guide, confirmed pattern)
- Celery + Redis for background analytics computation (execution guide)
- FastAPI as backend framework (execution guide, consistent with async requirements)
- React/Vite as frontend framework (consistent with prior project context)

### 1.7 System Constraints

- Solo founder context means sequential module delivery, not parallel team streams
- Month-1 timeline enforces feature minimalism — no scope creep
- Analytics features require behavioral data maturity; they cannot be validated before multiple test attempts exist
- Attempt Tracking (F026) is the single most critical data collection feature; all intelligence features derive from it

### 1.8 Hidden and Implied Requirements

- **Idempotent submission:** A student submitting a test twice (network retry, browser back) must not generate duplicate attempt records.
- **Test state recovery:** If a student's browser crashes during a test, their in-progress answers must be recoverable.
- **Analytics eventual consistency:** Performance Dashboard and Weakness Heatmap may operate on computed aggregates that do not need to be real-time — near-real-time (post-submission computation) is acceptable.
- **Audit trail:** All authentication events and question state changes require immutable audit records (Module 1).
- **Question approval workflow:** Questions should not be served in tests until they reach "Published" status (Module 2).

### 1.9 Architectural Pressure Points

- The `attempt_answers` table will grow faster than any other table and requires partitioning planning from day one.
- Analytics computation should be moved to background workers (Celery) immediately to prevent slow API responses after test submission.
- The Performance Score (F031) is a multi-factor calculation; its formula must be locked early and versioned, because changing it retroactively invalidates historical scores.
- Recovery Mission generation (F045) is the most complex orchestration task in the MVP — it must consume outputs from F026, F027, F028, F031, and F044 simultaneously.

---

## Section 2 — MVP Feature Selection Summary

### 2.1 The 25 MVP Features

The following 25 features are the complete and fixed MVP launch set. Together they deliver the full loop: Question → Test → Attempt Tracking → Intelligence → Recovery → Return.

#### Module 1 — Authentication (4 features)

| ID | Feature | Why MVP | Priority | Business Value |
|---|---|---|---|---|
| F001 | Student Registration | No identity = no analytics attribution. Every intelligence feature requires a persistent user. | P0 | Enables longitudinal performance tracking |
| F002 | Login | Secure access required before any protected resource can be reached. | P0 | Session establishment for test access |
| F003 | Profile Management | Target year, target score, and subject preferences feed into personalization and recommendation weighting. | P0 | Improves recommendation context |
| F005 | Role-Based Access Control | Student/Teacher/Admin segregation is required to prevent data leakage and unauthorized operations from day one. | P0 | Security and multi-actor platform support |

**Excluded from MVP:** F004 (Session Management) — JWT handles this at MVP scale. Advanced session dashboards and device tracking are post-MVP.

#### Module 2 — Question System (8 features)

| ID | Feature | Why MVP | Priority | Business Value |
|---|---|---|---|---|
| F006 | Question Bank | Central content repository without which no test can be generated. Tier-1 dependency for all downstream features. | P0 | Foundation of all assessment content |
| F007 | Question Import Pipeline | Bulk CSV/XLSX import allows rapid seeding of 5,000–10,000 questions without manual entry. | P0 | Operational velocity for content population |
| F008 | PYQ Database | Previous Year Questions carry the highest NEET exam relevance weight and are the first content students demand. | P0 | Immediate perceived platform value |
| F009 | Question Tagging | Tags drive weakness detection, recovery mission generation, and test composition. Without tags, analytics cannot operate at topic granularity. | P0 | Enables all intelligence features |
| F010 | Subject Classification | Root level of the taxonomy hierarchy (Physics, Chemistry, Biology). | P0 | Required for test composition and analytics |
| F011 | Chapter Classification | Second level of taxonomy. Required for chapter-level weakness detection. | P0 | Weakness Heatmap granularity |
| F012 | Topic Classification | Third level of taxonomy. Most granular analytics unit in the MVP. | P0 | Recovery Mission precision |
| F014 | Question Search | Enables teachers and admins to locate questions for test building without requiring direct database access. | P1 | Operational efficiency |

**Excluded from MVP:** F013 (Difficulty Classification — use simple enum), F015 (Question Validation — use manual review initially).

#### Module 3 — Test Engine (7 features)

| ID | Feature | Why MVP | Priority | Business Value |
|---|---|---|---|---|
| F016 | Full NEET Mock | Primary engagement driver. 180-question simulation produces the richest behavioral dataset per session. | P0 | Premium retention event, rank benchmarking |
| F017 | Unit Tests | Chapter-level assessment allows targeted practice outside full mock format. | P0 | Daily engagement touchpoint |
| F018 | Mixed Revision Tests | Cross-chapter mixed tests simulate retention testing and produce multi-subject behavioral data. | P0 | Revision habit support |
| F023 | Timer Engine | Per-question and total time tracking is the source of timing intelligence signals (pacing, time killers). | P0 | Required for all time-based analytics |
| F024 | OMR Simulation | Answer change tracking and review flag behavior produce confidence and decision-quality signals. | P0 | Confidence and execution intelligence |
| F025 | Negative Marking | NEET standard scoring (+4/-1/0) must be accurate. Guessing behavior analysis depends on tracking negative mark choices. | P0 | Scoring accuracy and risk intelligence |
| F026 | Attempt Tracking | **The single most important feature in the entire MVP.** Every intelligence feature derives from the atomic events captured here: selection, change, review, skip, timing. | P0 | Source of all analytics intelligence |

**Excluded from MVP:** F019, F020, F021, F022 — generated from the same engine post-MVP when behavioral data enables intelligent question selection.

#### Module 4 — Performance Intelligence (3 features)

| ID | Feature | Why MVP | Priority | Business Value |
|---|---|---|---|---|
| F027 | Performance Dashboard | The primary decision interface — converts analytics into visible, actionable explanations. First differentiation visible to students. | P0 | Core product differentiation |
| F028 | Weakness Heatmap | Visual chapter-level failure mapping. Answers "where am I losing marks?" at the topic granularity. | P0 | Diagnostic intelligence |
| F031 | Performance Score | Unified readiness metric beyond raw marks. Represents accuracy, consistency, and improvement trajectory. | P0 | Engagement and self-awareness hook |

**Excluded from MVP:** F029, F030, F032–F035 — require multiple tests and historical behavioral data to generate meaningful signals.

#### Module 6 — Recovery System (3 features)

| ID | Feature | Why MVP | Priority | Business Value |
|---|---|---|---|---|
| F044 | Mistake Vault | Persistent mistake intelligence repository. Converts wrong answers into classified, tracked, prioritized recovery assets. | P0 | Retention hook — transforms failure into data |
| F045 | Recovery Missions | Translates analytics into a structured next-session action plan. Answers "what should I do tomorrow?" | P0 | Highest retention feature in MVP |
| F047 | Weak Topic Recommendations | Prescriptive topic-level guidance derived from heatmap and vault data. | P0 | Reduces decision fatigue |

**Excluded from MVP:** F046 (Daily Recovery Plan — requires habit data), F048, F049, F050 — require data maturity.

### 2.2 Why These 25 Features Are the Optimal First-Launch Set

These 25 features are the minimum set required to prove the core product thesis: **students who take tests on this platform understand their failures more deeply and receive a recovery plan**, a capability no incumbent provides.

The scope achieves several things simultaneously:

It generates the behavioral dataset (via F026) that all future intelligence features (Why Am I Stuck, Rank Leakage, Progress Radar, Learning DNA) require. Without this data, those features cannot be built meaningfully. The MVP is therefore the data collection foundation for the entire future product.

It completes a retainable experience loop. A student can register, take a test, receive an explanation of their weaknesses, and get a recovery mission in a single session. This loop is sufficient to generate word-of-mouth and early retention without any gamification, habit systems, or AI intelligence layers.

It is realistically executable in a solo-founder, 4-week sprint with a backend-first development approach.

### 2.3 What Is Intentionally Excluded

**Excluded from MVP and why:**

Psychology Engine (F036–F043): Requires hundreds of test events per student to generate statistically meaningful confidence, panic, and stress signals. Building the infrastructure before the data exists wastes implementation cycles.

Identity/Prediction Layer (F051–F064): Brain Twin, Learning DNA, Future Score Simulator — all data-hungry systems that require established behavioral histories.

Habit/Engagement Layer (F065–F072): Daily Performance Score, Brain CEO, Zero Decision Mode — valuable retention features but dependent on repeated daily engagement data.

Teacher Analytics (F076–F078): Post-MVP once student usage establishes question quality patterns worth analyzing.

---

## Section 3 — Feature Dependency and Risk Matrix

### 3.1 Dependency Map

```
F001 (Registration)
    ↓
F002 (Login)
    ↓
F003 (Profile Management)
F005 (RBAC)
    ↓
F006 (Question Bank)
    ↓
F007 (Import Pipeline) → F008 (PYQ Database)
F009 (Tagging) → F010 (Subject) → F011 (Chapter) → F012 (Topic)
F014 (Search)
    ↓
F016 (Full Mock) → F017 (Unit Tests) → F018 (Mixed Tests)
F023 (Timer Engine)
F024 (OMR Simulation)
F025 (Negative Marking)
    ↓
F026 (Attempt Tracking)  ← CRITICAL CONVERGENCE POINT
    ↓
F027 (Performance Dashboard)
F028 (Weakness Heatmap)
F031 (Performance Score)
    ↓
F044 (Mistake Vault)
    ↓
F047 (Weak Topic Recommendations)
    ↓
F045 (Recovery Missions)
```

### 3.2 Full Risk Matrix

| ID | Feature | Depends On | Blocks | Dev Complexity | Technical Risk | Integration Risk | Data Risk | Testing Risk |
|---|---|---|---|---|---|---|---|---|
| F001 | Registration | None | F002, F003, F005 | Low | Low | Low | Medium | Low |
| F002 | Login | F001 | All protected features | Low | Medium | Low | Medium | Low |
| F003 | Profile Mgmt | F001, F002 | F027, F047 | Low | Low | Low | Low | Low |
| F005 | RBAC | F001, F002 | All API access | Medium | Medium | Low | Low | Medium |
| F006 | Question Bank | F010, F011, F012 | F007, F008, F016, F017, F018 | Medium | Low | Low | Medium | Medium |
| F007 | Import Pipeline | F006, F009 | F008 | Medium | Medium | Low | High | High |
| F008 | PYQ Database | F006, F007 | F016 | Low | Low | Low | Medium | Low |
| F009 | Tagging | F006 | F028, F044, F047 | Low | Low | Low | Low | Low |
| F010 | Subject Classif. | None | F011, F006 | Low | Low | Low | Low | Low |
| F011 | Chapter Classif. | F010 | F012, F006 | Low | Low | Low | Low | Low |
| F012 | Topic Classif. | F011 | F009, F006 | Low | Low | Low | Low | Low |
| F014 | Question Search | F006, F009 | None | Low | Low | Low | Low | Low |
| F016 | Full NEET Mock | F006, F023, F025 | F026 | High | High | Medium | Medium | High |
| F017 | Unit Tests | F006, F023, F025 | F026 | Medium | Medium | Low | Low | Medium |
| F018 | Mixed Tests | F006, F023, F025 | F026 | Medium | Medium | Low | Low | Medium |
| F023 | Timer Engine | None | F016, F017, F018, F026 | Medium | High | Low | High | High |
| F024 | OMR Simulation | F023 | F026 | Medium | Medium | Low | Medium | Medium |
| F025 | Negative Marking | F006 | F026, F031 | Low | Low | Low | Medium | Medium |
| F026 | Attempt Tracking | F016/F017/F018, F023, F024, F025 | F027, F028, F031, F044, F045, F047 | High | High | High | High | High |
| F027 | Perf. Dashboard | F026, F028, F031 | F044, F045 | High | Medium | Medium | Medium | High |
| F028 | Weakness Heatmap | F026, F009, F011, F012 | F044, F047, F045 | High | Medium | Medium | High | High |
| F031 | Performance Score | F026, F025 | F027, F045 | High | High | Low | High | High |
| F044 | Mistake Vault | F026, F006, F009 | F045, F047 | High | Medium | Medium | High | High |
| F045 | Recovery Missions | F044, F028, F031, F047 | None | High | High | High | Medium | High |
| F047 | Weak Topic Recs | F028, F044, F026 | F045 | Medium | Medium | Medium | Medium | Medium |

### 3.3 Critical Path Features

The following features must be completed before any subsequent feature can be started. They form the critical path:

```
F010 → F011 → F012 → F006 → F009
                                ↓
F001 → F002 → F005         [Content Ready]
                                ↓
                        F023 → F016/F017/F018
                                ↓
                            F026  ← MVP CONVERGENCE POINT
                                ↓
                    F028 → F027 → F044 → F047 → F045
```

### 3.4 Release Blockers

Any defect in the following features blocks the entire MVP launch:

- F001 (broken registration = no students)
- F006 (no question bank = no tests)
- F026 (broken tracking = no intelligence)
- F016 (no mock test = no engagement)

F026 is the single highest-risk feature in the entire MVP because it sits at the convergence of all input features and is the source of all output features.

---

## Section 4 — Domain-Driven Architecture Blueprint

### 4.1 Bounded Contexts

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEET Performance OS                          │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   IDENTITY       │    │   CONTENT        │                   │
│  │   DOMAIN         │    │   DOMAIN         │                   │
│  │                  │    │                  │                   │
│  │  User            │    │  Question        │                   │
│  │  Profile         │    │  Subject         │                   │
│  │  Role            │    │  Chapter         │                   │
│  │  Session         │    │  Topic           │                   │
│  │  Permission      │    │  PYQ             │                   │
│  └────────┬─────────┘    └───────┬──────────┘                  │
│           │                      │                             │
│           ▼                      ▼                             │
│  ┌─────────────────────────────────────────┐                   │
│  │           ASSESSMENT DOMAIN              │                   │
│  │                                          │                   │
│  │   Test   TestSection   TestQuestion      │                   │
│  │   Attempt   AttemptAnswer                │                   │
│  │   TimerEvent   OMREvent                  │                   │
│  └────────────────────┬────────────────────┘                   │
│                       │                                         │
│                       ▼                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │         INTELLIGENCE DOMAIN              │                   │
│  │                                          │                   │
│  │  PerformanceSnapshot  WeaknessSignal     │                   │
│  │  PerformanceScore  SubjectAnalytics      │                   │
│  │  ChapterAnalytics  TopicAnalytics        │                   │
│  └────────────────────┬────────────────────┘                   │
│                       │                                         │
│                       ▼                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │           RECOVERY DOMAIN                │                   │
│  │                                          │                   │
│  │  Mistake  MistakeOccurrence              │                   │
│  │  MistakePattern  RecoveryMission         │                   │
│  │  MissionTask  WeakTopicRecommendation    │                   │
│  └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Domain Ownership

| Domain | Aggregate Roots | Domain Services | Owns |
|---|---|---|---|
| Identity | User, Role | AuthService, RBACService | Authentication, session, permissions |
| Content | Question, Subject | QuestionService, TaxonomyService | All question lifecycle, tagging, import |
| Assessment | Test, Attempt | TestEngineService, AttemptService | Test session, scoring, tracking |
| Intelligence | PerformanceSnapshot | AnalyticsService, ScoreService | Aggregation, dashboard computation |
| Recovery | RecoveryMission, Mistake | RecoveryService, MistakeService | Mistake classification, mission generation |

### 4.3 Shared Services

| Service | Consumed By | Purpose |
|---|---|---|
| AuditService | All domains | Immutable event log for all state changes |
| NotificationService | Identity, Assessment | Email verification, test completion alerts |
| StorageService | Content | Question image and file storage |

### 4.4 Cross-Domain Contracts

**Assessment → Intelligence:** `AttemptCompletedEvent` triggers analytics computation. Contains attempt_id, user_id, test_id, completed_at.

**Intelligence → Recovery:** `WeaknessDetectedEvent` triggers mistake classification and mission generation. Contains user_id, topic_ids, severity scores.

**Content → Assessment:** `QuestionResolvedEvent` provides question metadata at test generation time. Read-only projection, not a live join.

### 4.5 MVP to Production Domain Evolution

MVP operates as a monolith with internal domain separation (modules/packages). Each domain is implemented as a self-contained package with clean interfaces. Post-MVP, each domain can be extracted into an independent service when scale demands it, without rewriting business logic.

---

## Section 5 — Functional & Non-Functional Requirements

### 5.1 Functional Requirements

#### Authentication Domain

- Students can register with email, password, name, grade, and target year.
- Duplicate email registration returns a 409 error.
- Email verification is required before test access is granted.
- Login returns JWT access token (15-minute expiry) and refresh token (7-day expiry).
- Refresh token rotation: each use invalidates the old token and issues a new one.
- Profile fields: name, target score, target year, preferred subject, notification preferences.
- RBAC enforces access boundaries: Students cannot access Teacher or Admin APIs; Teachers cannot access Admin APIs.
- All authentication events are logged to an immutable audit table.

#### Content Domain

- Questions are created with mandatory fields: text, options (4), correct answer, explanation, subject, chapter, topic, difficulty.
- Questions progress through states: Draft → Review → Approved → Published → Archived.
- Only Published questions are served in tests.
- Bulk import via CSV/XLSX/JSON validates each row and reports errors per row without failing the entire batch.
- PYQ questions carry additional metadata: exam year, exam code, historical frequency.
- Question search supports filtering by subject, chapter, topic, difficulty, PYQ flag, and tags.

#### Assessment Domain

- Full NEET Mock: 180 questions, Physics (45) + Chemistry (45) + Biology (90), 180-minute timer.
- Unit Test: configurable chapter and topic selection, configurable question count.
- Mixed Revision Test: configurable multi-chapter selection, randomized question selection.
- Timer Engine tracks: test start time, per-question first-touch time, per-question time spent, section time, total elapsed.
- OMR Simulation tracks: answer selection events, answer change events (with timestamps), review flag events.
- Negative marking: +4 correct, -1 incorrect, 0 unanswered. Configurable per test type.
- Attempt submission is idempotent: duplicate submission for the same attempt_id is silently deduplicated.
- Active test state (in-progress answers) is persisted to Redis every 30 seconds to support browser-crash recovery.
- One active attempt per test per user at any given time.

#### Intelligence Domain

- Performance Dashboard renders within 1 second after test submission.
- Weakness Heatmap shows subject → chapter → topic severity ratings derived from accuracy rates and attempt frequency.
- Performance Score is a composite metric from: accuracy rate, attempt consistency, topic breadth, improvement delta, negative mark ratio.
- Dashboard must answer: Where am I losing marks? Why? What next?

#### Recovery Domain

- Mistake Vault captures every wrong answer, classified by root cause: Conceptual, Application, Calculation, Interpretation, Memory, Timing, Confidence, Guessing.
- Mistake Vault tracks recurrence: same question type wrong again = escalated severity.
- Recovery Missions are generated automatically post-test from: Weakness Heatmap + Mistake Vault + Performance Score.
- Each mission has: trigger reason, expected mark recovery, task list (topic to revise, question set to retry), completion status.
- Maximum 3 active missions per student at any time. Priority-ranked by expected score impact.
- Weak Topic Recommendations list topics with accuracy below threshold, ranked by mark leakage.

### 5.2 Non-Functional Requirements

| Category | MVP Target | Production Target |
|---|---|---|
| API Response Time | < 300ms P95 | < 150ms P95 |
| Dashboard Load | < 1000ms | < 500ms |
| Test Screen Latency | < 100ms | < 50ms |
| Concurrent Users | 100 | 10,000+ |
| Uptime | 99.5% | 99.9% |
| Data Durability | Daily backups | Point-in-time recovery |
| Security | JWT, HTTPS, Argon2, RBAC | WAF, key rotation, SSO, MFA |
| Observability | Sentry error tracking | Prometheus + Grafana + structured logging |
| Scalability | Single instance | Read replicas, background workers, partitioning |
| Maintainability | Domain-separated monolith, OpenAPI docs | Microservice extraction path |
| Compliance | Privacy consent, data deletion support | Audit logs, encryption at rest |

---

## Section 6 — Production-Grade Architecture Design

### 6.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│        React / Vite SPA           (Browser / Mobile Browser)       │
│        TanStack Query             (Server state, caching)           │
│        Zustand                    (Client state: test session)      │
│        React Router v6            (Navigation)                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS / REST
┌──────────────────────────────▼──────────────────────────────────────┐
│                         API GATEWAY LAYER                           │
│                                                                     │
│        Nginx / Caddy              (Reverse proxy, TLS termination)  │
│        Rate Limiting              (Per-IP, Per-user)                │
│        CORS Policy                                                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                         BACKEND LAYER (FastAPI)                     │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Auth Router  │  │ Question     │  │ Test Engine  │              │
│  │              │  │ Router       │  │ Router       │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                  │                      │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐              │
│  │ Analytics    │  │ Recovery     │  │ Admin        │              │
│  │ Router       │  │ Router       │  │ Router       │              │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘              │
│         │                 │                                         │
│         └────────┬─────────┘                                        │
│                  │                                                   │
│  ┌───────────────▼────────────────────────────────────────┐         │
│  │                  SERVICE LAYER                          │         │
│  │                                                         │         │
│  │  AuthService  JWTService  RBACService  AuditService     │         │
│  │  QuestionService  TaxonomyService  ImportService        │         │
│  │  TestEngineService  AttemptService  ScoringService      │         │
│  │  AnalyticsService  ScoreService  HeatmapService         │         │
│  │  MistakeService  RecoveryService  RecommendationService │         │
│  └───────────────┬────────────────────────────────────────┘         │
│                  │                                                   │
│  ┌───────────────▼────────────────────────────────────────┐         │
│  │                REPOSITORY LAYER                         │         │
│  │                                                         │         │
│  │  UserRepo  ProfileRepo  RoleRepo                        │         │
│  │  QuestionRepo  SubjectRepo  ChapterRepo  TopicRepo      │         │
│  │  TestRepo  AttemptRepo  AttemptAnswerRepo               │         │
│  │  SnapshotRepo  WeaknessRepo  MistakeRepo  MissionRepo   │         │
│  └───────────────┬────────────────────────────────────────┘         │
└──────────────────┼──────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────────┐
│                         DATA LAYER                                  │
│                                                                     │
│  ┌────────────────┐  ┌─────────────┐  ┌──────────────────────┐     │
│  │  PostgreSQL    │  │   Redis     │  │   Object Storage     │     │
│  │                │  │             │  │   (Cloudflare R2)    │     │
│  │  Primary store │  │  Active     │  │                      │     │
│  │  All domains   │  │  test state │  │  Question images     │     │
│  │  Analytics     │  │  Sessions   │  │  Import files        │     │
│  │  Audit         │  │  Dashboard  │  │  Reports             │     │
│  │  Snapshots     │  │  cache      │  │                      │     │
│  └────────────────┘  └─────────────┘  └──────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       BACKGROUND WORKERS                            │
│                                                                     │
│  Celery + Redis Broker                                              │
│                                                                     │
│  analytics_computation_task    (triggered by AttemptCompleted)      │
│  weakness_detection_task       (triggered by AnalyticsComputed)     │
│  mission_generation_task       (triggered by WeaknessDetected)      │
│  import_processing_task        (triggered by ImportUploaded)        │
│  email_notification_task       (triggered by events)                │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Backend Request Lifecycle

```
HTTP Request
    │
    ▼
Nginx (TLS termination, rate limiting)
    │
    ▼
FastAPI Router
    │
    ├── Request validation (Pydantic models)
    │
    ├── Authentication middleware (JWT decode → user_id extraction)
    │
    ├── RBAC middleware (permission check → 403 if denied)
    │
    ├── Route handler invoked
    │       │
    │       ├── Input DTOs validated
    │       │
    │       ├── Service layer called (business logic)
    │       │       │
    │       │       ├── Repository layer called (data access)
    │       │       │       │
    │       │       │       └── PostgreSQL / Redis
    │       │       │
    │       │       └── Async task dispatched if needed
    │       │
    │       └── Output DTO constructed
    │
    └── HTTP Response returned
```

### 6.3 Frontend Architecture

**Rendering:** SPA with React/Vite. Static assets served via CDN. No SSR required at MVP.

**State Management:**
- Server state (API data): TanStack Query with stale-while-revalidate caching.
- Client state (active test session): Zustand store. Test state persisted to localStorage every 30 seconds as backup to Redis server-side state.
- Auth state: Zustand with access token in memory (not localStorage); refresh token in httpOnly cookie.

**Authentication Flow:**
1. Login API returns access_token (in response body) and refresh_token (in httpOnly cookie).
2. Access token stored in Zustand memory store.
3. Axios interceptor attaches `Authorization: Bearer <token>` to all requests.
4. On 401, interceptor calls `/auth/refresh` endpoint, updates access token, retries original request.
5. On refresh failure, user is redirected to login.

**Test Session UI Lifecycle:**
1. Test started → Zustand test store initialized with question list, timer start.
2. Timer component runs countdown; emits tick events every second.
3. On answer selection → Zustand updated → debounced sync to server (PATCH /attempts/:id/answers).
4. On test submission → POST /attempts/:id/submit → redirect to results page.
5. Results page fetches analytics via TanStack Query; shows Performance Dashboard.

### 6.4 Module Interaction Flow

```
Student action: "Start Full NEET Mock"
    │
    ├── Frontend: POST /tests/:id/attempts
    │       └── TestEngineService creates Attempt record
    │           ├── Fetches 180 Published questions
    │           ├── Creates AttemptAnswer stubs (selected_option=null)
    │           └── Returns attempt_id + question list
    │
    ├── Frontend: Renders test UI with Zustand session state
    │       └── Timer running, OMR events tracked
    │
    ├── Every answer: PATCH /attempts/:id/answers/:question_id
    │       └── AttemptService updates AttemptAnswer
    │
    ├── Student submits: POST /attempts/:id/submit
    │       ├── ScoringService computes raw score (+4/-1/0)
    │       ├── Attempt marked as completed
    │       ├── AttemptCompletedEvent dispatched to Celery
    │       └── 200 OK returned immediately (analytics are async)
    │
    ├── Celery worker: analytics_computation_task
    │       ├── AnalyticsService aggregates AttemptAnswers
    │       ├── Computes subject/chapter/topic accuracy
    │       ├── Generates PerformanceSnapshot
    │       └── Dispatches WeaknessDetectedEvent
    │
    ├── Celery worker: weakness_detection_task
    │       ├── HeatmapService identifies weak topics (accuracy < threshold)
    │       ├── Updates WeaknessSignal records
    │       └── Dispatches MissionGenerationTrigger
    │
    └── Celery worker: mission_generation_task
            ├── MistakeService classifies wrong answers by root cause
            ├── RecoveryService generates mission from heatmap + vault + score
            └── Saves RecoveryMission + MissionTask records
```

---

## Section 7 — Advanced Data Architecture

### 7.1 Core Entity Relationship Design

```
users ──────────────── profiles
  │                       │
  │                    user_roles ──── roles ──── role_permissions ──── permissions
  │
  ├── attempts ────────────────────── tests ──────────── test_questions
  │       │                              │
  │       │                           test_sections
  │       │
  │       └── attempt_answers ──── questions ──── answer_options
  │               │                    │
  │               │                 question_tags ──── tags
  │               │                 question_explanations
  │               │
  │           subjects ── chapters ── topics
  │
  ├── performance_snapshots
  │       │
  │       ├── subject_analytics
  │       ├── chapter_analytics
  │       └── topic_analytics
  │
  ├── weakness_signals
  │
  ├── mistakes ──── mistake_occurrences ──── mistake_patterns
  │
  └── recovery_missions ──── mission_tasks
          │
      weak_topic_recommendations
```

### 7.2 Normalized Schema — Core Tables

#### users

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    email_verified  BOOLEAN DEFAULT FALSE,
    status          VARCHAR(20) DEFAULT 'pending',   -- pending | active | suspended
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_users_email ON users (email);
```

#### profiles

```sql
CREATE TABLE profiles (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name        VARCHAR(100) NOT NULL,
    last_name         VARCHAR(100) NOT NULL,
    target_score      INTEGER CHECK (target_score BETWEEN 0 AND 720),
    target_year       INTEGER NOT NULL,
    avatar_url        TEXT,
    notification_prefs JSONB DEFAULT '{}',
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_at        TIMESTAMPTZ DEFAULT now()
);
```

#### roles / user_roles / permissions / role_permissions

```sql
CREATE TABLE roles (
    id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL  -- student | teacher | admin | mentor
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE permissions (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource VARCHAR(100) NOT NULL,
    action   VARCHAR(50) NOT NULL,
    UNIQUE (resource, action)
);

CREATE TABLE role_permissions (
    role_id       UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
```

#### subjects / chapters / topics

```sql
CREATE TABLE subjects (
    id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,   -- Physics | Chemistry | Biology
    code VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE chapters (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(id),
    name       VARCHAR(200) NOT NULL,
    code       VARCHAR(20),
    sequence   INTEGER,
    UNIQUE (subject_id, name)
);

CREATE TABLE topics (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID NOT NULL REFERENCES chapters(id),
    name       VARCHAR(200) NOT NULL,
    sequence   INTEGER,
    UNIQUE (chapter_id, name)
);
```

#### questions

```sql
CREATE TABLE questions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id    UUID NOT NULL REFERENCES subjects(id),
    chapter_id    UUID NOT NULL REFERENCES chapters(id),
    topic_id      UUID REFERENCES topics(id),
    question_text TEXT NOT NULL,
    explanation   TEXT,
    difficulty    VARCHAR(20) NOT NULL DEFAULT 'medium',  -- easy | medium | hard | trap
    is_pyq        BOOLEAN DEFAULT FALSE,
    pyq_year      INTEGER,
    status        VARCHAR(20) DEFAULT 'draft',            -- draft | review | approved | published | archived
    author_id     UUID REFERENCES users(id),
    version       INTEGER DEFAULT 1,
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_questions_subject ON questions(subject_id);
CREATE INDEX idx_questions_chapter ON questions(chapter_id);
CREATE INDEX idx_questions_status ON questions(status);
CREATE INDEX idx_questions_pyq ON questions(is_pyq) WHERE is_pyq = TRUE;
```

#### answer_options

```sql
CREATE TABLE answer_options (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id    UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    option_text    TEXT NOT NULL,
    is_correct     BOOLEAN NOT NULL DEFAULT FALSE,
    display_order  INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_options_question ON answer_options(question_id);
```

#### tests / test_sections / test_questions

```sql
CREATE TABLE tests (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title         VARCHAR(255) NOT NULL,
    test_type     VARCHAR(30) NOT NULL,  -- full_mock | unit_test | mixed_revision
    duration_mins INTEGER NOT NULL DEFAULT 180,
    total_marks   INTEGER NOT NULL,
    status        VARCHAR(20) DEFAULT 'draft',
    created_by    UUID REFERENCES users(id),
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE test_sections (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id     UUID NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    subject_id  UUID REFERENCES subjects(id),
    name        VARCHAR(100) NOT NULL,
    sequence    INTEGER NOT NULL
);

CREATE TABLE test_questions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id     UUID NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    section_id  UUID REFERENCES test_sections(id),
    question_id UUID NOT NULL REFERENCES questions(id),
    marks       INTEGER NOT NULL DEFAULT 4,
    sequence    INTEGER NOT NULL
);
CREATE INDEX idx_test_questions_test ON test_questions(test_id);
```

#### attempts — THE MOST CRITICAL TABLE

```sql
CREATE TABLE attempts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id),
    test_id       UUID NOT NULL REFERENCES tests(id),
    status        VARCHAR(20) DEFAULT 'in_progress',  -- in_progress | submitted | abandoned
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    submitted_at  TIMESTAMPTZ,
    total_score   INTEGER,
    raw_correct   INTEGER,
    raw_incorrect INTEGER,
    raw_unattempted INTEGER,
    UNIQUE (user_id, test_id, status)  -- prevents duplicate active attempts
);
CREATE INDEX idx_attempts_user ON attempts(user_id);
CREATE INDEX idx_attempts_test ON attempts(test_id);
CREATE INDEX idx_attempts_user_status ON attempts(user_id, status);
```

#### attempt_answers — THE LARGEST AND MOST IMPORTANT TABLE

```sql
CREATE TABLE attempt_answers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id          UUID NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    question_id         UUID NOT NULL REFERENCES questions(id),
    selected_option_id  UUID REFERENCES answer_options(id),
    is_correct          BOOLEAN,
    is_marked_review    BOOLEAN DEFAULT FALSE,
    answer_changed      BOOLEAN DEFAULT FALSE,
    time_spent_seconds  INTEGER DEFAULT 0,
    first_touched_at    TIMESTAMPTZ,
    answered_at         TIMESTAMPTZ,
    skipped             BOOLEAN DEFAULT FALSE,
    UNIQUE (attempt_id, question_id)
);
CREATE INDEX idx_attempt_answers_attempt ON attempt_answers(attempt_id);
CREATE INDEX idx_attempt_answers_question ON attempt_answers(question_id);
CREATE INDEX idx_attempt_answers_correct ON attempt_answers(is_correct);
-- Partition by attempt_id range when scale demands it
```

#### performance_snapshots

```sql
CREATE TABLE performance_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    attempt_id      UUID NOT NULL REFERENCES attempts(id),
    performance_score INTEGER NOT NULL,  -- 0-100 composite
    accuracy_rate   NUMERIC(5,2),
    computed_at     TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_snapshots_user ON performance_snapshots(user_id);
```

#### topic_analytics (aggregated per attempt per topic)

```sql
CREATE TABLE topic_analytics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    attempt_id      UUID NOT NULL REFERENCES attempts(id),
    topic_id        UUID NOT NULL REFERENCES topics(id),
    questions_seen  INTEGER NOT NULL DEFAULT 0,
    questions_correct INTEGER NOT NULL DEFAULT 0,
    accuracy_pct    NUMERIC(5,2),
    avg_time_seconds NUMERIC(7,2),
    computed_at     TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_topic_analytics_user_topic ON topic_analytics(user_id, topic_id);
```

#### weakness_signals

```sql
CREATE TABLE weakness_signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    topic_id        UUID NOT NULL REFERENCES topics(id),
    severity        VARCHAR(20) NOT NULL,   -- critical | high | medium | low
    accuracy_pct    NUMERIC(5,2),
    attempts_count  INTEGER DEFAULT 1,
    detected_at     TIMESTAMPTZ DEFAULT now(),
    resolved_at     TIMESTAMPTZ,
    UNIQUE (user_id, topic_id)
);
```

#### mistakes

```sql
CREATE TABLE mistakes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    question_id     UUID NOT NULL REFERENCES questions(id),
    attempt_id      UUID NOT NULL REFERENCES attempts(id),
    root_cause      VARCHAR(30) NOT NULL,   -- conceptual | application | calculation | memory | timing | confidence | guessing
    severity        VARCHAR(20) DEFAULT 'medium',
    recurrence_count INTEGER DEFAULT 1,
    first_seen_at   TIMESTAMPTZ DEFAULT now(),
    last_seen_at    TIMESTAMPTZ DEFAULT now(),
    resolved_at     TIMESTAMPTZ
);
CREATE INDEX idx_mistakes_user ON mistakes(user_id);
CREATE INDEX idx_mistakes_user_question ON mistakes(user_id, question_id);
CREATE INDEX idx_mistakes_root_cause ON mistakes(user_id, root_cause);
```

#### recovery_missions / mission_tasks

```sql
CREATE TABLE recovery_missions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    trigger_source  VARCHAR(50) NOT NULL,  -- weakness_heatmap | mistake_vault | performance_score
    title           VARCHAR(255) NOT NULL,
    expected_gain   INTEGER,               -- estimated mark recovery
    priority_score  INTEGER NOT NULL DEFAULT 50,
    status          VARCHAR(20) DEFAULT 'active',  -- active | completed | dismissed
    created_at      TIMESTAMPTZ DEFAULT now(),
    completed_at    TIMESTAMPTZ
);

CREATE TABLE mission_tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id  UUID NOT NULL REFERENCES recovery_missions(id) ON DELETE CASCADE,
    task_type   VARCHAR(30) NOT NULL,  -- revise_topic | retry_questions | take_mini_test
    topic_id    UUID REFERENCES topics(id),
    description TEXT NOT NULL,
    status      VARCHAR(20) DEFAULT 'pending',  -- pending | completed
    sequence    INTEGER NOT NULL
);
```

### 7.3 Indexing Strategy

**Critical indexes (must exist from day one):**

- `users(email)` — unique, login lookup
- `attempts(user_id, status)` — active test detection
- `attempt_answers(attempt_id)` — primary analytics aggregation
- `attempt_answers(question_id)` — question-level performance statistics
- `mistakes(user_id, root_cause)` — mistake classification queries
- `weakness_signals(user_id, topic_id)` — heatmap rendering
- `questions(subject_id)`, `questions(chapter_id)`, `questions(status)` — test generation queries

**Deferred indexes (add when query plans show degradation):**

- `topic_analytics(user_id, topic_id)` with date range
- `performance_snapshots(user_id)` ordered by computed_at

### 7.4 Caching Strategy

| Cache Key Pattern | TTL | Contents |
|---|---|---|
| `active_test:{attempt_id}` | 3 hours | Current answer draft for in-progress test |
| `test_questions:{test_id}` | 1 hour | Full question set for a test (read-heavy) |
| `user_dashboard:{user_id}` | 5 minutes | Aggregated dashboard data |
| `session:{user_id}` | 15 minutes | JWT session metadata |
| `question_search:{hash}` | 10 minutes | Common search result sets |

### 7.5 Data Consistency Rules

- Attempt scoring is computed synchronously at submission; analytics computation is async.
- A completed Attempt record is immutable (score, correct count, incorrect count cannot change post-submission).
- Mistake Vault entries are append-only; resolutions create a resolved_at timestamp rather than deleting records.
- Weakness Signals are upserted: on new detection, update severity and accuracy; do not duplicate.
- RecoveryMissions are capped at 3 active per user; mission generation enforces this via service layer.

---

## Section 8 — API & Backend Engineering Blueprint

### 8.1 API Organization

All APIs follow the pattern: `/api/v1/{domain}/{resource}`

Authentication: Bearer token in Authorization header for all protected routes.
Versioning: URL path versioning (`/api/v1/`).
Pagination: Cursor-based pagination for lists (`?cursor=uuid&limit=20`).
Error format: `{"code": "ERROR_CODE", "message": "Human readable", "details": {...}}`.

### 8.2 Authentication APIs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/v1/auth/register | Public | Student registration |
| POST | /api/v1/auth/verify-email | Public | Email verification |
| POST | /api/v1/auth/login | Public | Returns access + refresh tokens |
| POST | /api/v1/auth/refresh | Cookie | Refresh access token |
| POST | /api/v1/auth/logout | Bearer | Invalidate refresh token |
| GET | /api/v1/auth/me | Bearer | Current user + permissions |
| GET | /api/v1/profile | Bearer | Get student profile |
| PATCH | /api/v1/profile | Bearer | Update student profile |

**POST /api/v1/auth/login — Detail:**

Input: `{"email": "string", "password": "string"}`
Output: `{"access_token": "jwt", "expires_in": 900, "user_id": "uuid", "role": "student"}`
httpOnly Cookie: `refresh_token` (7 days, Secure, SameSite=Strict)
Business logic: Verify email_verified=true before issuing tokens. Log login event to audit table. Track failed_attempts; lock account after 5 consecutive failures.
Edge cases: Account suspended, email not verified, rate limit exceeded.
Security: Argon2id password comparison. Constant-time comparison to prevent timing attacks.

### 8.3 Question System APIs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/questions | Bearer (Teacher+) | List questions with filters |
| POST | /api/v1/questions | Bearer (Teacher+) | Create question |
| GET | /api/v1/questions/:id | Bearer | Get question detail |
| PATCH | /api/v1/questions/:id | Bearer (Teacher+) | Update question |
| DELETE | /api/v1/questions/:id | Bearer (Admin) | Archive question |
| POST | /api/v1/questions/import | Bearer (Admin) | Bulk import |
| GET | /api/v1/subjects | Bearer | List subjects |
| GET | /api/v1/subjects/:id/chapters | Bearer | List chapters in subject |
| GET | /api/v1/chapters/:id/topics | Bearer | List topics in chapter |
| GET | /api/v1/questions/search | Bearer (Teacher+) | Search with filters |

**POST /api/v1/questions/import — Detail:**

Input: Multipart form with CSV/XLSX/JSON file.
Processing: Async (Celery task). Returns `{"import_id": "uuid", "status": "processing"}`.
Polling: GET /api/v1/imports/:id returns status, success count, error count, error rows.
Validation: Per-row validation. Invalid rows collected in error report; valid rows committed.
Edge cases: File too large (>10MB rejected), unsupported format (400), malformed rows (reported per row), duplicate question detection.

### 8.4 Test Engine APIs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/tests | Bearer | List available tests |
| GET | /api/v1/tests/:id | Bearer | Get test details |
| POST | /api/v1/tests | Bearer (Admin) | Create test |
| POST | /api/v1/tests/:id/attempts | Bearer (Student) | Start test attempt |
| GET | /api/v1/attempts/:id | Bearer | Get attempt state (recovery) |
| PATCH | /api/v1/attempts/:id/answers | Bearer | Save answer events (batch) |
| POST | /api/v1/attempts/:id/submit | Bearer | Submit attempt |
| GET | /api/v1/attempts/:id/result | Bearer | Get scored result |

**POST /api/v1/tests/:id/attempts — Detail:**

Input: `{"test_id": "uuid"}`
Pre-conditions: Test exists and is published. No active attempt exists for this user+test. User is verified Student.
Output: `{"attempt_id": "uuid", "questions": [...], "duration_seconds": 10800, "started_at": "iso"}`
Business logic: Creates Attempt record (status=in_progress). Creates AttemptAnswer stubs for all 180 questions. Caches question list to Redis (`test_questions:{test_id}`). Stores attempt_id in Redis (`active_test:{attempt_id}`).
Idempotency: Returns existing in-progress attempt if called twice.

**PATCH /api/v1/attempts/:id/answers — Detail:**

Input: `{"events": [{"question_id": "uuid", "selected_option_id": "uuid", "time_spent": 45, "changed": false, "marked_review": false}]}`
Design: Accepts batch of events (up to 10 per call) to reduce network chattiness.
Processing: Upserts each AttemptAnswer. Updates Redis cache. Does not compute score.
Performance: Target < 100ms. Uses bulk upsert.

**POST /api/v1/attempts/:id/submit — Detail:**

Input: None (or `{"force": true}` for timer expiry).
Processing: Synchronous scoring (compute total_score, raw_correct, raw_incorrect). Mark attempt as submitted. Dispatch async analytics tasks.
Output: `{"score": 540, "correct": 135, "incorrect": 0, "unattempted": 45, "analytics_status": "computing"}`
Idempotency: Second call returns same response without re-scoring.
Edge cases: Already submitted (idempotent), attempt belongs to different user (403), timer already expired (accept submission).

### 8.5 Analytics APIs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/dashboard | Bearer | Performance Dashboard |
| GET | /api/v1/dashboard/heatmap | Bearer | Weakness Heatmap data |
| GET | /api/v1/dashboard/score | Bearer | Performance Score history |
| GET | /api/v1/dashboard/attempts | Bearer | Attempt history |
| GET | /api/v1/dashboard/attempts/:id | Bearer | Single attempt analytics |

**GET /api/v1/dashboard — Detail:**

Output includes: current_performance_score, last_attempt_summary, top_weaknesses (top 5 by severity), recent_missions, improvement_trend (last 5 tests).
Caching: Redis with 5-minute TTL. Cache invalidated on new attempt submission.
Performance: Target < 300ms with cache; < 1000ms without.

### 8.6 Recovery APIs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/mistakes | Bearer | Mistake Vault list |
| GET | /api/v1/mistakes/patterns | Bearer | Mistake pattern summary |
| GET | /api/v1/missions | Bearer | Active Recovery Missions |
| GET | /api/v1/missions/:id | Bearer | Mission detail with tasks |
| POST | /api/v1/missions/:id/start | Bearer | Begin mission execution |
| PATCH | /api/v1/missions/:id/tasks/:tid | Bearer | Complete mission task |
| POST | /api/v1/missions/:id/complete | Bearer | Mark mission complete |
| GET | /api/v1/recommendations | Bearer | Weak Topic Recommendations |

### 8.7 Error Handling Standards

| Scenario | HTTP Status | Error Code |
|---|---|---|
| Validation failure | 400 | VALIDATION_ERROR |
| Unauthenticated | 401 | UNAUTHORIZED |
| Insufficient permission | 403 | FORBIDDEN |
| Resource not found | 404 | NOT_FOUND |
| Duplicate resource | 409 | CONFLICT |
| Rate limit exceeded | 429 | RATE_LIMITED |
| Server error | 500 | INTERNAL_ERROR |
| Service unavailable | 503 | SERVICE_UNAVAILABLE |

### 8.8 Rate Limiting

| Endpoint | Limit |
|---|---|
| POST /auth/register | 5 per IP per minute |
| POST /auth/login | 10 per IP per minute |
| POST /questions/import | 3 per user per hour |
| All other authenticated | 200 per user per minute |

---

## Section 9 — End-to-End Execution Workflow

### 9.1 Complete Student Journey: First Test

```
1. REGISTRATION
   Student → POST /auth/register
   System → Creates User (status=pending), Profile, dispatches verification email
   Student → Clicks verification link → POST /auth/verify-email?token=xxx
   System → Sets email_verified=true, status=active
   Audit → USER_REGISTERED, EMAIL_VERIFIED events logged

2. LOGIN
   Student → POST /auth/login
   System → Validates credentials, issues JWT access token + httpOnly refresh token
   Frontend → Stores access_token in Zustand, refresh_token in cookie
   Audit → LOGIN_SUCCESS logged

3. PROFILE SETUP
   Student → PATCH /profile (target_score=620, target_year=2026)
   System → Updates profile, invalidates profile cache

4. TEST DISCOVERY
   Student → GET /tests (shows Full NEET Mock, Unit Tests available)
   System → Returns test list from PostgreSQL, filtered to published tests

5. TEST START
   Student → POST /tests/{mock_id}/attempts
   System → Creates Attempt (in_progress), fetches 180 questions, stubs 180 AttemptAnswers
   System → Caches question list in Redis (test_questions:{test_id}, 1hr TTL)
   System → Caches attempt state in Redis (active_test:{attempt_id}, 3hr TTL)
   Frontend → Receives question list, initializes Zustand test store, starts countdown timer

6. TEST EXECUTION (180 minutes)
   Student → Selects answer for Q1
   Frontend → Updates Zustand store, debounces server sync (500ms debounce)
   Frontend → PATCH /attempts/{id}/answers [batch of changed events]
   System → Upserts AttemptAnswers, updates Redis cache
   
   [Auto-save every 30 seconds to server, client localStorage as tertiary backup]
   [Student navigates, marks review, changes answers — all tracked]
   [Timer reaches 0 → Frontend auto-submits]

7. SUBMISSION
   Student → POST /attempts/{id}/submit
   System (sync) → ScoringService: iterates AttemptAnswers, computes score (+4/-1/0)
   System (sync) → Updates Attempt: total_score=540, raw_correct=135, raw_incorrect=0, raw_unattempted=45
   System (sync) → Sets status=submitted
   System (async) → Dispatches AttemptCompletedEvent to Celery queue
   System → Returns 200: {score, correct, incorrect, unattempted}

8. ANALYTICS COMPUTATION (async, within 30 seconds)
   Celery: analytics_computation_task
   → Fetches all 180 AttemptAnswers with joins to questions, chapters, topics
   → Computes subject_accuracy per subject (Physics/Chemistry/Biology)
   → Computes chapter_accuracy for every chapter in the test
   → Computes topic_accuracy for every topic
   → Computes avg_time_spent per topic
   → Persists PerformanceSnapshot, SubjectAnalytics, ChapterAnalytics, TopicAnalytics
   → Computes PerformanceScore composite (accuracy + consistency + breadth + improvement delta)
   → Persists PerformanceScore
   → Dispatches WeaknessDetectedEvent

9. WEAKNESS DETECTION (async)
   Celery: weakness_detection_task
   → Queries topic_accuracy records for this attempt
   → Identifies topics below accuracy threshold (e.g., < 50%)
   → Upserts WeaknessSignal records (severity = critical | high | medium)
   → Dispatches MissionGenerationTrigger

10. MISTAKE VAULT UPDATE (async)
    Celery: mistake_classification_task
    → Fetches all incorrect AttemptAnswers
    → For each wrong answer, applies root cause inference:
        time_spent < 20s → likely Guessing
        time_spent > 180s AND wrong → likely Timing/Overthinking
        answer_changed AND wrong → likely Confidence
        high difficulty + wrong → likely Conceptual
        medium/easy + wrong → likely Application or Memory
    → Upserts Mistake records (recurrence_count++ if existing)

11. RECOVERY MISSION GENERATION (async)
    Celery: mission_generation_task
    → Reads WeaknessSignals (top 5 by severity)
    → Reads Mistake patterns (most frequent root causes)
    → Reads PerformanceScore (identifies lowest-scoring dimension)
    → Generates up to 3 missions (priority ranked by expected_gain)
    → Each mission has 3-5 MissionTasks (revise_topic, retry_questions, take_mini_test)
    → Caps active missions at 3 per user

12. DASHBOARD VIEW
    Student → Returns to dashboard (next session)
    GET /dashboard → System returns cached analytics (5-min TTL)
    Student sees:
        PerformanceScore: 62/100
        Weakness Heatmap: Genetics 🔴, Thermodynamics 🔴, Organic Chemistry 🟡
        Recovery Missions: "Fix Genetics Mistakes", "Thermodynamics Revision"
        Weak Topic Recommendations: [Genetics, Human Physiology, Rotational Motion]
```

### 9.2 Recovery Mission Execution Workflow

```
Student → GET /missions → sees 3 active missions
Student → GET /missions/{id} → sees tasks: 
    Task 1: Revise "Mendelian Genetics" (topic_id)
    Task 2: Retry 10 previous Genetics questions
    Task 3: Take 20-question Genetics unit test

Student → POST /missions/{id}/start → mission status = executing
Student → Completes Task 1 (revision) → PATCH /missions/{id}/tasks/{t1}/complete
Student → Takes unit test (F017) → system links attempt to mission
Student → POST /missions/{id}/complete
System → Validates completion (all tasks done)
System → Records RecoveryOutcome (before_accuracy vs after_accuracy)
System → Updates WeaknessSignal (severity downgraded if improved)
System → Mission archived
```

---

## Section 10 — Engineering Decision Analysis

### 10.1 Technology Choices

| Decision | Choice | Rationale |
|---|---|---|
| Backend Framework | FastAPI (Python) | Async-native, Pydantic validation, OpenAPI auto-generation, type safety, excellent DX. Confirmed across execution guide. |
| Database | PostgreSQL | ACID guarantees for attempt data, JSONB for flexible fields, materialized views for analytics, full-text search capability for future, battle-tested at scale. |
| Cache | Redis | Session storage, active test state, dashboard caching, Celery broker. Single technology serving multiple infrastructure roles reduces operational complexity. |
| Task Queue | Celery + Redis | Analytics computation must be async to keep submission API fast. Celery is the lowest-friction choice for a Python FastAPI stack. RabbitMQ when scale demands it. |
| Frontend | React + Vite | Component ecosystem maturity, TanStack Query for server state, Zustand for client state. Lightweight bundle, fast HMR in development. |
| ORM | SQLAlchemy (async) | Async support with asyncpg driver, strong migration tooling via Alembic, excellent type support, supports complex joins needed for analytics queries. |
| Password Hashing | Argon2id | OWASP recommended. Superior memory-hardness over bcrypt. Module 1 explicitly recommends this. |
| Authentication | JWT (access) + httpOnly cookie (refresh) | Access token in memory prevents localStorage XSS theft. httpOnly cookie prevents JS-accessible refresh token theft. Refresh rotation limits token replay risk. |
| Object Storage | Cloudflare R2 | Execution guide recommends this explicitly over S3 for cost efficiency. Same API surface as S3 (AWS SDK compatible). |
| Error Monitoring | Sentry | Low-integration-cost, excellent Python + React support, provides stack traces and performance tracing. |

### 10.2 Architectural Tradeoffs

**Monolith vs Microservices:** MVP is a domain-separated monolith. Each domain is a Python package with its own routers, services, and repositories. This avoids distributed systems complexity (service discovery, inter-service auth, network latency) at MVP scale while preserving a clean extraction path. The domain boundaries in the code mirror future microservice boundaries.

**Sync vs Async Analytics:** Analytics computation is async (Celery). This means the dashboard is not instantly updated at submission — it lags 10–30 seconds. This tradeoff is correct: it keeps submission API response time under 300ms, which is the latency that determines user experience during test submission. The analytics delay is invisible because students need several seconds to read their initial score before viewing the full dashboard.

**Materialized Views vs OLAP:** MVP uses PostgreSQL materialized views refreshed after each attempt. This is sufficient for 100–1,000 concurrent users. At scale (10,000+ users), a dedicated analytics warehouse (BigQuery, ClickHouse) becomes necessary to avoid contention between OLAP queries and transactional writes on the same PostgreSQL instance.

**Weakness Detection Heuristics vs ML:** Root cause classification (Guessing, Timing, Conceptual) uses rule-based heuristics at MVP (time_spent thresholds, difficulty levels, answer change patterns). This is correct because ML models require labeled training data that does not exist yet. The heuristic outputs become the labeled training data for future ML classification.

### 10.3 Performance Decisions

- AttemptAnswer uses bulk upsert (not individual INSERT per answer event) to handle high-frequency answer changes during test execution.
- Dashboard API uses Redis cache with 5-minute TTL rather than recomputing on every request.
- Test question list is cached in Redis at attempt creation; it does not re-query PostgreSQL on every test screen render.
- Analytics queries use pre-aggregated `topic_analytics` table rather than raw `attempt_answers` aggregation on every dashboard load.

---

## Section 11 — Scalability & Production Evolution

### 11.1 MVP Scale Baseline

```
Concurrent users:    ~100
Daily test attempts: ~200
AttemptAnswer rows:  ~36,000 per day (200 tests × 180 questions)
Monthly rows:        ~1.1M
Annual rows:         ~13M
PostgreSQL:          Single instance, 16GB RAM, adequate for 2-3 years
```

### 11.2 Scaling Bottlenecks and Solutions

| Bottleneck | Occurs At | Solution |
|---|---|---|
| Analytics query contention | ~5,000 daily attempts | Add PostgreSQL read replica for analytics queries |
| AttemptAnswer table growth | ~50M rows | Partition by year: `attempt_answers_2025`, `attempt_answers_2026` |
| Dashboard query latency | ~10,000 users | Pre-compute snapshots; use Celery to refresh materialized views |
| Test question cache miss | High concurrency | Increase Redis TTL; pre-warm cache for published tests |
| Submission spike (exam period) | Concurrent submits | Queue submissions via Celery; return 202 Accepted + polling endpoint |

### 11.3 MVP → Production Architecture Evolution

**Phase 1 (MVP):** Single FastAPI instance, single PostgreSQL, single Redis, Celery with 2 workers.

**Phase 2 (Growth — 1K daily users):** Add PostgreSQL read replica for analytics. Separate analytics queries to replica. Add nginx upstream with 2 FastAPI workers. Add monitoring (Prometheus + Grafana).

**Phase 3 (Scale — 10K daily users):** Partition `attempt_answers` by year. Add Redis Cluster. Add CDN for static assets and question images. Move analytics to dedicated ClickHouse or BigQuery instance. Add background worker autoscaling.

**Phase 4 (Production OS):** Extract Identity, Content, Assessment, Intelligence, and Recovery into independent services. Add event streaming (Kafka or AWS Kinesis) to replace Celery for cross-service communication. Introduce GraphQL gateway for flexible frontend queries.

### 11.4 Observability Strategy

**MVP:**
- Sentry for error tracking and performance monitoring
- Structured JSON logging (Python `structlog`)
- Key metrics logged: API response time, test submission count, analytics computation time, mission generation count

**Growth:**
- Prometheus metrics endpoint on FastAPI
- Grafana dashboards: API latency percentiles, attempt submission rate, cache hit rate, Celery queue depth
- Alerting: queue depth > 100, API P95 > 500ms, Celery worker failure

### 11.5 Security Hardening Roadmap

**MVP:** JWT + Argon2id + HTTPS + RBAC + Rate limiting + Audit logging.

**Post-MVP:** WAF (Cloudflare), key rotation policy, SSO for institutional accounts, MFA for admin accounts, data encryption at rest (AES-256), GDPR-compliant data deletion workflows.

---

## Section 12 — AI-Assisted Development Structuring

### 12.1 PROJECT_BRAIN.md — What It Contains

The authoritative project memory file. Updated after every major implementation decision.

```markdown
# PROJECT_BRAIN.md

## Product Identity
- Product: NEET Performance Operating System
- Primary user: NEET aspirant (student)
- Core loop: Question → Test → Tracking → Intelligence → Recovery → Return

## Tech Stack (Confirmed)
- Backend: FastAPI (Python 3.11+)
- Database: PostgreSQL 16
- Cache/Queue: Redis 7 + Celery 5
- Frontend: React 18 + Vite + TanStack Query + Zustand
- Auth: JWT (access) + httpOnly cookie (refresh) + Argon2id
- Storage: Cloudflare R2
- Error tracking: Sentry

## MVP Feature Set (25 features)
[List all 25 with status: not_started | in_progress | complete]

## Domain Boundaries
[Domain map]

## Most Critical Table
- attempt_answers: source of all intelligence features
- Never delete rows from this table

## Analytics Architecture
- All analytics are async (Celery)
- Submission returns score synchronously
- Dashboard computed post-submission via background tasks
```

### 12.2 PROJECT_STATE.md — What It Contains

Current implementation status. Updated at the start and end of each development session.

```markdown
# PROJECT_STATE.md

## Current Phase: [Phase 1 | 2 | 3 | 4]
## Last Session: [date]
## Active Feature: [feature ID and name]

## Completed Features
- F001 Student Registration ✅
- F002 Login ✅
...

## In Progress
- F006 Question Bank — schema done, CRUD in progress

## Blocked
- F016 Full NEET Mock — blocked by F006

## Database Migrations
- 001_create_users.sql ✅
- 002_create_profiles.sql ✅
...

## Known Issues
[Any open bugs or technical debt]
```

### 12.3 API_CONTRACTS.md — What It Contains

Complete API reference for AI-assisted frontend development. Each endpoint documented with request/response schemas, status codes, and behavior notes. Organized by domain. Updated whenever a new endpoint is added.

### 12.4 DB_SCHEMA.md — What It Contains

Current canonical database schema with table definitions, indexes, and relationships. Updated after each migration. Includes: entity relationship notes, cardinality annotations, which tables are read-heavy vs write-heavy, current row counts (updated weekly in production).

### 12.5 CHANGELOG.md — What It Contains

```markdown
# CHANGELOG.md

## [Unreleased]
### Added
- F006 Question Bank: CRUD APIs

## [0.1.0] — YYYY-MM-DD
### Added
- F001 Student Registration
- F002 Login
- F003 Profile Management
- F005 RBAC

### Notes
- JWT expiry set to 15 minutes for MVP; will reduce to 5 minutes post-launch
```

### 12.6 TASK_QUEUE.md — What It Contains

Granular implementation tasks, organized by feature. Each task is one Copilot context window: small enough to implement in a single session, large enough to produce meaningful output.

```markdown
# TASK_QUEUE.md

## Active Task
TASK-047: Implement AttemptService.submit_attempt()
  - Inputs: attempt_id, user_id
  - Must compute score synchronously
  - Must dispatch Celery task
  - Must be idempotent
  - See: DB_SCHEMA.md (attempts table), API_CONTRACTS.md (/api/v1/attempts/:id/submit)
  
## Next Tasks
TASK-048: Implement ScoringService.compute_neet_score()
TASK-049: Implement AttemptCompletedEvent dispatch
TASK-050: Implement analytics_computation_task (Celery)
```

### 12.7 AI-to-Copilot Workflow

For each feature implementation session:

1. Open PROJECT_STATE.md → identify current active feature.
2. Open TASK_QUEUE.md → identify the specific task.
3. Open DB_SCHEMA.md → load relevant table definitions.
4. Open API_CONTRACTS.md → load endpoint specification.
5. Feed TASK_QUEUE entry + relevant schema sections + API contract as context to Copilot.
6. Implement. Test. Update PROJECT_STATE.md. Create CHANGELOG entry.

This pattern minimizes AI context loss because each task is self-contained with explicit schema and contract references.

---

## Section 13 — Step-by-Step Implementation Roadmap

### 13.1 Phase Structure

```
Week 1: Foundation (F001, F002, F003, F005, F006, F007, F008, F009, F010, F011, F012, F014)
Week 2: Assessment (F016, F017, F018, F023, F024, F025, F026)
Week 3: Intelligence (F027, F028, F031)
Week 4: Recovery + Polish (F044, F045, F047 + beta hardening)
```

### 13.2 Week 1 — Foundation

**Goal:** Questions can enter the system. Students can register.

**Day 1–2: Database + Auth**
1. Initialize PostgreSQL with Alembic migrations.
2. Create tables: users, profiles, roles, permissions, user_roles, role_permissions.
3. Implement UserRepository (CRUD).
4. Implement AuthService (register, verify_email, login, logout, refresh).
5. Implement JWTService (issue, validate, refresh).
6. Implement RBACMiddleware (permission check on every request).
7. Implement AuditService (append-only event log).
8. Write integration tests for F001, F002, F005.

**Day 3: Taxonomy**
9. Create tables: subjects, chapters, topics.
10. Implement TaxonomyService (seed subjects: Physics, Chemistry, Biology).
11. Create taxonomy management APIs (GET /subjects, GET /chapters, GET /topics).

**Day 4–5: Question System**
12. Create tables: questions, answer_options, question_tags.
13. Implement QuestionRepository (CRUD with filtering).
14. Implement QuestionService (create, update, approve, publish, archive).
15. Implement bulk import: CSV/XLSX parser + Celery task + validation report.
16. Implement Question Search API with filters.
17. Write integration tests for F006, F007, F008, F009, F014.

**End of Week 1 Checkpoint:**
- 1,000 questions can be imported and searched.
- Students can register, verify email, and log in.
- Admin can manage question status.

### 13.3 Week 2 — Assessment Engine

**Goal:** Students can take tests.

**Day 6–7: Test Structure**
18. Create tables: tests, test_sections, test_questions.
19. Implement TestService (create Full Mock, Unit Test, Mixed Test).
20. Seed one Full NEET Mock test with 180 questions from question bank.
21. Implement test listing API.

**Day 8: Timer Engine**
22. Design TimerEngine as a frontend-side countdown with server-side start_time reference.
23. Implement per-question time tracking in AttemptAnswer (time_spent_seconds).
24. Timer expiry → auto-submit endpoint call.

**Day 9–10: Attempt Engine (Critical)**
25. Create tables: attempts, attempt_answers.
26. Implement AttemptService (start_attempt, save_answers batch, submit_attempt).
27. Implement idempotent submission (duplicate submit detection).
28. Implement Redis caching for active test state.
29. Implement ScoringService (NEET +4/-1/0 scoring).
30. Implement OMR event tracking (answer changes, review flags) in attempt_answers.
31. Write extensive integration tests for F026 (every edge case in attempt lifecycle).

**End of Week 2 Checkpoint:**
- Student can start and complete a Full NEET Mock.
- Score is computed and returned synchronously.
- Every answer event is persisted.

### 13.4 Week 3 — Intelligence Layer

**Goal:** Students can understand their performance.

**Day 11–12: Analytics Pipeline**
32. Implement Celery task: analytics_computation_task.
33. Implement AnalyticsService: aggregate attempt_answers by subject/chapter/topic.
34. Persist: performance_snapshots, subject_analytics, chapter_analytics, topic_analytics.
35. Implement ScoreService: compute composite PerformanceScore from accuracy, consistency, breadth.
36. Implement PerformanceSnapshot persistence.

**Day 13: Weakness Detection**
37. Implement HeatmapService: identify topics with accuracy < threshold.
38. Persist WeaknessSignal records.
39. Implement Weakness Heatmap API (GET /dashboard/heatmap).

**Day 14–15: Dashboard**
40. Implement DashboardService: aggregate snapshot + heatmap + score + mission count.
41. Implement Redis caching for dashboard response.
42. Implement GET /dashboard API.
43. Implement GET /dashboard/score (score history).
44. Build frontend Performance Dashboard component.
45. Build Weakness Heatmap visualization (subject → chapter → topic severity map).

**End of Week 3 Checkpoint:**
- After test submission, student sees Performance Dashboard within 30 seconds.
- Weakness Heatmap shows chapter-level severity.
- Performance Score is visible.

### 13.5 Week 4 — Recovery System + Polish

**Goal:** Students get an action plan. System is ready for beta.

**Day 16–17: Mistake Vault**
46. Create tables: mistakes, mistake_occurrences.
47. Implement MistakeClassificationTask (root cause inference via heuristics).
48. Implement MistakeService (classify, record, detect recurrence).
49. Implement GET /mistakes API.
50. Build Mistake Vault UI: grouped by root cause, severity-ranked.

**Day 18–19: Recovery Missions**
51. Create tables: recovery_missions, mission_tasks, weak_topic_recommendations.
52. Implement MissionGenerationTask (consume heatmap + vault + score → generate missions).
53. Implement RecoveryService (create missions, enforce 3-mission cap, track completion).
54. Implement RecommendationService (generate weak topic list from heatmap).
55. Implement all Recovery APIs (GET /missions, GET /recommendations, etc.).
56. Build Recovery Missions UI.

**Day 20–21: Hardening**
57. End-to-end test of complete student journey (registration → test → dashboard → missions).
58. Load test attempt submission under concurrent users (target: 50 concurrent).
59. Fix N+1 query issues in analytics computation.
60. Add Sentry error tracking.
61. Set up CI pipeline (GitHub Actions: lint, test, migration validation).
62. Deploy to staging environment.
63. Beta test with 5–10 real students.

### 13.6 CI/CD Setup

```yaml
# GitHub Actions pipeline
on: [push]
jobs:
  test:
    - Run Alembic migrations on test DB
    - Run pytest with coverage
    - Fail if coverage < 80%
  lint:
    - ruff (Python linting)
    - mypy (type checking)
  build:
    - Docker build
    - Push to container registry
  deploy (main branch only):
    - SSH to server
    - Pull latest image
    - Run migrations
    - Restart service (zero-downtime with 2-instance rotation)
```

---

## Section 14 — README & GitHub Presentation Blueprint

### 14.1 README Structure

```markdown
# NEET Performance Operating System

> "Not a test platform. A performance intelligence system that explains 
> why a student is stuck, what is causing score loss, and what to do next."

## Why This Exists

[2-paragraph explanation of the problem: students drowning in content 
with no diagnostic intelligence, platforms showing scores without explanations]

## What It Does

| Loop Step | What Happens |
|---|---|
| Question Bank | 10,000+ tagged NEET questions with PYQ coverage |
| Test Engine | Full NEET Mock, Unit Tests, Mixed Revision with real OMR simulation |
| Attempt Tracking | Every answer event, time spent, and answer change captured |
| Performance Intelligence | Weakness Heatmap, Performance Score, Dashboard |
| Recovery System | Mistake Vault with root cause classification, Recovery Missions |

## Architecture

[Architecture diagram — Mermaid or PNG]

## Tech Stack

| Layer | Technology | Decision Rationale |
|---|---|---|
| Backend | FastAPI + Python 3.11 | Async, typed, OpenAPI auto-docs |
| Database | PostgreSQL 16 | ACID for attempt data, JSONB for analytics |
| Cache + Queue | Redis 7 + Celery | Active test state, async analytics |
| Frontend | React 18 + Vite | TanStack Query for server state |
| Auth | JWT + Argon2id | OWASP-aligned security baseline |
| Storage | Cloudflare R2 | Low-cost S3-compatible object storage |

## MVP Feature Set

[Table of 25 features with module, status, and description]

## Data Model

[ER diagram — key tables and relationships]

## API Reference

[Link to OpenAPI docs / brief summary of endpoint groups]

## Running Locally

[Docker Compose setup: postgres + redis + api + worker + frontend]

## Engineering Decisions

[3-4 key decisions with rationale: async analytics, monolith-first, 
JWT strategy, heuristic classification]

## Roadmap

Phase 1 MVP → Phase 2 Growth → Phase 3 AI Operating System
[Brief description of what each phase adds]

## What Makes This Different

[Comparison: PW/Aakash = content platforms. This = performance intelligence.
Specific feature comparisons.]
```

### 14.2 GitHub Repository Structure

```
/
├── backend/
│   ├── app/
│   │   ├── domains/
│   │   │   ├── identity/           (auth, profile, rbac)
│   │   │   ├── content/            (questions, taxonomy, import)
│   │   │   ├── assessment/         (tests, attempts, scoring)
│   │   │   ├── intelligence/       (analytics, dashboard, heatmap)
│   │   │   └── recovery/           (mistakes, missions, recommendations)
│   │   ├── shared/
│   │   │   ├── audit/
│   │   │   ├── notifications/
│   │   │   └── storage/
│   │   ├── workers/                (Celery tasks)
│   │   └── main.py
│   ├── migrations/                 (Alembic)
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── features/               (domain-aligned components)
│   │   ├── shared/                 (UI library, hooks)
│   │   └── pages/
│   └── tests/
│
├── docs/
│   ├── PROJECT_BRAIN.md
│   ├── PROJECT_STATE.md
│   ├── API_CONTRACTS.md
│   ├── DB_SCHEMA.md
│   ├── CHANGELOG.md
│   └── TASK_QUEUE.md
│
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

---

## Section 15 — Architecture Validation Review

### 15.1 Feature Coverage Matrix

| ID | Feature | Schema | API | Service | Worker | Test Plan |
|---|---|---|---|---|---|---|
| F001 | Student Registration | ✅ users, profiles | ✅ POST /auth/register | ✅ AuthService | — | ✅ |
| F002 | Login | ✅ users, sessions | ✅ POST /auth/login | ✅ AuthService, JWTService | — | ✅ |
| F003 | Profile Management | ✅ profiles | ✅ GET/PATCH /profile | ✅ ProfileService | — | ✅ |
| F005 | RBAC | ✅ roles, permissions, user_roles | ✅ RBAC middleware | ✅ RBACService | — | ✅ |
| F006 | Question Bank | ✅ questions, answer_options | ✅ GET/POST /questions | ✅ QuestionService | — | ✅ |
| F007 | Import Pipeline | ✅ (uses questions) | ✅ POST /questions/import | ✅ ImportService | ✅ import_task | ✅ |
| F008 | PYQ Database | ✅ questions (is_pyq flag) | ✅ filtered via GET /questions | ✅ QuestionService | — | ✅ |
| F009 | Question Tagging | ✅ question_tags | ✅ tags field in question API | ✅ TaxonomyService | — | ✅ |
| F010 | Subject Classification | ✅ subjects | ✅ GET /subjects | ✅ TaxonomyService | — | ✅ |
| F011 | Chapter Classification | ✅ chapters | ✅ GET /subjects/:id/chapters | ✅ TaxonomyService | — | ✅ |
| F012 | Topic Classification | ✅ topics | ✅ GET /chapters/:id/topics | ✅ TaxonomyService | — | ✅ |
| F014 | Question Search | ✅ (indexed) | ✅ GET /questions/search | ✅ QuestionService | — | ✅ |
| F016 | Full NEET Mock | ✅ tests, test_sections, test_questions | ✅ POST /tests/:id/attempts | ✅ TestEngineService | — | ✅ |
| F017 | Unit Tests | ✅ (same schema) | ✅ same attempt flow | ✅ TestEngineService | — | ✅ |
| F018 | Mixed Revision Tests | ✅ (same schema) | ✅ same attempt flow | ✅ TestEngineService | — | ✅ |
| F023 | Timer Engine | ✅ attempts.started_at, attempt_answers.time_spent | ✅ encoded in attempt answer events | ✅ AttemptService | — | ✅ |
| F024 | OMR Simulation | ✅ attempt_answers (answer_changed, marked_review) | ✅ PATCH /attempts/:id/answers | ✅ AttemptService | — | ✅ |
| F025 | Negative Marking | ✅ (scoring logic) | ✅ reflected in POST /submit result | ✅ ScoringService | — | ✅ |
| F026 | Attempt Tracking | ✅ attempts, attempt_answers | ✅ full CRUD lifecycle | ✅ AttemptService | — | ✅ |
| F027 | Performance Dashboard | ✅ performance_snapshots | ✅ GET /dashboard | ✅ DashboardService | ✅ analytics_task | ✅ |
| F028 | Weakness Heatmap | ✅ weakness_signals, topic_analytics | ✅ GET /dashboard/heatmap | ✅ HeatmapService | ✅ weakness_task | ✅ |
| F031 | Performance Score | ✅ performance_snapshots (score field) | ✅ GET /dashboard/score | ✅ ScoreService | ✅ analytics_task | ✅ |
| F044 | Mistake Vault | ✅ mistakes, mistake_occurrences | ✅ GET /mistakes | ✅ MistakeService | ✅ classification_task | ✅ |
| F045 | Recovery Missions | ✅ recovery_missions, mission_tasks | ✅ GET/POST /missions | ✅ RecoveryService | ✅ mission_task | ✅ |
| F047 | Weak Topic Recs | ✅ (derived from weakness_signals) | ✅ GET /recommendations | ✅ RecommendationService | — | ✅ |

**Coverage Result: 25/25 features covered. ✅**

### 15.2 Gap Analysis

**No gaps identified in the 25 MVP features.** All features have:
- A corresponding schema design
- At least one API endpoint
- A service layer owner
- A test plan entry

**Identified design risks (not gaps, but requiring attention):**

1. **Root cause classification accuracy:** The heuristic rules (time_spent < 20s → Guessing) are proxies. They will produce some incorrect classifications. This is acceptable at MVP. The system should expose a "Dismiss / Reclassify" option in the Mistake Vault UI so students can correct the classification, which also creates a feedback dataset for future ML improvement.

2. **PerformanceScore formula lock:** The composite score formula must be defined and locked before first deployment. Changing it retroactively invalidates historical scores. Decision: lock the formula in a configuration table, version it, and never change existing scores — only compute new scores with the new formula.

3. **Mission generation cold start:** A student who has taken only one test has sparse data for mission generation. The system should generate limited, high-confidence missions (1 instead of 3) for students with < 3 test attempts, rather than generating missions from insufficient signal.

4. **Import pipeline error handling:** The bulk import task must handle file encoding issues (non-UTF-8 CSVs from Excel), malformed question text (embedded HTML, broken unicode), and question count limits per import (recommend cap at 1,000 per batch at MVP).

### 15.3 Risk Summary

| Risk | Severity | Probability | Mitigation |
|---|---|---|---|
| F026 implementation bug causes data loss | Critical | Medium | Extensive integration tests, duplicate submission protection, Redis backup of active state |
| AttemptAnswer table unindexed → slow analytics | High | High | Indexes defined in schema from Day 1 |
| ScoringService race condition on concurrent submits | High | Low | Idempotency key on attempt submission |
| Celery worker crash during analytics computation | Medium | Medium | Celery retry policy (3 retries, exponential backoff); analytics are idempotent (recomputing gives same result) |
| Mission generation produces irrelevant missions | Medium | High | Confidence score on missions; allow student dismissal |
| Root cause classification is inaccurate | Low | High | Acceptable at MVP; student feedback loop planned |
| Import pipeline fails on malformed file | Low | Medium | Per-row error reporting; partial success acceptable |

### 15.4 Readiness Assessment

| Dimension | MVP Readiness | Assessment |
|---|---|---|
| Architecture | Fully designed | Ready to implement |
| Data schema | Complete for all 25 features | Ready to implement |
| API contracts | Defined for all critical paths | Ready to implement |
| Dependency order | Fully mapped, no circular dependencies | Ready to implement |
| Tech stack | Confirmed (FastAPI, PostgreSQL, Redis, Celery, React) | Ready to implement |
| Risk identification | Complete | Mitigations defined |
| Implementation roadmap | 4-week sprint, 21-day sequenced | Ready to execute |
| AI development memory | 6 document system defined | Ready to set up |
| GitHub structure | Defined | Ready to scaffold |
| Validation coverage | 25/25 features | Complete |

**Overall Readiness: IMPLEMENTATION READY.**

The system architecture is coherent, the dependencies are correctly ordered, the schemas support all 25 MVP features, and the roadmap is sequenced for solo-founder execution. The most important implementation principle is: **build F026 (Attempt Tracking) as if everything depends on it, because everything does.**

---

*Document generated from: MODULE_1_Authentication, MODULE_2_Question_System, module_3_test_engine_mvp1, Module_4_Performance_Intelligence, Module_6_Recovery_System, MVP_first_version, 78_features, categorized_features, ful_features_ideas, how_to_do_project.*  
*Source priority applied per specification. All inferred facts are explicitly labeled.*
