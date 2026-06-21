# TASK_QUEUE.md

## Purpose
Defines the strict implementation execution order. Only one active task may exist at a time.

## Queue Rules
* Complete current task before activating next task.
* Do not skip dependencies.
* Source code must pass tests before marking Complete.
* Update memory files after every completed task.

---

## Completed Tasks
* **TASK-000:** Infrastructure Setup (Alembic, Asyncpg, Pytest NullPool)
* **TASK-001:** F001 Registration (Argon2id hashing thread-offload)
* **TASK-002:** F002 Login & JWT Authentication (Redis rate limiting)
* **TASK-003:** F003 Profile Management
* **TASK-004:** F005 RBAC (Role-Based Access Control)
* **TASK-005:** F010 Subjects (CRUD, RBAC, Audit)

---

## Current Active Task

### TASK-006: F011 Chapters
**Priority:** P1  
**Status:** In Progress  
**Dependencies:** TASK-005 Complete (Subjects exist to attach Chapters to)

---

## Upcoming Tasks (Sequential)
* **TASK-007:** F012 Topics
* **TASK-008:** Frontend Integration Check (Auth & Taxonomy)
* **TASK-009:** F006 Question Bank Models & CRUD
* **TASK-010:** F008 Question Import Pipeline
* **TASK-011:** F016 Assessment Engine Models
* **TASK-012:** F026 Attempt Tracking & State Management
* **TASK-013:** F029 Analytics Pipeline Base# TASK QUEUE

## Completed Tasks
- ✅ Init FastAPI backend & Vite frontend.
- ✅ Implement `AuthService` with Argon2 and Redis JWT rotation.
- ✅ Implement `RBACService` with fast permission evaluations.
- ✅ Build Alembic Migrations `001`, `002`, `003`.
- ✅ Build Subject CRUD endpoints (`app/domains/content/routes/subjects.py`).
- ✅ Build Frontend Auth flow and API client (`authStore.ts`, `api/client.ts`).
- ✅ Build Frontend Subjects UI (`SubjectsPage.tsx`).
- ✅ Add comprehensive Pytest coverage.

## Current Active Task
- 🔄 **BACKEND-015:** Expand `backend/app/domains/content/models.py` to include `Chapter` and `Topic` models linked to `Subject`.

## Next Immediate Tasks (Up Next)
1. **BACKEND-016:** Create Alembic Migration `004_taxonomy` for Chapters and Topics.
2. **BACKEND-017:** Implement CRUD repositories, schemas, and routes for Chapters (`/api/v1/chapters`).
3. **BACKEND-018:** Implement CRUD repositories, schemas, and routes for Topics (`/api/v1/topics`).
4. **FRONTEND-013:** Create Taxonomy Management Page for Teachers/Admins to manage Chapters/Topics.

## Backlog / Technical Debt
- **DEBT-001:** Remove MVP auto-verify in `auth_service.py` (`user.email_verified = True`) and wire up Celery email tasks.
- **DEBT-002:** Add frontend unit tests (Vitest/React Testing Library) to match backend coverage.