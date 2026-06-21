# NEET Performance Operating System — Frontend Dependency Gap Report

**Document Type:** Implementation-Grade Frontend Gap Analysis  
**Source:** NEET_POS_Engineering_Blueprint.md (Single source of truth)  
**Analyst Role:** Senior Frontend Systems Designer & Backend-Frontend Integration Analyst  
**Scope:** All 25 MVP features — F001 through F047  
**Date:** 2026-06-19

---

## Table of Contents

1. Executive Summary  
2. Gap Analysis by Layer  
3. Feature-by-Feature Gap Table  
4. Screen Mapping Matrix  
5. Integration Flow Map  
6. Missing Gap List  
7. Recommended Blueprint Section: Frontend Dependency Architecture  
8. Implementation Order  
9. Implementation Readiness Verdict  

---

## 1. EXECUTIVE SUMMARY

### Overall Coverage Score: 3.5 / 10

### Coverage Interpretation

The blueprint is a backend-complete, frontend-skeletal document: all 25 features have schema, service, and API definitions, but the frontend side consists of name-drops of technologies and a handful of lifecycle prose paragraphs rather than a developer-executable specification.

### Main Strengths of the Blueprint

- **Backend architecture is production-grade and complete.** Schema, indexes, services, repositories, and API contracts are defined for all 25 features. A backend developer can start coding on day one.
- **End-to-end workflow prose (Section 9) is the single most useful frontend artifact in the document.** Steps 1–12 of the student journey provide a concrete event narrative that a frontend developer can trace.
- **Technology selections are confirmed and appropriate.** React 18 + Vite + TanStack Query + Zustand + React Router v6 is a coherent stack. The auth flow (JWT in memory, httpOnly cookie, Axios interceptor) is correctly specified in Section 6.3.
- **State management roles are split correctly.** The blueprint explicitly assigns server state to TanStack Query and client state (active test session) to Zustand.
- **API error codes are standardized** (Section 8.7) — frontend error handling can map directly to these codes.

### Main Missing Gaps

1. **No screen inventory exists.** The blueprint never lists what screens/pages the frontend contains, what routes they live on, or what components compose them.
2. **No component specification exists.** Individual React components — their props, internal state, event handlers, and conditional render branches — are completely absent.
3. **No query/mutation hook layer is defined.** TanStack Query hooks are mentioned by name but never specified: no queryKey patterns, no stale time decisions, no mutation handlers, no cache invalidation logic.
4. **Visualization specifications are absent.** The Weakness Heatmap (F028), Performance Score history chart (F031), and improvement trend (F027) are described semantically but have zero rendering specifications: no chart type, no axis definitions, no color-to-severity mapping, no library choice, no responsive behavior.
5. **Loading, error, and empty states are completely unspecified** for every single screen and every API interaction. The blueprint defines backend error codes but never connects them to UI behavior.
6. **The async analytics gap (post-submission) has no frontend resolution.** The blueprint states analytics are computed asynchronously (10–30 seconds). No polling mechanism, WebSocket, or pending state is defined on the frontend side.

### Why These Gaps Matter for Implementation Risk

A backend developer reading this blueprint can begin implementation immediately. A frontend developer reading this blueprint cannot: they do not know what screens to create, what components to build, how those components map to API endpoints, what the query layer looks like, how to handle loading and error states, or what the visualizations should render. Every frontend implementation decision must be invented, creating maximum implementation divergence risk in a solo-founder context where undocumented decisions become invisible technical debt.

### Top 5 Highest-Priority Gaps

| Priority | Gap | Affected Features | Risk |
|---|---|---|---|
| 1 | Screen inventory and route map undefined | All 25 features | Critical |
| 2 | Weakness Heatmap visualization unspecified | F028 | Critical |
| 3 | Async analytics polling/resolution undefined | F027, F028, F031 | Critical |
| 4 | TanStack Query hook layer not defined | All API-consuming features | High |
| 5 | Loading / error / empty states missing across all screens | All 25 features | High |

---

## 2. GAP ANALYSIS BY LAYER

### A. Backend Dependency Coverage — PRESENT

All 25 features have:
- A defined database schema
- At least one API endpoint with input/output documented
- A service layer owner
- Background worker assignment where async computation is required

**What is complete:** Schema, indexes, service interfaces, repository interfaces, API contracts for auth, question, test, analytics, and recovery domains. Error code standards. Rate limiting definitions. Caching strategy (keys, TTLs). Background worker task chain.

**What is incomplete:** The `subject_analytics` and `chapter_analytics` tables are mentioned in the entity diagram (Section 7.1) and analytics computation workflow (Section 9, Step 8) but their SQL schemas are never provided, only `topic_analytics` is defined in Section 7.2. The `mistake_occurrences` and `mistake_patterns` tables are referenced in the schema diagram and implementation roadmap (Step 46) but their column definitions are absent from Section 7.2. The `weak_topic_recommendations` table is referenced in the ER diagram but has no schema definition anywhere in the blueprint.

### B. Frontend Screen Dependency Coverage — MISSING

**Evidence:** Section 6.3 (Frontend Architecture) contains 12 lines covering the technology stack, state split, auth flow, and test session lifecycle. No screen is named. No route is specified. Section 13 (Implementation Roadmap) mentions "Build frontend Performance Dashboard component" (Step 44), "Build Weakness Heatmap visualization" (Step 45), "Build Mistake Vault UI" (Step 50), and "Build Recovery Missions UI" (Step 56) — all as single-line items with no decomposition.

**Verdict:** The blueprint never produces a screen inventory. A developer implementing the frontend must invent all screen names, all routes, all page structures, and all navigation flows from scratch.

### C. UI Component Dependency Coverage — MISSING

**Evidence:** Zero React components are named or specified anywhere in the blueprint. The frontend directory structure in Section 14.2 references `features/` (domain-aligned components) and `shared/` (UI library, hooks) as folder labels, with no contents listed.

**Verdict:** No component tree, no component props, no component-to-feature mapping, no component-to-API mapping exists. A developer cannot derive a component inventory from the blueprint.

### D. Visualization Dependency Coverage — MISSING

**Evidence:** Section 9.1 Step 12 describes the dashboard as showing: "Weakness Heatmap: Genetics 🔴, Thermodynamics 🔴, Organic Chemistry 🟡" — this is the most specific visualization description in the entire document. Section 5.1 states the Heatmap "shows subject → chapter → topic severity ratings." The Performance Score history and improvement trend are mentioned in the dashboard API output description ("improvement_trend: last 5 tests"). No chart type, no chart library, no axis definitions, no color mapping, no responsive constraints, no drill-down interaction, no empty-state rendering is specified for any visualization.

**Verdict:** All three primary visualizations (Heatmap, Score History, Improvement Trend) require full visualization specifications before implementation can begin.

### E. Backend → Frontend Integration Coverage — PARTIALLY PRESENT

**What is present:** The auth flow integration (Section 6.3) is specified: token storage location, Axios interceptor behavior on 401, refresh failure redirect. The test session lifecycle (Section 6.3, steps 1–5) describes the sequence from test start to result redirect. The Module Interaction Flow (Section 6.4) narrates the backend async chain.

**What is missing:** For every other feature group (Question System, Profile, Recovery, Dashboard), the integration path from API response to React component render is completely absent. No query hook patterns. No cache invalidation triggers. No mutation success/error handlers. No optimistic update logic for answer saving during a live test.

### F. State Management Coverage — PARTIALLY PRESENT

**What is present:** The blueprint names Zustand for client state (active test session) and TanStack Query for server state. Auth state placement is correctly specified: access token in Zustand memory, refresh token in httpOnly cookie.

**What is missing:**
- The Zustand store schema for active test state is never defined. What fields does it contain? `currentQuestionIndex`, `answers: Map<questionId, optionId>`, `timeRemaining`, `reviewFlags: Set<questionId>`? None of this is specified.
- TanStack Query key patterns are never defined. Without agreed `queryKey` patterns, cache sharing, invalidation, and prefetching cannot be consistently implemented.
- Cache invalidation triggers are absent. When the student submits a test, which queries are invalidated? When a mission task is completed, which queries refetch?
- No global error state is defined (how are network errors surfaced to the user?).
- No auth state hydration strategy on page reload is defined (how does Zustand reload the access token if the page refreshes?).

### G. API Contract Coverage — PARTIALLY PRESENT

**What is present:** HTTP method, endpoint path, auth requirement, and a description for every endpoint. For critical endpoints (login, test start, answer save, submission), request body and response body schemas are documented. Edge cases for critical endpoints are listed.

**What is missing:**
- Full response schemas for GET /api/v1/dashboard, GET /api/v1/dashboard/heatmap, GET /api/v1/missions/:id, GET /api/v1/mistakes, GET /api/v1/recommendations are absent. The dashboard endpoint output lists field names in prose ("current_performance_score, last_attempt_summary, top_weaknesses") but no JSON structure, no field types, no nested object definitions.
- GET /api/v1/attempts/:id/result is listed in the endpoint table but has no detail block — request/response schema, edge cases, and business logic are undefined.
- Pagination response envelope schema is not specified (beyond mentioning cursor-based pagination exists).
- The polling endpoint for async analytics status (the blueprint implies the frontend must poll for analytics completion, but no polling endpoint is defined beyond the import polling pattern in F007).

### H. Error / Loading / Empty-State Coverage — MISSING

**Evidence:** Section 8.7 defines HTTP status codes and error code strings. This is the entirety of error handling specification visible to the frontend. No screen-level or component-level handling is described anywhere.

**Specific absences:**
- No loading skeleton or spinner specification for any screen
- No error message copy for any error code
- No empty-state design for any list (no mistakes yet, no missions yet, no tests yet)
- No handling for the `analytics_status: "computing"` state returned by submission
- No retry behavior on network failure during test execution (answer save PATCH)
- No handling for browser crash recovery (the blueprint says state is saved to localStorage and Redis, but the frontend workflow for restoring that state on reload is unspecified)

### I. Feature-by-Feature Execution Coverage — PARTIALLY PRESENT

**What is present:** The end-to-end execution workflow (Section 9) provides a step-by-step narrative for the primary student journey. The recovery mission execution workflow (Section 9.2) provides a simplified sequence. Section 13 provides a backend-first 21-day implementation roadmap.

**What is missing:** The execution workflow is narrated from a backend-event perspective. It does not specify what the frontend renders at each step, what user interactions are possible, what state changes occur in the Zustand or TanStack Query layer, or what the user sees during transition states. The workflow describes server events; it does not describe UI states.

---

## 3. FEATURE-BY-FEATURE GAP TABLE

| Feature ID | Feature Name | Score /10 | Backend Dep | Frontend Screen | UI Components | Integration | Visualization | Primary Gaps | Impl. Risk | Fix Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| **F001** | Student Registration | 5/10 | PRESENT | MISSING | MISSING | PARTIALLY PRESENT | N/A | Screen layout, form validation UI, email-verified gate, error state for 409/rate-limit | Medium | P1 |
| **F002** | Login | 5/10 | PRESENT | MISSING | MISSING | PRESENT | N/A | Screen layout, remember-me behavior, failed-login feedback, 401 retry interceptor integration | Medium | P1 |
| **F003** | Profile Management | 4/10 | PRESENT | MISSING | MISSING | PARTIALLY PRESENT | N/A | Profile screen, editable field list, save/cancel flow, success toast, what fields are displayed vs editable | Medium | P2 |
| **F005** | RBAC | 6/10 | PRESENT | No dedicated screen needed (middleware concern) | MISSING | PARTIALLY PRESENT | N/A | Role-gated route guards in React Router, RBAC-aware nav rendering (hide Teacher/Admin items from Student) | Low | P2 |
| **F006** | Question Bank | 3/10 | PRESENT | MISSING | MISSING | MISSING | N/A | Admin/Teacher-only screen, question list with filter UI, question detail view, status workflow UI (Draft→Published), create/edit form | High | P1 |
| **F007** | Import Pipeline | 4/10 | PRESENT | MISSING | MISSING | PARTIALLY PRESENT | N/A | Upload UI, progress indicator, polling for import status, per-row error report display | High | P2 |
| **F008** | PYQ Database | 3/10 | PRESENT | MISSING | MISSING | MISSING | N/A | PYQ filter in question list, PYQ badge in test UI, no dedicated screen needed beyond filter | Medium | P2 |
| **F009** | Question Tagging | 3/10 | PRESENT | No dedicated screen needed | MISSING | MISSING | N/A | Tag input component in question create/edit form, tag filter in question search | Low | P3 |
| **F010** | Subject Classification | 4/10 | PRESENT | No dedicated screen needed | MISSING | MISSING | N/A | Subject selector component (used across test creation, question form, dashboard filter) | Low | P3 |
| **F011** | Chapter Classification | 4/10 | PRESENT | No dedicated screen needed | MISSING | MISSING | N/A | Cascading chapter selector dependent on subject selection | Low | P3 |
| **F012** | Topic Classification | 4/10 | PRESENT | No dedicated screen needed | MISSING | MISSING | N/A | Cascading topic selector dependent on chapter selection | Low | P3 |
| **F014** | Question Search | 3/10 | PRESENT | MISSING | MISSING | MISSING | N/A | Search input, filter panel (subject/chapter/topic/difficulty/PYQ), result list, no detail on result click behavior | Medium | P2 |
| **F016** | Full NEET Mock | 4/10 | PRESENT | MISSING | MISSING | PARTIALLY PRESENT | N/A | Test listing screen, test detail screen, test interface (OMR layout, section tabs, question navigator), timer display, auto-submit behavior | Critical | P0 |
| **F017** | Unit Tests | 4/10 | PRESENT | MISSING | MISSING | PARTIALLY PRESENT | N/A | Same as F016 with configurable section UI | High | P0 |
| **F018** | Mixed Revision Tests | 4/10 | PRESENT | MISSING | MISSING | PARTIALLY PRESENT | N/A | Same as F016 with multi-chapter selector | High | P0 |
| **F023** | Timer Engine | 3/10 | PRESENT | No dedicated screen | MISSING | PARTIALLY PRESENT | N/A | Timer component spec: countdown display format, warning states (<10 min, <1 min), auto-submit trigger | Critical | P0 |
| **F024** | OMR Simulation | 2/10 | PRESENT | No dedicated screen | MISSING | PARTIALLY PRESENT | N/A | OMR answer grid component spec: 4-option bubble UI, review flag toggle, answer-change visual feedback, no pencil-and-paper fidelity guidance | Critical | P0 |
| **F025** | Negative Marking | 5/10 | PRESENT | No dedicated screen | MISSING | PARTIALLY PRESENT | N/A | Score display breakdown component: +4/-1/0 explained in result UI, confirmation dialog for negative-risk answers | Medium | P1 |
| **F026** | Attempt Tracking | 3/10 | PRESENT | No dedicated screen | MISSING | PARTIALLY PRESENT | N/A | Zustand store schema for active attempt state, debounce/batch answer sync logic, localStorage backup format, browser crash recovery flow | Critical | P0 |
| **F027** | Performance Dashboard | 2/10 | PRESENT | MISSING | MISSING | MISSING | MISSING | Dashboard screen layout, component decomposition, polling for async analytics, all visualization specs, improvement trend chart spec | Critical | P0 |
| **F028** | Weakness Heatmap | 1/10 | PRESENT | MISSING | MISSING | MISSING | MISSING | Heatmap visualization type, subject→chapter→topic drill-down interaction, severity color mapping, empty state (no data yet), chart library choice | Critical | P0 |
| **F031** | Performance Score | 2/10 | PRESENT | MISSING | MISSING | MISSING | MISSING | Score display component, score history chart spec (axis: attempts vs score, trend line), composite breakdown display | Critical | P0 |
| **F044** | Mistake Vault | 2/10 | PRESENT | MISSING | MISSING | MISSING | N/A | Vault screen, grouping UI (by root cause), severity ordering, reclassify action (mentioned in blueprint as a design risk), recurrence badge | High | P1 |
| **F045** | Recovery Missions | 2/10 | PRESENT | MISSING | MISSING | MISSING | N/A | Mission list screen, mission detail screen, task completion flow, mission completion confirmation, dismiss action, 3-mission cap indicator | High | P1 |
| **F047** | Weak Topic Recs | 3/10 | PRESENT | MISSING | MISSING | MISSING | N/A | Recommendation list component (where does it live: dashboard panel or separate screen?), mark-leakage ranking display | Medium | P1 |

---

## 4. SCREEN MAPPING MATRIX

The following matrix maps every required frontend screen (derived from blueprint evidence) to its components, API endpoints, state hooks, and required handling. Screens marked **[not in blueprint]** are derived from functional requirements in Section 5.1 — they are implied but never explicitly listed.

### Screen 1: Registration Page `/register` — F001

| Dimension | Specification |
|---|---|
| **UI Components** | EmailInput, PasswordInput, NameInput, GradeSelect, TargetYearInput, SubmitButton, FormErrorMessage |
| **API Endpoint** | POST /api/v1/auth/register |
| **State (TanStack)** | `useMutation` — registerMutation |
| **State (Zustand)** | None — unauthenticated screen |
| **Loading State** | Button spinner during mutation |
| **Error State** | Inline field error for 400 VALIDATION_ERROR; toast for 409 CONFLICT (duplicate email); rate-limit message for 429 |
| **Empty State** | N/A |
| **Success Flow** | Redirect to `/verify-email-sent` confirmation screen |
| **Missing From Blueprint** | Screen name, route, component list, success redirect target, field validation rules (client-side), error message copy |

### Screen 2: Email Verification Confirmation `/verify-email-sent` — F001

| Dimension | Specification |
|---|---|
| **UI Components** | InstructionText, ResendEmailButton |
| **API Endpoint** | POST /api/v1/auth/verify-email (triggered by link in email, not by this screen) |
| **Missing From Blueprint** | This screen is never mentioned. The blueprint specifies the verification API but not the post-registration UX. |

### Screen 3: Login Page `/login` — F002

| Dimension | Specification |
|---|---|
| **UI Components** | EmailInput, PasswordInput, SubmitButton, ForgotPasswordLink [implied], FormErrorMessage |
| **API Endpoint** | POST /api/v1/auth/login |
| **State (TanStack)** | `useMutation` — loginMutation |
| **State (Zustand)** | On success: write access_token to authStore |
| **Loading State** | Button spinner |
| **Error State** | "Invalid credentials" for 401; "Email not verified" gate; "Account locked" for repeated failures |
| **Empty State** | N/A |
| **Success Flow** | Redirect to `/dashboard` |
| **Missing From Blueprint** | Screen route, redirect-after-login logic, forgot-password screen (not in MVP scope but UX gap), email-not-verified state display |

### Screen 4: Profile Page `/profile` — F003

| Dimension | Specification |
|---|---|
| **UI Components** | ProfileForm (first_name, last_name, target_score, target_year, avatar_url, notification_prefs), SaveButton, AvatarUploader [implied by avatar_url field] |
| **API Endpoints** | GET /api/v1/profile (load), PATCH /api/v1/profile (save) |
| **State (TanStack)** | `useQuery` — profileQuery; `useMutation` — updateProfileMutation |
| **Loading State** | Skeleton on initial load |
| **Error State** | Validation errors on PATCH 400 |
| **Success Flow** | Success toast "Profile updated" |
| **Missing From Blueprint** | Which fields are displayed (all columns? subset?), notification_prefs field structure (it is a JSONB blob — what UI does it render?), avatar upload endpoint (none specified in API section), whether profile data feeds into any visible personalization on dashboard |

### Screen 5: Test Listing Page `/tests` — F016, F017, F018

| Dimension | Specification |
|---|---|
| **UI Components** | TestCard (title, test_type, duration_mins, total_marks, status), TestTypeFilter, StartTestButton |
| **API Endpoint** | GET /api/v1/tests |
| **State (TanStack)** | `useQuery` — testsQuery |
| **Loading State** | Skeleton cards |
| **Error State** | "Failed to load tests" with retry |
| **Empty State** | "No tests available" |
| **Success Flow** | Click → navigate to `/tests/:id` |
| **Missing From Blueprint** | Route defined, endpoint defined — but screen layout, card design, test_type badge display, "in progress" resume state (if student has an existing active attempt for this test) are absent |

### Screen 6: Test Detail / Pre-Start Page `/tests/:id` — F016, F017, F018

| Dimension | Specification |
|---|---|
| **UI Components** | TestInfoPanel (sections, question count, duration), InstructionsText, StartTestButton |
| **API Endpoint** | GET /api/v1/tests/:id |
| **State (TanStack)** | `useQuery` — testDetailQuery |
| **Loading State** | Skeleton |
| **Success Flow** | "Start Test" → POST /tests/:id/attempts → navigate to `/tests/:id/attempt/:attemptId` |
| **Missing From Blueprint** | This pre-start screen is never mentioned. The blueprint goes directly from test listing to attempt start without a detail/instruction page. |

### Screen 7: Active Test Interface `/tests/:id/attempt/:attemptId` — F016, F017, F018, F023, F024, F025, F026 [MOST COMPLEX SCREEN]

| Dimension | Specification |
|---|---|
| **UI Components** | QuestionPanel, AnswerOptionGrid (OMR bubbles), QuestionNavigator (grid of 180 question numbers), SectionTabBar, TimerDisplay, ReviewFlagToggle, SaveAndNextButton, SubmitTestButton |
| **API Endpoints** | GET /api/v1/attempts/:id (initial load / crash recovery); PATCH /api/v1/attempts/:id/answers (debounced batch save); POST /api/v1/attempts/:id/submit |
| **State (Zustand)** | activeTestStore: { attemptId, questions[], currentQuestionIndex, answers: {questionId: optionId}, reviewFlags: Set, timeRemaining, startedAt, syncStatus } |
| **State (TanStack)** | None during active test (Zustand owns all test state); `useMutation` — submitAttemptMutation |
| **Loading State** | Full-screen loader on initial question load |
| **Error State** | Answer sync failure → silent retry queue (no disruptive error during active test); submit failure → blocking error with retry |
| **Empty State** | N/A |
| **Timer Behavior** | Countdown; warning at 10 min and 1 min; auto-submit at 0 |
| **Success Flow** | Submit → navigate to `/attempts/:id/result` |
| **Missing From Blueprint** | OMR layout specification (column vs grid vs scrolling list), question navigation panel layout, section switching behavior, review flag visual state, per-question timer display (is it shown?), what happens when PATCH /answers returns 401 mid-test (token refresh during active test), Zustand store field schema, localStorage backup format, crash-recovery UI flow (how does the student know state was recovered?) |

### Screen 8: Test Result / Score Page `/attempts/:id/result` — F025, F026

| Dimension | Specification |
|---|---|
| **UI Components** | ScoreSummaryCard (total_score, correct, incorrect, unattempted), AnalyticsStatusIndicator (pending / ready), NavigateToDashboardButton |
| **API Endpoint** | GET /api/v1/attempts/:id/result |
| **State (TanStack)** | `useQuery` — attemptResultQuery |
| **Loading State** | Score shown immediately (from submit response); analytics pending indicator |
| **Analytics Async Gap** | Blueprint states analytics take 10–30 seconds. Frontend must show "Analyzing your test..." state and either poll or redirect. No polling endpoint is defined for this use case. |
| **Missing From Blueprint** | GET /api/v1/attempts/:id/result response schema is completely absent; analytics readiness polling mechanism; what is shown before analytics complete; transition to full dashboard |

### Screen 9: Performance Dashboard `/dashboard` — F027, F028, F031, F047

| Dimension | Specification |
|---|---|
| **UI Components** | PerformanceScoreWidget, WeaknessHeatmap, ImprovementTrendChart, RecentMissionsPanel, WeakTopicRecommendationList, AttemptHistorySummary |
| **API Endpoints** | GET /api/v1/dashboard; GET /api/v1/dashboard/heatmap; GET /api/v1/dashboard/score; GET /api/v1/dashboard/attempts |
| **State (TanStack)** | `useQuery` — dashboardQuery (staleTime: 5 min); heatmapQuery; scoreHistoryQuery; attemptsQuery |
| **Loading State** | Per-widget skeleton (staggered) |
| **Error State** | Per-widget error with retry |
| **Empty State** | "Take your first test to see your dashboard" (no attempt data yet) |
| **Missing From Blueprint** | All visualization specs (see Section 6D); response JSON schema for GET /dashboard and GET /dashboard/heatmap; layout of dashboard panels (single column, grid?); whether heatmap and score are on same page or separate routes; drill-down behavior from heatmap to mistake vault |

### Screen 10: Attempt History Page `/dashboard/attempts` — F027

| Dimension | Specification |
|---|---|
| **UI Components** | AttemptHistoryTable (date, test_name, score, correct, incorrect), PaginationControls |
| **API Endpoint** | GET /api/v1/dashboard/attempts |
| **State (TanStack)** | `useQuery` — attemptsHistoryQuery (cursor paginated) |
| **Empty State** | "No attempts yet" |
| **Missing From Blueprint** | Whether this is a separate page or a dashboard tab; pagination UI; click-to-attempt-detail behavior |

### Screen 11: Single Attempt Analytics `/dashboard/attempts/:id` — F027

| Dimension | Specification |
|---|---|
| **UI Components** | AttemptBreakdownPanel, TopicAccuracyTable, QuestionReviewList |
| **API Endpoint** | GET /api/v1/dashboard/attempts/:id |
| **Missing From Blueprint** | Response schema for this endpoint; what analytics are shown per-attempt; whether question review (with explanation display) is in scope for MVP |

### Screen 12: Mistake Vault `/mistakes` — F044

| Dimension | Specification |
|---|---|
| **UI Components** | MistakeFilterBar (by root_cause, by severity), MistakeCard (question_text, root_cause badge, recurrence_count, severity), PatternSummaryPanel |
| **API Endpoints** | GET /api/v1/mistakes; GET /api/v1/mistakes/patterns |
| **State (TanStack)** | `useQuery` — mistakesQuery; mistakePatternsQuery |
| **Loading State** | Skeleton list |
| **Empty State** | "No mistakes tracked yet. Complete a test to populate your Mistake Vault." |
| **Reclassify Action** | Blueprint Section 15.2 explicitly mentions a "Dismiss / Reclassify" option — no API endpoint exists for this action |
| **Missing From Blueprint** | Reclassify API endpoint absent; response schema for GET /mistakes; whether individual mistake drill-down (to original question) is in MVP scope |

### Screen 13: Recovery Missions `/missions` — F045

| Dimension | Specification |
|---|---|
| **UI Components** | MissionCard (title, trigger_source, expected_gain, priority_score, status), MissionCountIndicator (X/3 active), StartMissionButton |
| **API Endpoints** | GET /api/v1/missions; POST /api/v1/missions/:id/start |
| **State (TanStack)** | `useQuery` — missionsQuery; `useMutation` — startMissionMutation |
| **Loading State** | Skeleton |
| **Empty State** | "No active missions. Complete a test to generate your first recovery plan." |
| **Missing From Blueprint** | Mission list response schema; how missions are sorted by priority_score in the UI; dismiss action UI and confirmation |

### Screen 14: Mission Detail `/missions/:id` — F045

| Dimension | Specification |
|---|---|
| **UI Components** | MissionHeader, TaskList (TaskItem: task_type, description, topic_link, status toggle), CompleteMissionButton |
| **API Endpoints** | GET /api/v1/missions/:id; PATCH /api/v1/missions/:id/tasks/:tid; POST /api/v1/missions/:id/complete |
| **State (TanStack)** | `useQuery` — missionDetailQuery; `useMutation` — completeTaskMutation, completeMissionMutation |
| **Success Flow** | All tasks complete → CompleteMissionButton enabled → POST complete → mission archived → return to /missions |
| **Missing From Blueprint** | Mission detail response schema; how "revise_topic" task type links to any content (no content system exists in MVP); how "retry_questions" task type links to a practice set (no dedicated endpoint for this) |

### Screen 15: Question Bank Admin `/admin/questions` — F006, F007, F008, F009, F014

| Dimension | Specification |
|---|---|
| **Access Control** | Teacher+ role only (RBAC-gated route) |
| **UI Components** | QuestionDataTable, QuestionFilterPanel, ImportButton, CreateQuestionButton, QuestionStatusBadge |
| **API Endpoints** | GET /api/v1/questions (with filters); POST /api/v1/questions/import |
| **Missing From Blueprint** | Admin screen is never mentioned anywhere in the document. The blueprint defines all Question System APIs but never describes the admin interface for managing questions. |

### Screen 16: Question Create/Edit Form `/admin/questions/new`, `/admin/questions/:id/edit` — F006, F009

| Dimension | Specification |
|---|---|
| **UI Components** | QuestionTextEditor, AnswerOptionInputs (4 options), CorrectAnswerRadio, ExplanationTextarea, SubjectChapterTopicSelector (cascading), DifficultySelect, PYQCheckbox, TagMultiSelect |
| **API Endpoints** | POST /api/v1/questions (create); PATCH /api/v1/questions/:id (edit) |
| **Missing From Blueprint** | Entirely absent from blueprint. No form spec, no validation rules, no image upload integration (despite StorageService and Cloudflare R2 being in the architecture) |

### Screen 17: Import Status Page `/admin/questions/import/:importId` — F007

| Dimension | Specification |
|---|---|
| **UI Components** | ImportProgressBar, ImportStatusBadge, ErrorRowTable (row number, field, error message), SuccessCount, RetryButton |
| **API Endpoint** | GET /api/v1/imports/:id (polling) |
| **State (TanStack)** | `useQuery` — importStatusQuery (refetchInterval: 3000 while status=processing) |
| **Missing From Blueprint** | Polling interval; maximum poll duration; what happens on import failure (partial success); error row display format |

---

## 5. INTEGRATION FLOW MAP

### Group A — Identity Domain (F001, F002, F003, F005)

```
users / profiles / roles tables
  → UserRepo / ProfileRepo / RoleRepo
    → AuthService / JWTService / RBACService
      → POST /auth/register | POST /auth/login | GET /auth/me | GET/PATCH /profile
        → Frontend: useMutation(registerMutation) | useMutation(loginMutation)
          → Zustand authStore: { accessToken, userId, role }
            → ProtectedRoute component (reads authStore.role)
              → Login Page | Registration Page | Profile Page
                → User action: submit form → mutation → Zustand update → redirect
```

**Integration gap:** Auth state hydration on page reload is unspecified. When the browser refreshes, Zustand loses the in-memory access token. The blueprint states the access token is NOT in localStorage. The frontend must silently call POST /auth/refresh (using the httpOnly cookie) on mount to recover the access token. This silent refresh flow is mentioned in the auth interceptor description but the initial mount hydration logic is absent.

### Group B — Content Domain (F006–F014)

```
questions / subjects / chapters / topics / tags tables
  → QuestionRepo / SubjectRepo / ChapterRepo / TopicRepo
    → QuestionService / TaxonomyService / ImportService
      → GET /questions | POST /questions | GET /subjects | GET /chapters | GET /topics | POST /questions/import | GET /questions/search
        → Frontend: useQuery(questionsQuery) | useMutation(createQuestionMutation) | useMutation(importMutation)
          → TanStack Query cache: ['questions', filters] | ['subjects'] | ['chapters', subjectId] | ['topics', chapterId]
            → QuestionDataTable | QuestionForm | SubjectChapterTopicSelector | ImportStatusPoller
              → Admin screens: /admin/questions | /admin/questions/new
                → User action: upload file → useMutation(import) → poll importStatusQuery → display results
```

**Integration gap:** The cascading taxonomy selector (Subject → Chapter → Topic) requires three dependent queries. The blueprint defines the three taxonomy API endpoints but never specifies how the cascading dependency is implemented in TanStack Query (dependent queries with `enabled` flag when parent selection changes). Cache invalidation after question creation is unspecified.

### Group C — Assessment Domain (F016–F026)

```
tests / attempts / attempt_answers tables
  → TestRepo / AttemptRepo / AttemptAnswerRepo
    → TestEngineService / AttemptService / ScoringService
      → GET /tests | POST /tests/:id/attempts | PATCH /attempts/:id/answers | POST /attempts/:id/submit | GET /attempts/:id/result
        → Frontend:
            useQuery(testsQuery) → Test Listing Screen
            useMutation(startAttemptMutation) → initializes Zustand activeTestStore
            [Zustand activeTestStore manages all in-test state]
            [Debounced PATCH /answers sync every 500ms from Zustand diff]
            [localStorage sync every 30s as backup]
            useMutation(submitAttemptMutation) → clears activeTestStore → navigates to result screen
              → Active Test Screen ← MOST CRITICAL FRONTEND COMPONENT
                → User action: select answer → Zustand update → debounce → PATCH answers
                → User action: submit → POST submit → navigate to result
```

**Integration gap:** The Zustand store initialization from the POST /tests/:id/attempts response is described in prose (Section 6.3 step 1: "Zustand test store initialized with question list, timer start") but the exact store fields are never defined. The debounce implementation (500ms per Section 9.1 Step 6) is mentioned but not the batch format. The localStorage backup format is unspecified, meaning crash recovery cannot be implemented deterministically.

**Critical gap:** Token expiry during a test. A test takes 180 minutes. The JWT access token expires in 15 minutes. The Axios interceptor handles refresh on 401, but this means during a 180-minute test, the token will be refreshed ~12 times via the interceptor. The blueprint does not address whether this silent refresh is transparent to the test session, what happens if refresh fails mid-test, or whether the active attempt state is preserved on a re-auth flow.

### Group D — Intelligence Domain (F027, F028, F031)

```
performance_snapshots / topic_analytics / weakness_signals tables
  → SnapshotRepo / WeaknessRepo
    → AnalyticsService / HeatmapService / ScoreService (all via Celery workers)
      → GET /dashboard | GET /dashboard/heatmap | GET /dashboard/score | GET /dashboard/attempts
        → Frontend:
            [Analytics computed async: 10–30s after submission]
            [No polling endpoint defined for analytics readiness]
            useQuery(dashboardQuery, { staleTime: 300000 }) → Performance Dashboard Screen
            useQuery(heatmapQuery) → WeaknessHeatmap component
            useQuery(scoreHistoryQuery) → PerformanceScore component
              → Dashboard Screen: renders widgets as data resolves
                → User action: view dashboard → data present or empty state
```

**Critical integration gap:** The async analytics computation creates a frontend dead zone. After submission, GET /dashboard will return either stale data (from last attempt's cache) or an empty response if no prior data exists. The blueprint does not specify: (a) what the dashboard returns immediately after a test before analytics complete, (b) whether there is a polling or webhook mechanism to notify the frontend that analytics are ready, (c) whether the result screen should hold the student until analytics complete or redirect immediately. The `analytics_status: "computing"` field in the submit response is the only breadcrumb — it is never connected to a frontend resolution strategy.

### Group E — Recovery Domain (F044, F045, F047)

```
mistakes / recovery_missions / mission_tasks / weak_topic_recommendations tables
  → MistakeRepo / MissionRepo
    → MistakeService / RecoveryService / RecommendationService (via Celery workers)
      → GET /mistakes | GET /mistakes/patterns | GET /missions | GET /missions/:id | POST /missions/:id/start | PATCH /missions/:id/tasks/:tid | POST /missions/:id/complete | GET /recommendations
        → Frontend:
            useQuery(mistakesQuery) → Mistake Vault Screen
            useQuery(missionsQuery) → Recovery Missions Screen
            useMutation(completeMissionTaskMutation) → Mission Detail Screen
            useQuery(recommendationsQuery) → Dashboard Panel or Separate Screen
              → User action: complete task → PATCH task → invalidate missionDetailQuery
              → User action: complete mission → POST complete → invalidate missionsQuery → navigate to /missions
```

**Integration gap:** Cache invalidation chain is unspecified. When a mission task is marked complete, the mission detail query must refetch. When a mission is completed, the missions list query must refetch and the weakness signals should update — but whether the frontend triggers a dashboard refetch at this point is unspecified. The "revise_topic" task type has no content destination — the blueprint contains no content delivery feature (lectures, PDFs, notes) in MVP scope, so this task type has no functional completion path.

---

## 6. MISSING GAP LIST

### Screen Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| No screen inventory exists | Cannot begin frontend architecture without a screen list | All 25 | Critical | Add a complete screen inventory with routes and access roles to the blueprint |
| Active Test Interface layout unspecified | The most complex screen; OMR layout, question navigator, section tabs are unknown | F016, F017, F018, F023, F024 | Critical | Define test screen wireframe with OMR grid, section nav, timer placement |
| Email verification confirmation screen absent | Post-registration UX gap; student is stuck after registration with no instructions | F001 | High | Define `/verify-email-sent` screen and `/verify-email?token=xxx` callback behavior |
| Test pre-start / detail screen absent | Student needs test instructions and section info before starting | F016, F017, F018 | Medium | Define `/tests/:id` screen before attempt creation |
| Admin Question Management screen absent | Teachers cannot manage questions without this | F006, F007, F009, F014 | High | Define `/admin/questions` screen and access control |
| Question Create/Edit form absent | No way to add questions manually without this | F006, F009 | High | Define form component spec |
| Analytics pending screen / state absent | Post-submission, student sees nothing while analytics compute | F027, F028, F031 | Critical | Define result screen with analytics-pending state and resolution mechanism |
| Recommendations screen location undefined | Is it a dashboard panel or a separate `/recommendations` page? | F047 | Medium | Define placement and route |

### Component Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| No component inventory defined | Cannot parallelize frontend development without component tree | All | Critical | Define component inventory aligned to feature groups |
| Zustand activeTestStore schema undefined | Cannot implement test state management without field definitions | F016–F026 | Critical | Define store shape: attempts, answers map, reviewFlags set, timeRemaining, syncStatus |
| OMR answer bubble component unspecified | Incorrect implementation would break NEET simulation fidelity | F024 | Critical | Specify: 4-option single-select, visual states (empty, selected, review-flagged), keyboard nav |
| Timer component behavior unspecified | Missing warning thresholds, format, and auto-submit behavior | F023 | High | Specify: MM:SS format, color-change at 10 min, pulse at 1 min, auto-submit trigger |
| RBAC-aware route guard implementation absent | Without this, role boundaries are not enforced in navigation | F005 | High | Define ProtectedRoute component with role prop |
| Reclassify action in Mistake Vault has no API | Blueprint mentions this UI feature but no backend endpoint exists | F044 | Medium | Either define the endpoint or remove from UI scope |
| Notification prefs JSONB field has no UI spec | notification_prefs is stored as JSONB with no documented structure | F003 | Medium | Define the notification preference fields and their UI controls |

### Integration Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| Silent token refresh on page load unspecified | Access token in memory is lost on refresh; app is unusable without this | F002 | Critical | Define: on app mount, call /auth/refresh if no access token; show loading until resolved |
| Token refresh during 180-minute test unspecified | Access token expires every 15 min; test session spans 180 min | F016, F026 | Critical | Define: Axios interceptor handles this transparently; confirm no test state is disrupted |
| Analytics polling / WebSocket strategy absent | Frontend has no way to know when async analytics complete | F027, F028, F031 | Critical | Define: either a polling endpoint (GET /dashboard/status?attempt_id=X) or SSE push |
| Cache invalidation chain undefined | Stale data after test submission, mission completion | F027, F044, F045 | High | Define invalidation triggers per mutation |
| Dependent query chain for taxonomy selector absent | Cascading subject→chapter→topic selectors require coordinated queries | F010, F011, F012 | Medium | Define TanStack Query `enabled` flags and dependency chain |
| Browser crash recovery flow unspecified | Blueprint says state is saved; frontend recovery flow is not described | F026 | High | Define: on /tests/:id/attempt/:id load, check Redis (via GET /attempts/:id) and localStorage; merge and restore |
| LocalStorage backup format unspecified | Cannot implement backup without knowing the serialization structure | F026 | High | Define localStorage key (`test_backup:{attemptId}`) and JSON structure |
| Answer batch payload format | PATCH /answers accepts up to 10 events per call; batching logic is unspecified | F026 | High | Define: Zustand diff algorithm, batch assembly, and debounce flush logic |
| Reclassify mistake API endpoint missing | Blueprint UI mentions this; no backend endpoint exists | F044 | Medium | Add PATCH /mistakes/:id/root_cause endpoint or descope from UI |

### Visualization Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| Weakness Heatmap: chart type unspecified | Cannot implement without knowing if this is a treemap, table, color-coded grid, or heat matrix | F028 | Critical | Specify: chart type, library (e.g. Recharts, D3, custom SVG), subject→chapter→topic drill-down behavior |
| Weakness Heatmap: severity color mapping unspecified | 🔴/🟡 emoji are in Section 9.1 but no hex values or CSS classes exist | F028 | High | Define: critical=red (#DC2626), high=orange (#EA580C), medium=yellow (#CA8A04), low=green (#16A34A) |
| Performance Score history: chart type unspecified | Line chart? Bar chart? Sparkline? Library? Y-axis (0–100)? X-axis (attempt number or date)? | F031 | Critical | Specify chart type, axes, data format expected from GET /dashboard/score |
| Improvement trend: 5-test rolling chart unspecified | Dashboard API returns "improvement_trend (last 5 tests)" — rendering is undefined | F027 | High | Specify: mini line chart in dashboard panel, axes, hover behavior |
| Empty visualization states unspecified | What renders when a student has 0 attempts? | F027, F028, F031 | High | Define per-visualization empty state message and placeholder rendering |
| Chart library selection absent | Multiple team members (or AI sessions) may choose different chart libraries | F027, F028, F031 | Medium | Lock to Recharts (already in React ecosystem) or D3; document the choice |

### Execution-Flow Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| Post-submission analytics resolution flow absent | Students are left with no UI signal after submitting a test | F027, F028, F031 | Critical | Define: result screen shows score immediately, then polling indicator until dashboard is ready (with redirect or manual navigate button) |
| Mission "revise_topic" task has no content destination | Task completion is blocked; no content delivery exists in MVP | F045 | High | Descope from MVP or define an external link field in MissionTask |
| Mission "retry_questions" task has no question-set endpoint | Cannot surface a set of questions to retry without a dedicated API | F045 | High | Define GET /missions/:id/tasks/:tid/questions or descope this task type |
| Question status workflow UI absent | Draft→Review→Approved→Published transitions need admin UI triggers | F006 | Medium | Define status change buttons and confirmation dialogs in admin question screen |
| Auto-submit timer flow absent | Blueprint says timer at 0 triggers auto-submit; no UI confirmation or cancellation is defined | F023 | High | Define: at 0, call POST /submit with {force:true}; show brief "Time's up — submitting..." overlay |

### State-Management Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| Zustand activeTestStore schema undefined | This is the most complex state in the MVP | F016–F026 | Critical | Define: `{ attemptId, testId, questions[], currentIndex, answers: Record<questionId,optionId>, reviewFlags: Set<questionId>, timeRemaining, lastSyncedAt, syncStatus: 'synced'|'syncing'|'error' }` |
| TanStack Query key taxonomy undefined | Inconsistent keys cause cache fragmentation | All API features | High | Define key patterns: `['dashboard']`, `['heatmap']`, `['missions', userId]`, `['mistakes', {rootCause, severity}]` |
| Auth state rehydration on mount undefined | App is unusable on page refresh without this | F002 | Critical | Define: `useEffect` on app mount calls `/auth/refresh`; sets access token in authStore; shows full-page loader until resolved |
| Global network error state undefined | Unhandled network errors silently fail | All | Medium | Define: TanStack Query `onError` global handler with toast notification system |

### API-Contract Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| GET /dashboard response schema absent | Cannot build dashboard components without knowing JSON shape | F027 | Critical | Define full JSON schema with field names, types, and nesting |
| GET /dashboard/heatmap response schema absent | Cannot build heatmap visualization | F028 | Critical | Define: `{subjects: [{id, name, chapters: [{id, name, topics: [{id, name, severity, accuracy_pct}]}]}]}` |
| GET /dashboard/score response schema absent | Cannot build score history chart | F031 | High | Define: `{current_score, history: [{attempt_id, score, computed_at}]}` |
| GET /attempts/:id/result response schema absent | Result screen cannot be built | F026 | Critical | Define: `{score, correct, incorrect, unattempted, analytics_status: 'computing'|'ready'}` |
| GET /mistakes response schema absent | Mistake Vault cannot be built | F044 | High | Define: `{mistakes: [{id, question_id, root_cause, severity, recurrence_count, first_seen_at}], cursor}` |
| GET /missions response schema absent | Missions list cannot be built | F045 | High | Define: `{missions: [{id, title, trigger_source, expected_gain, priority_score, status, task_count, tasks_completed}]}` |
| GET /recommendations response schema absent | Recommendation list cannot be built | F047 | High | Define: `{recommendations: [{topic_id, topic_name, chapter_name, subject_name, accuracy_pct, mark_leakage_estimate}]}` |
| Analytics readiness polling endpoint absent | Post-submission async gap has no resolution | F027, F028, F031 | Critical | Add GET /dashboard/status?attempt_id=:id returning `{status: 'computing'|'ready'}` |
| Mistake reclassify endpoint absent | UI mentions this action; no backend supports it | F044 | Medium | Add PATCH /mistakes/:id with `{root_cause: string}` |

### Error / Empty-State Gaps

| Gap | Why It Matters | Affected Features | Severity | Recommended Fix |
|---|---|---|---|---|
| No loading skeleton defined for any screen | Perceived performance depends on meaningful loading states | All | High | Define skeleton components per screen |
| No error message copy for any API error code | Cannot display user-facing errors without copy | All | High | Map all error codes to human-readable messages |
| No empty state defined for any list | First-time students see blank screens without empty states | F027, F028, F044, F045, F047 | High | Define per-screen empty state: illustration + message + CTA |
| Post-submission analytics pending state undefined | Student sees nothing while computation runs | F027 | Critical | Define pending indicator with estimated time message |
| Answer sync failure during test undefined | A PATCH /answers failure during test could silently lose data | F026 | Critical | Define: silent retry queue with sync status indicator; never block student UI |
| Browser crash recovery UX undefined | Student returns to a test after crash and sees no guidance | F026 | High | Define: toast "Restored your previous session" on load from localStorage/Redis |
| Rate-limit error handling undefined in UI | Register and login endpoints have rate limits; frontend shows nothing | F001, F002 | Medium | Define: show countdown timer until rate limit resets |
| Import partial success state undefined | Import can succeed partially; the UI has no way to communicate this | F007 | Medium | Define: separate success count and error count display with downloadable error report |

---

## 7. RECOMMENDED BLUEPRINT SECTION — FRONTEND DEPENDENCY ARCHITECTURE

The following section should be added to the blueprint as **Section 6A — Frontend Dependency Architecture**, positioned between Section 6 (Production-Grade Architecture Design) and Section 7 (Advanced Data Architecture).

---

### 6A.1 Screen Inventory and Route Map

```
ROUTE                           SCREEN NAME                      ACCESS        FEATURES
/                               Landing / Redirect               Public         —
/register                       Registration Page                Public         F001
/verify-email-sent              Email Verification Sent          Public         F001
/login                          Login Page                       Public         F002
/dashboard                      Performance Dashboard            Student        F027, F028, F031, F047
/dashboard/attempts             Attempt History                  Student        F027
/dashboard/attempts/:id         Single Attempt Analytics         Student        F027
/tests                          Test Listing                     Student        F016, F017, F018
/tests/:id                      Test Detail / Pre-Start          Student        F016, F017, F018
/tests/:id/attempt/:attemptId   Active Test Interface            Student        F016–F026
/attempts/:id/result            Test Result / Score              Student        F025, F026
/mistakes                       Mistake Vault                    Student        F044
/missions                       Recovery Missions                Student        F045
/missions/:id                   Mission Detail                   Student        F045
/recommendations                Weak Topic Recommendations       Student        F047
/profile                        Student Profile                  Student        F003
/admin/questions                Question Bank Management         Teacher+       F006, F007, F014
/admin/questions/new            Create Question                  Teacher+       F006, F009
/admin/questions/:id/edit       Edit Question                    Teacher+       F006, F009
/admin/questions/import/:id     Import Status                    Admin          F007
```

### 6A.2 Screen → Component Mapping

**Performance Dashboard (`/dashboard`):**
- `DashboardLayout`
  - `PerformanceScoreWidget` → GET /dashboard/score
  - `WeaknessHeatmap` → GET /dashboard/heatmap
  - `ImprovementTrendChart` → GET /dashboard (improvement_trend field)
  - `ActiveMissionsPanel` → GET /missions (first 3)
  - `WeakTopicList` → GET /recommendations
  - `RecentAttemptsPanel` → GET /dashboard/attempts (first 5)

**Active Test Interface (`/tests/:id/attempt/:attemptId`):**
- `TestLayout`
  - `TimerDisplay` (reads Zustand: timeRemaining)
  - `SectionTabBar` (reads Zustand: questions grouped by section)
  - `QuestionPanel` (reads Zustand: questions[currentIndex])
  - `OMRAnswerGrid` (reads Zustand: answers[currentQuestion])
  - `ReviewFlagToggle` (reads/writes Zustand: reviewFlags)
  - `QuestionNavigator` (reads Zustand: 180-question grid)
  - `SyncStatusIndicator` (reads Zustand: syncStatus)
  - `SubmitButton` (triggers submitAttemptMutation)

### 6A.3 Component → API Mapping

| Component | Query Hook | API Endpoint | Cache Key | Stale Time |
|---|---|---|---|---|
| PerformanceScoreWidget | useScoreHistory | GET /dashboard/score | ['score', userId] | 5 min |
| WeaknessHeatmap | useHeatmap | GET /dashboard/heatmap | ['heatmap', userId] | 5 min |
| ImprovementTrendChart | useDashboard | GET /dashboard | ['dashboard', userId] | 5 min |
| MistakeVaultList | useMistakes | GET /mistakes | ['mistakes', userId, filters] | 2 min |
| MissionsList | useMissions | GET /missions | ['missions', userId] | 1 min |
| RecommendationList | useRecommendations | GET /recommendations | ['recommendations', userId] | 10 min |
| TestList | useTests | GET /tests | ['tests'] | 30 min |
| ImportStatusPoller | useImportStatus | GET /imports/:id | ['import', importId] | Poll 3s |

### 6A.4 Zustand Store Schemas

**authStore:**
```typescript
{
  accessToken: string | null;
  userId: string | null;
  role: 'student' | 'teacher' | 'admin' | null;
  setAuth: (token: string, userId: string, role: string) => void;
  clearAuth: () => void;
}
```

**activeTestStore:**
```typescript
{
  attemptId: string | null;
  testId: string | null;
  questions: Question[];
  currentQuestionIndex: number;
  answers: Record<string, string>;          // questionId → optionId
  reviewFlags: Set<string>;                 // questionId
  timeRemaining: number;                    // seconds
  startedAt: string;                        // ISO
  syncStatus: 'idle' | 'syncing' | 'error';
  pendingEvents: AnswerEvent[];             // events not yet synced
  initTest: (attemptId, testId, questions, durationSeconds) => void;
  setAnswer: (questionId, optionId) => void;
  toggleReview: (questionId) => void;
  decrementTimer: () => void;
  setSyncStatus: (status) => void;
  clearTest: () => void;
}
```

### 6A.5 State → User Workflow Mapping

```
User navigates to /tests → testsQuery fetches → TestList renders
  ↓
User clicks test → navigate to /tests/:id → testDetailQuery fetches
  ↓
User clicks "Start Test" → startAttemptMutation → on success:
  → activeTestStore.initTest(attemptId, testId, questions, duration)
  → localStorage.setItem('test_backup:{attemptId}', JSON.stringify(store))
  → navigate to /tests/:id/attempt/:attemptId
  ↓
User answers questions → activeTestStore.setAnswer()
  → debounce 500ms → PATCH /attempts/:id/answers (batch up to 10 events)
  → on success: activeTestStore.setSyncStatus('idle')
  → every 30s: localStorage.setItem('test_backup:{attemptId}', JSON.stringify(store))
  ↓
User submits → submitAttemptMutation → POST /attempts/:id/submit
  → activeTestStore.clearTest()
  → localStorage.removeItem('test_backup:{attemptId}')
  → navigate to /attempts/:id/result
  ↓
Result page renders → attemptResultQuery fetches → shows score
  → if analytics_status='computing': show pending indicator
  → poll GET /dashboard/status?attempt_id=:id every 5s
  → on status='ready': invalidate ['dashboard'], ['heatmap'], ['score'], ['missions'], ['mistakes']
  → show "View Full Analysis" button → navigate to /dashboard
```

### 6A.6 Loading / Error / Empty State Mapping

| Screen | Loading State | Error State | Empty State |
|---|---|---|---|
| Dashboard | Per-widget skeleton | Per-widget "Failed to load, retry" button | "Take your first test to see your analysis" with link to /tests |
| Heatmap | Animated skeleton grid | "Heatmap unavailable" | "No weakness data yet" |
| Mistake Vault | Skeleton list (5 items) | "Failed to load mistakes" | "No mistakes tracked yet. Complete a test to populate your Vault." |
| Missions | Skeleton cards (3 items) | "Failed to load missions" | "No active missions. Complete a test to generate your recovery plan." |
| Active Test | Full-screen loader with "Loading your test..." | Blocking error with "Return to test list" | N/A |
| Test Result | None (score from submit response is immediate) | "Result unavailable" with support link | N/A |

### 6A.7 Integration Acceptance Criteria

- Registration → Login → Dashboard renders within 3 user actions
- After test submission, score appears within 1 second (synchronous)
- After test submission, dashboard analytics appear within 35 seconds (polling resolves)
- Answer events are synced within 1 second of user input (debounce + PATCH)
- Browser crash during test: on return, restored state is confirmed via "Restored your previous session" toast
- Token expiry during test: silent refresh is transparent; no test state is lost
- 401 on any non-test screen: redirect to /login with return URL preserved

---

## 8. IMPLEMENTATION ORDER

### Step 1: Freeze Backend API Contracts

**Goal:** Lock all API response schemas before any frontend code is written.  
**Dependencies:** None.  
**Output Artifact:** `API_CONTRACTS.md` with full JSON request/response schemas for all 25 endpoints, including GET /dashboard, GET /dashboard/heatmap, GET /dashboard/score, GET /attempts/:id/result, GET /mistakes, GET /missions, GET /missions/:id, GET /recommendations.  
**Completion Criteria:** Every endpoint has a documented JSON response schema with field names, types, and example values. GET /dashboard/status (analytics polling) endpoint is added and documented.

### Step 2: Define Screen Map and Route Inventory

**Goal:** Create the complete screen list with routes, access roles, and which features each screen serves.  
**Dependencies:** Step 1 (API shapes inform what each screen displays).  
**Output Artifact:** `SCREEN_MAP.md` — the 17-screen inventory from Section 6A.1 above, with per-screen component list.  
**Completion Criteria:** Every MVP feature maps to at least one screen. Every screen has a defined route and access role. No features are screen-orphaned.

### Step 3: Define Component Inventory

**Goal:** Enumerate every React component needed to implement all screens.  
**Dependencies:** Step 2 (screens define components needed).  
**Output Artifact:** `COMPONENT_INVENTORY.md` — grouped by domain (Auth, Content, Assessment, Intelligence, Recovery, Shared). Each component entry lists: name, screen(s) it appears in, props interface, API dependency (if any), Zustand dependency (if any).  
**Completion Criteria:** Every screen from Step 2 has all its components listed. Shared components (TimerDisplay, SectionTabBar, QuestionNavigator) are identified once and cross-referenced.

### Step 4: Define TanStack Query Hook Layer

**Goal:** Standardize all query and mutation hooks before implementation begins.  
**Dependencies:** Steps 1 and 3 (API contracts + component map).  
**Output Artifact:** `QUERY_HOOKS.md` — for each hook: queryKey, endpoint, staleTime, refetchInterval (if polling), enabled conditions (for dependent queries), onSuccess cache invalidation list, onError behavior.  
**Completion Criteria:** Every API endpoint consumed by the frontend has exactly one named hook. Cache invalidation triggers are defined for all mutations.

### Step 5: Define Zustand State Management Layer

**Goal:** Lock the store schemas for authStore and activeTestStore before test session development.  
**Dependencies:** Step 4 (query hooks clarify what state lives in Zustand vs TanStack Query).  
**Output Artifact:** Zustand store TypeScript interfaces documented in `STATE_MANAGEMENT.md`. Includes: localStorage backup format for activeTestStore, auth state rehydration logic, store action names.  
**Completion Criteria:** Both stores have TypeScript interfaces. localStorage key patterns are defined. The auth mount hydration flow (silent refresh on app load) is explicitly sequenced.

### Step 6: Define Visualization Specifications

**Goal:** Specify chart type, library, axis definitions, and color mapping for all three intelligence-domain visualizations.  
**Dependencies:** Steps 1 and 5 (API response shapes + confirmed library choices).  
**Output Artifact:** `VISUALIZATION_SPEC.md` with: Weakness Heatmap (chart type: color-coded topic grid with subject/chapter grouping, library: Recharts or custom SVG, severity palette), Score History chart (line chart, X: attempt number, Y: 0–100 score, library: Recharts LineChart), Improvement Trend (mini sparkline, 5-point line, inline in dashboard panel).  
**Completion Criteria:** A developer can implement all three visualizations without design ambiguity. Library choice is locked. Empty state rendering is specified for each.

### Step 7: Define Error / Loading / Empty State Standards

**Goal:** Establish UI patterns for all three state types before component implementation.  
**Dependencies:** Steps 2 and 3 (screens and components are known).  
**Output Artifact:** `UI_STATE_STANDARDS.md` — loading skeleton specs per component type, error message copy for all API error codes, empty state copy and CTA per screen, network retry behavior, sync failure display during active test.  
**Completion Criteria:** Every screen has a documented loading, error, and empty state. No API error code is unmapped to a user-visible message.

### Step 8: Define End-to-End Integration Scenarios

**Goal:** Document the complete frontend execution path for the three critical user journeys.  
**Dependencies:** Steps 1–7.  
**Output Artifact:** `INTEGRATION_SCENARIOS.md` with step-by-step frontend flows for: (a) Registration → Login → First Test → Submit → Dashboard, (b) Return Visit → Dashboard → Recovery Mission → Task Completion, (c) Browser Crash During Test → Return → State Recovery.  
**Completion Criteria:** Each scenario is specified as a sequence of: user action → Zustand mutation → API call → cache update → navigation → render. No steps require guessing.

### Step 9: Define Testing Order

**Goal:** Sequence frontend testing to match backend readiness and prevent integration bottlenecks.  
**Dependencies:** Steps 1–8 and backend implementation progress.

**Recommended testing sequence:**

| Order | Test Type | Scope | Dependency |
|---|---|---|---|
| 1 | Unit tests: Zustand stores | authStore and activeTestStore state transitions | Step 5 |
| 2 | Unit tests: Query hooks | Mock API responses, cache key validation | Step 4 |
| 3 | Integration test: Auth flow | Register → verify → login → /auth/me | Backend F001, F002 complete |
| 4 | Integration test: Test session | Start → answer → save → submit | Backend F016, F026 complete |
| 5 | Integration test: Token refresh during test | Simulate 401 mid-PATCH /answers | Backend F002, F026 complete |
| 6 | Integration test: Analytics polling | Submit → poll /dashboard/status → dashboard renders | Backend F027, F028, F031 complete |
| 7 | Integration test: Crash recovery | Kill browser mid-test → reload → restore state | Backend F026, F023 complete |
| 8 | E2E test: Full student journey | Playwright: register → test → submit → dashboard → mission | All backend complete |
| 9 | E2E test: Empty states | First-time student sees correct empty states everywhere | All backend complete |

---

## 9. IMPLEMENTATION READINESS VERDICT

### Verdict: NOT READY (for frontend implementation)

### Explanation

**1. Frontend cannot start from this document alone.** A backend developer can start coding on day one. A frontend developer cannot. The gap between "backend-ready" and "frontend-ready" in this blueprint is total: no screens, no components, no query hooks, no state schemas, no visualization specs, no loading/error/empty states. Every frontend implementation decision must be invented, not derived from the blueprint.

**2. The three most complex screens have the most missing specifications.** The Active Test Interface (F016–F026), the Performance Dashboard (F027/F028/F031), and the Mistake Vault (F044) are the most implementation-critical frontend screens. They also have the least frontend documentation. The Active Test Interface in particular — which must manage a 180-question, 3-hour session with per-second timer ticks, debounced answer sync, crash recovery, and silent token refresh — has zero component or state specification.

**3. The async analytics gap is unresolved at the frontend level.** Submission is synchronous; analytics take 10–30 seconds asynchronously. The blueprint identifies this as an architectural decision but never resolves it for the frontend. No polling endpoint exists. No pending state is defined. No resolution flow is specified. This gap will produce either a broken result screen or an ad-hoc implementation that is never validated.

**4. Four API response schemas critical to frontend rendering are absent.** GET /dashboard, GET /dashboard/heatmap, GET /attempts/:id/result, and the three recovery domain list endpoints have no documented JSON response structure. No frontend component can be built against an undocumented response shape.

**5. The Section 15 "Implementation Ready" verdict applies to the backend, not the frontend.** The blueprint's own readiness assessment (Section 15.4) confirms schema, API, service, and test plan coverage — all backend dimensions. It makes no claim about frontend screen coverage, component coverage, or visualization coverage because none of those exist. The "25/25 features covered" in Section 15.1 means 25/25 have a backend implementation path. It does not mean 25/25 have a frontend implementation path.

---

*Gap report generated from: NEET_POS_Engineering_Blueprint.md (single source of truth). No features, screens, components, endpoints, or flows were invented. All gaps are based on absence of evidence from the blueprint, not contradictions within it.*
