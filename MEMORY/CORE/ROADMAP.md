# ROADMAP.md

## Project: NEET Performance Operating System (NEET POS)
**Goal:** 25-Feature MVP

---

### Milestone 1: Infrastructure Foundation (COMPLETE)
* [x] FastAPI / SQLAlchemy 2.0 Async setup
* [x] PostgreSQL & Redis Dockerization
* [x] Pytest configuration with async support
* [x] Alembic migration pipeline

### Milestone 2: Identity & Access Management (COMPLETE)
* [x] User Entity & Registration (F001)
* [x] Authentication & JWT Flow (F002)
* [x] Profile CRUD (F003)
* [x] RBAC Implementation (F005)
* [x] Security Audit Logging

### Milestone 3: Content Taxonomy (CURRENT)
* [x] Subjects Engine (F010)
* [ ] Chapters Engine (F011) **<- WE ARE HERE**
* [ ] Topics Engine (F012)

### Milestone 4: Question Management (NEXT)
* [ ] Question CRUD & Models (F006)
* [ ] Question Approval Workflow (F007)
* [ ] Question Bulk Import Pipeline (F008)

### Milestone 5: Assessment Engine (CORE MVP)
* [ ] Mock Test Creation & Assignment (F016)
* [ ] Secure Timer Engine
* [ ] Attempt Tracking & State Management (F026)

### Milestone 6: Intelligence & Analytics
* [ ] Dashboard Aggregation (F027)
* [ ] Analytics Pipeline (F029)
* [ ] Mistake Vault (F044)

### Milestone 7: Frontend Integration
* [ ] React + Vite Routing
* [ ] Auth UI (Login/Register)
* [ ] Dashboard UI
* [ ] Mock Test Execution UI

---

## Critical Path
F011 Chapters -> F012 Topics -> F006 Question Bank -> F016 Assessment Engine
# ROADMAP

## Phase 1: Foundation & Identity (COMPLETED)
- [x] Repository setup (Mono-repo style).
- [x] Database Configuration (Async SQLAlchemy, PostgreSQL).
- [x] Redis Integration for caching and auth state.
- [x] Frontend Setup (Vite, React, Tailwind).
- [x] User Authentication API (Argon2, JWT, HttpOnly Cookies).
- [x] Profile Management API (Target year, Target score).
- [x] Role-Based Access Control (RBAC) scaffolding.
- [x] Frontend Auth screens & Protected Routing.
- [x] Core Backend Test Suite creation.

## Phase 2: Core Domain & Content Taxomony (IN PROGRESS)
- [x] Backend: Subjects CRUD & API (`003_subjects` migration).
- [x] Frontend: Subjects dashboard interface (`SubjectsPage.tsx`).
- [ ] Backend: Chapters & Topics Models and API.
- [ ] Frontend: Taxonomy browsing interface (Chapters/Topics).
- [ ] Backend: Question Bank Models (MCQ, Assertion/Reason).
- [ ] Frontend: Question Entry Interface (Teacher Role).

## Phase 3: Testing Engine & Exam Emulation (PLANNED)
- [ ] Backend: Test Generation logic (Randomized, Subject-wise, Full Mock).
- [ ] Backend: Test Session tracking (Time, Answers, State).
- [ ] Frontend: Exam UI (Timer, Question Palette, Mark-for-review).
- [ ] Backend: Auto-grading and score calculation.

## Phase 4: Analytics & Insights (PLANNED)
- [ ] Backend: Weakness analysis (Chapter-wise accuracy).
- [ ] Frontend: Student Analytics Dashboard (Charts, Progression graphs).

## Phase 5: Production Readiness (PLANNED)
- [ ] SMTP Integration (Replace auto-verify with Celery email tasks).
- [ ] Load Testing.
- [ ] CI/CD Pipeline finalized.