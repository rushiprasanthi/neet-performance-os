# **NEET Performance Operating System: Comprehensive Frontend and Integration Specification**

The NEET Performance Operating System (NEET POS) represents a fundamental paradigm shift from traditional educational content delivery mechanisms to an intelligence-driven, diagnostic, and recovery-oriented ecosystem.1 The foundational engineering objective of this platform relies on establishing an uninterrupted behavioral data collection loop: capturing atomic test-taking events, processing these high-frequency inputs into actionable diagnostic intelligence, and issuing targeted recovery prescriptions.1 While the core backend architecture—comprising FastAPI for asynchronous handling, PostgreSQL for transactional storage, Redis for state caching, and Celery for background analytical processing—provides robust data infrastructure, the frontend implementation definitions currently exhibit severe maturity gaps.1 Existing blueprint documentation places frontend readiness between 15% and 50%, with high-priority analytical modules such as the Mistake Vault (F044) and Recovery Missions (F045) existing entirely as single-line roadmap items devoid of user interface schemas, integration flows, or state management strategies.1  
To bridge this chasm without introducing modifications to the established backend architecture, this exhaustive report provides an implementation-ready specification that elevates the frontend definition to a 95%+ readiness threshold. By structuring the architectural deliverables through enterprise specification methodologies, this document meticulously maps features to screens, components, APIs, queries, and localized states. The following integrated specification documents establish a definitive blueprint for engineering teams to construct a scalable, resilient, and highly responsive React-based client application.

## **FRONTEND\_ARCHITECTURE.md: System Foundations and Strategic Decoupling**

The frontend architecture of the NEET POS is designed to balance the severe operational constraints of a solo-founder development timeline with the rigorous performance requirements of a high-stakes examination simulator.1 The architectural philosophy mandates strict decoupling between synchronous operational states and asynchronous server data, ensuring that the critical data collection engine—Attempt Tracking (F026)—remains completely insulated from network latency and background computational bottlenecks.1  
The application relies on React bootstrapped via Vite to ensure rapid module replacement and highly optimized production builds. The core technical strategy employs a dual-store state management topology. Zustand is exclusively reserved for managing the highly synchronous, rapidly mutating local state required by the Test Engine, providing deterministic and granular render control without the boilerplate overhead of Redux.1 Conversely, TanStack Query (React Query) serves as the singular authority for server state, orchestrating all interactions with the FastAPI backend through a tightly controlled factory pattern for query keys and hook abstractions.2  
Furthermore, the architecture acknowledges the rapidly expanding volume of the attempt\_answers dataset.1 Because aggregating performance metrics across subjects, chapters, and topics is highly analytical and computationally heavy, the frontend is engineered to expect eventual consistency. It utilizes adaptive frontend polling mechanisms and exponential backoff strategies to communicate seamlessly with Celery worker queues, entirely decoupling the user's test submission experience from the synchronous generation of their diagnostic dashboard.1

## **SCREEN\_MATRIX.md: Comprehensive User Interface Inventory**

The screen matrix acts as the foundational inventory of all distinct visual boundaries within the application, mapped explicitly against the 25 MVP features.1 The interface design prioritizes deep analytical immersion, requiring minimal cognitive overhead from the student while navigating complex performance data.

| Screen Identifier | Associated MVP Features | Primary Layout Context | Core User Action | Data Volatility |
| :---- | :---- | :---- | :---- | :---- |
| **SCR-01: Public Landing** | N/A | PublicLayout | Marketing engagement and entry gateway | Static |
| **SCR-02: Registration** | F001 | PublicLayout | Capturing longitudinal profile anchors | Low |
| **SCR-03: Authentication** | F002 | PublicLayout | Verifying JWT credentials | Low |
| **SCR-04: Profile Config** | F003 | StudentLayout | Setting target year, score, and subject preferences | Low |
| **SCR-05: Dashboard** | F027, F031 | StudentLayout | Synthesizing Performance Score and readiness index | Medium |
| **SCR-06: Test Hub** | F016, F017, F018 | StudentLayout | Selecting Full Mocks, Unit Tests, or Mixed Revisions | Low |
| **SCR-07: Active Engine** | F023, F024, F025, F026 | TestEngineLayout | Simulating OMR, tracking pacing, capturing atomic events | Extremely High |
| **SCR-08: Heatmap Core** | F028, F010, F011 | StudentLayout | Visualizing chapter-level weakness aggregations | Medium |
| **SCR-09: Topic Drill-Down** | F028, F012 | StudentLayout | Pinpointing granular conceptual failures | Medium |
| **SCR-10: Mistake Vault** | F044 | StudentLayout | Reviewing categorized incorrect answers by root cause | Medium |
| **SCR-11: Recovery Ops** | F045, F047 | StudentLayout | Executing actionable study missions and topic presets | Medium |
| **SCR-12: Question Admin** | F006, F014 | AdminLayout | Searching, filtering, and tagging repository content | Low |
| **SCR-13: Import Pipeline** | F007, F008 | AdminLayout | Executing bulk JSON/CSV/XLSX uploads | Low |

The isolation of the TestEngineLayout (SCR-07) from standard navigational layouts is a critical architectural decision. By removing standard navigation headers, sidebars, and footer elements, the interface maximizes the viewport real estate dedicated to the examination context, minimizing distraction and preventing accidental route changes that could interrupt the highly volatile event capture sequence.1

## **NAVIGATION\_MAP.md: Enterprise Route Architecture and Navigation Guards**

The routing topology, powered by React Router v6, strictly enforces Role-Based Access Control (RBAC) (F005) while segregating public entry points from protected operational zones.1 The architecture departs from the legacy React Router v5 paradigm of utilizing custom \<PrivateRoute\> components that manually interrogate authentication logic within the render function. Instead, it utilizes nested layout routes and dedicated \<ProtectedRoute\> boundary components that seamlessly integrate with the application's authentication state.8

### **Role-Based Authorization Mechanisms**

The authentication architecture relies on JSON Web Tokens (JWT) possessing specific embedded role claims: Student, Teacher, and Admin.1 The routing hierarchy utilizes a useAuth hook—interfacing directly with the application's secure credential store—to retrieve both the validity of the current session and the assigned role of the active user.6  
When a navigation event occurs, the \<ProtectedRoute\> component evaluates the destination path against an allowed roles matrix.8 If the session is invalid or the token is entirely absent, the router intercepts the transition and executes a declarative \<Navigate to="/login" replace /\> instruction, ensuring the unauthorized route is never mounted to the DOM.8 To enhance the user experience, the router captures the user's intended destination within the location.state object, enabling an automatic redirection to the requested resource immediately following successful authentication.9  
If the user possesses valid authentication but attempts to access a route mapped to a higher privilege tier (e.g., a Student attempting to access the /admin/import pipeline), the \<ProtectedRoute\> component diverts the user to an explicit \<UnauthorizedBoundary /\> interface.8 This explicit demarcation prevents privilege escalation vulnerabilities on the client side while maintaining a predictable navigational flow.10

### **Hierarchical Routing Topology**

The foundational route structure is orchestrated using the createBrowserRouter API, leveraging deep nesting to share layouts and authentication boundaries systematically 8:

JavaScript  
export const router \= createBrowserRouter(,  
  },  
  {  
    path: '/',  
    element: \<ProtectedRoute allowedRoles\={} /\>,  
    children:  
      },  
      {  
        element: \<TestEngineLayout /\>,  
        children: \[  
          { path: 'tests/active/:testId', element: \<ActiveEngine /\> },  
        \]  
      }  
    \],  
  },  
  {  
    path: '/admin',  
    element: \<ProtectedRoute allowedRoles\={} /\>,  
    children: \[  
      {  
        element: \<AdminLayout /\>,  
        children: \[  
          { path: 'questions', element: \<QuestionAdmin /\> },  
          { path: 'import', element: \<ImportPipeline /\> },  
        \]  
      }  
    \],  
  }  
\]);

This strict architectural layout ensures that deep-linked F045 Recovery Missions or complex analytical drill-downs cannot be directly accessed or manipulated by unauthorized actors.1

## **COMPONENT\_ARCHITECTURE.md: Scalable React Component Trees and UI Primitives**

The visual architecture adheres to the atomic design methodology, aggressively decoupling data presentation primitives from complex business logic and state subscription layers. This separation is vital to mitigating the performance degradation that typically accompanies high-frequency re-rendering during state updates, particularly within the Test Engine context where atomic behavioral events are tracked continuously.1

### **Universal UI Primitives**

The design system standardizes several core primitives. Because the platform heavily relies on specialized educational content, typography components are engineered to process and cleanly render embedded LaTeX strings for complex physics formulas and chemical equations. Standard interactive elements—such as checkboxes, toggle switches, and tab groups—are fully customized to operate completely free of complex prop drilling, utilizing local context boundaries for state management.

### **The Test Engine Component Subtree**

The active testing environment requires the highest degree of rendering optimization within the entire application. The ActiveEngine is structured as a collection of isolated sibling components orchestrated by the Zustand state manager.1

1. **QuestionViewer**: This component receives the current question text, taxonomy tags, and multiple-choice options. It utilizes strict referential equality checks via React.memo to ensure it only recalculates its render tree when the active questionId specifically mutates.  
2. **OMRPanel (Optical Mark Recognition Simulation)**: Representing the digital answer sheet, this grid component subscribes solely to the drafts slice of the state. It maps boolean values for completion status, flagged-for-review status, and visited status. To replicate the tactile speed of a physical exam, the specialized radio button primitives bypass standard React synthetic event propagation delays, offering instantaneous visual feedback to the student.1  
3. **PacingTimer**: Operating independently from the primary layout context, the timer component subscribes to the Zustand timer slice to execute local DOM updates every second. By completely isolating the timer from the main testing tree, the architecture guarantees that the one-second interval ticks do not force the entire QuestionViewer or OMRPanel to needlessly re-render.1  
4. **EventTracker**: Functioning as a headless (non-visual) component, the EventTracker observes user interactions—such as answer selections, answer changes, and review flags—and continuously calculates the delta time spent on the current question. It compiles these events into highly formatted payload artifacts and pushes them to the in-memory telemetry buffer for eventual synchronization.1

## **STATE\_MANAGEMENT\_ARCHITECTURE.md: Zustand Decomposition and TanStack Cache Strategy**

The state management strategy systematically segregates volatile operational data from persistent analytical data. This deliberate separation resolves critical architectural pressure points related to F026 (Attempt Tracking) performance and crash recovery, while ensuring that deep analytical queries remain consistent and easily invalidatable.1

### **Zustand Architecture: Synchronous Store Decomposition**

To satisfy the explicit hidden requirement for robust crash recovery, the client must preserve student sessions locally.1 Utilizing React context or standard Redux implementations for a rapidly mutating testing state introduces unacceptable latency and prop-drilling complexity. The architecture utilizes Zustand to create a lightweight, modular store configured with persistent middleware interacting directly with localStorage.1  
The useTestSessionStore is decomposed into distinct, logically isolated slices to minimize unnecessary re-render subscriptions:

* **Session Slice**: Manages the overarching metadata, including activeTestId, studentId, and testStatus (IDLE, IN\_PROGRESS, SUBMITTED).  
* **Draft Answers Slice**: Structured as a normalized dictionary object (Record\<string, DraftObject\>), this slice maps a question\_id to its current state: the selected option\_id, a boolean indicating if it is is\_flagged for review, and the cumulative time\_spent\_ms. Normalization prevents expensive array traversal operations during rapid answer changes.  
* **Timer Slice**: Tracks the absolute globalSecondsRemaining alongside a rapidly resetting currentQuestionSeconds.  
* **Telemetry Buffer Slice**: Maintains an array of TrackingEvent objects detailing the raw atomic events generated by the student.1

The Session, Draft Answers, and Timer slices are wrapped in the Zustand persist middleware. Upon navigating to /tests/active/:testId, the store executes an automatic hydration cycle. If a catastrophic event occurs—such as a power failure causing a browser crash—the student can return to the platform, and the local storage hydration instantly reconstructs their active draft, fully restoring their progress and preventing data loss.1 The Telemetry Buffer is deliberately excluded from persistence to avoid heavy I/O blocking against the disk during rapid sequential interactions.

### **TanStack Query Architecture: Caching, Pre-fetching, and Invalidation**

TanStack Query manages the entirety of the asynchronous server state, ensuring high scalability and providing an abstraction layer over the FastAPI backend. To prevent the injection of subtle bugs caused by typographical errors in query identification, the architecture mandates a strictly typed, centralized query key factory that enforces the usage of array keys.3

JavaScript  
export const queryKeys \= {  
  pos: \['neet\_pos'\] as const,  
  user: {  
    profile: (userId: string) \=\> \[...queryKeys.pos, 'user', userId\] as const,  
  },  
  questions: {  
    list: (filters: any) \=\> \[...queryKeys.pos, 'questions', 'list', filters\] as const,  
    detail: (id: string) \=\> \[...queryKeys.pos, 'questions', 'detail', id\] as const,  
  },  
  analytics: {  
    base: () \=\> \[...queryKeys.pos, 'analytics'\] as const,  
    dashboard: (attemptId: string) \=\> \[...queryKeys.analytics.base(), 'dashboard', attemptId\] as const,  
    heatmap: (subjectId: string) \=\> \[...queryKeys.analytics.base(), 'heatmap', subjectId\] as const,  
    missions: () \=\> \[...queryKeys.analytics.base(), 'missions'\] as const,  
  }  
};

This deeply nested taxonomy allows for surgical cache invalidation. Upon the successful completion of a Recovery Mission (F045), the application can execute queryClient.invalidateQueries({ queryKey: queryKeys.analytics.base() }) to purge and refresh all associated dashboards and heatmaps simultaneously.3  
Furthermore, direct invocation of useQuery or useMutation within component files is strictly prohibited. Engineering teams must create custom hooks that encapsulate queryOptions to standardize staleTime, cacheTime, and retry logic.2  
The architecture leverages React Query's internal structural logic to handle massive datasets. For instance, populating the Question Bank (F006) repository interface utilizes useInfiniteQuery. The key namespace for infinite queries is explicitly demarcated from standard list queries, as the internal data caching behaviors differ fundamentally and sharing keys between the two paradigms corrupts the paginated result arrays.11  
To create a seamlessly fluid user experience, the system heavily utilizes prefetching. When a student hovers over a specific chapter within the F028 Weakness Heatmap, the application proactively dispatches a queryClient.prefetchQuery payload for the corresponding F012 Topic drill-down data. By the time the user executes the click event, the analytical data is already present in the synchronous cache, completely eliminating the transition loading state.

## **API\_RESPONSE\_CONTRACTS.md: Enforcing Idempotency and Payload Structures**

Establishing rigorous payload contracts guarantees that frontend engineers can construct robust rendering logic independent of the backend's completion status. The documentation dictates precise schemas for both data ingestion and data egress.

### **Contract: F026 Attempt Submission Payload**

Due to the implied requirement of strict idempotency, network retries must never result in duplicate submission entries within the rapidly growing attempt\_answers PostgreSQL table.1 The frontend enforces this by generating an immutable submission\_id (UUIDv4) upon the initial click of the submit button.

| Parameter | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| submission\_id | UUID | Yes | Idempotency key guaranteeing unique processing |
| test\_id | UUID | Yes | Reference to the foundational F016/F017 exam |
| duration\_ms | Integer | Yes | Total time elapsed across the entire session |
| answers | Array | Yes | Matrix of question\_id, selected\_option, and time\_spent |
| telemetry | Array | Yes | Sequential list of raw atomic behavior changes |

If a network timeout occurs and the user forces a retry via page reload, the locally persisted submission\_id is re-transmitted. The backend recognizes the duplication, bypasses database insertion, and successfully returns the existing polling task reference.1

### **Contract: F031 Performance Score and F045 Recovery Missions**

| Object Node | Field | Type | Description |
| :---- | :---- | :---- | :---- |
| **Score Synthesis** | readiness\_index | Float | Multi-factor holistic score mapped from 0.0 to 100.0 |
|  | accuracy\_variance | Float | Precision distribution across subjects |
|  | momentum\_classification | Enum | Algorithmic trend analysis (ACCELERATING, PLATEAU, DECLINING) |
| **Mission Pipeline** | mission\_id | UUID | Unique identifier for the generated recovery track |
|  | target\_topic\_id | UUID | Linkage to specific F012 granular taxonomies |
|  | root\_cause\_tag | String | Cognitive or execution failure mapped from F044 Mistake Vault |
|  | prescription\_type | Enum | The targeted action (PRACTICE, REVIEW, CONCEPT) |

## **ASYNC\_PROCESSING\_SPEC.md: Frontend Integration for Celery Background Analytics**

The multi-factor Performance Score (F031) and Recovery Mission generations (F045) rely on intricate algorithmic models referencing deep historical data.1 Generating these analytics synchronously during the F026 Attempt Submission request would exceed standard HTTP timeout thresholds and provide a severely degraded user experience.1 Consequently, the FastAPI application immediately returns a 202 Accepted status alongside a Celery task\_id rather than the completed data payload.1 The frontend architecture must elegantly navigate this paradigm of eventual consistency.

### **Adaptive Exponential Backoff Polling**

To monitor the background analytical generation, the frontend implements a status polling loop. However, implementing a static 1-second interval creates a severe system vulnerability known as the Thundering Herd Problem.13 If an entire cohort of NEET aspirants finishes a 180-minute mock examination simultaneously, thousands of clients hitting the status endpoint every second will rapidly exhaust backend connection pools.13  
The solution integrates an adaptive exponential backoff algorithm customized with randomized jitter.4 The React Query configuration dictates the polling interval dynamically. The delay for the ![][image1]\-th polling attempt is computed as:  
![][image2]  
Where the parameters are defined as:

* ![][image3]  
* ![][image4] to ![][image5] 15  
* ![][image6]

The corresponding custom hook dynamically evaluates the refetchInterval parameter:

JavaScript  
export const useAnalyticsTaskPolling \= (taskId) \=\> {  
  const \= useState(0);

  return useQuery({  
    queryKey: \['task', taskId\],  
    queryFn: () \=\> fetchTaskStatus(taskId),  
    enabled: Boolean(taskId),  
    refetchInterval: (data) \=\> {  
      // Terminate polling upon definitive state transition  
      if (data?.state \=== 'SUCCESS' || data?.state \=== 'FAILURE') return false;  
        
      // Calculate delay with maximum cap of 10 seconds  
      const backoffDelay \= Math.min(1000 \* Math.pow(1.5, retryCount), 10000);  
      const jitter \= Math.floor(Math.random() \* 500);  
      setRetryCount(c \=\> c \+ 1);  
      return backoffDelay \+ jitter;  
    },  
  });  
};

This mathematical structure guarantees that if the Celery worker queue is congested, the client progressively decreases its polling frequency (e.g., 1.5s, 2.25s, 3.37s) until it hits the capped ceiling, preventing excessive server load.14 Jitter ensures that even if hundreds of clients submit at the exact same microsecond, their subsequent polling requests are distributed across a wide temporal window, smoothing the traffic curve.13

### **Explicit Interventions and Manual Refetching**

The adaptive polling sequence effectively handles the chronological waiting period. However, the system must also support explicit human action. If a user temporarily navigates away from the loading screen and later clicks a persistent "Refresh Dashboard" button, the architecture mandates that this user action instantly aborts the existing backoff multiplier schedule.5 The click event triggers an immediate query invalidation, forcing an instant status check. As specified by asynchronous design principles, "The polling cadence handles the 'what's happening now' question; explicit refetches handle the 'I just did something' question".5 Once the Celery task achieves a SUCCESS state, the frontend seamlessly executes a massive cache invalidation for all analytical query keys, instantly painting the UI with the fresh data.5

## **AUTHENTICATION\_UX\_SPEC.md: Identity Lifecycle and Access Provisioning**

The Authentication module (F001, F002) is the gatekeeper for longitudinal data tracking.1 Securing highly sensitive assessment records requires financial-grade access controls.1  
The application utilizes stateless JSON Web Tokens issued by the backend. The frontend handles the storage and transmission of these credentials via secure HttpOnly cookies where feasible, falling back to highly restricted memory configurations if cross-origin complexities mandate it.  
Crucially, standard JWTs possess limited operational lifespans for security purposes. A Full NEET Mock (F016) requires exactly 180 minutes to complete.1 If the student's access token expires at minute 120, standard application logic would instantly reject their next action and forcefully eject them to the /login screen, completely ruining the mock examination experience and causing severe emotional distress.1  
To prevent this catastrophic UX failure, the system integrates a silent refresh utility mirroring the getAccessTokenSilently() mechanism provided by professional SDKs.6 Operating within a background interval or strategically triggered during the test submission sequence, the client securely queries the backend with a long-lived refresh token to acquire a fresh access credential entirely in the background, ensuring uninterrupted user flow without ever presenting an authentication prompt mid-test.6

## **EMPTY\_AND\_ERROR\_STATE\_SPEC.md: Constructing Resilient Interfaces**

Given the targeted demographic of highly stressed NEET aspirants, system interfaces must communicate operational state with extreme clarity. Ambiguous technical errors or blank screens can induce panic.1 The UI architecture defines a strict matrix of transitional and terminal states that every data-fetching component must implement.

| State Category | Trigger Condition | UX Representation Strategy | User Recovery Pathway |
| :---- | :---- | :---- | :---- |
| **Loading** | Cache miss on initial mount | Context-aware Skeleton Loaders matching exact data dimensions | Auto-resolves upon TanStack Query fulfillment |
| **Processing** | Polling active Celery task | Indeterminate Progress Bar with comforting copy (e.g., "Synthesizing your performance DNA...") | Managed entirely via Exponential Backoff |
| **Error** | API 500 / Network Timeout | Isolated Error Boundary Fallback component | Actionable "Retry Connection" button triggering refetchQueries() |
| **Offline** | navigator.onLine \=== false | Non-intrusive persistent toast banner | Interactions buffered in local state; auto-flushed upon reconnection |
| **Empty** | Zero data elements returned | High-quality vector illustration and explanatory text | Deep-link to primary value action |

### **Resolving the Mistake Vault (F044) and Recovery Missions (F045) Empty States**

The dependency gap report highlighted a complete lack of specification for F044 and F045.1 When a newly registered student logs into the platform, they possess zero attempt history.1 Navigating to /vault or /recovery would natively return an empty array, resulting in a blank interface that violates UX principles.  
The specification explicitly addresses this by mandating educational zero-states. When the F044 TanStack Query returns an empty list, the UI must render an interactive overview explaining the biological mechanism of mistake tracking and its impact on score retention. The screen provides a dominant primary button driving the user to the F016 test selection hub to "Establish a Diagnostic Baseline." Similarly, the Recovery Missions empty state provides an interactive mockup of what a completed mission looks like, framing the feature as an elite tool unlocked only after producing actionable data.

## **USER\_JOURNEYS.md: Analytical Visualization and Drill-Down Pathways**

The architecture requires complex visualization pipelines to translate raw behavioral data into the actionable recovery pathways central to the product vision.1 The most prominent journey is the navigation of the Weakness Heatmap (F028) and its subsequent integration with F045 Recovery Missions.1

### **The Subject-to-Topic Diagnostic Funnel**

The interface provides an analytical drill-down utilizing nested route parameters, enabling shareability and deeply linked state management.

1. **Macro Tier: Subject Classification (F010)**  
   * **Path Alignment:** /analytics/heatmap?level=subject  
   * **Visualization:** The user is presented with a macro-level radar chart visualizing aggregate performance across Physics, Chemistry, and Biology.1  
   * **Action Flow:** Clicking a specific subject sector pushes the router state deeper, injecting the subject\_id into the URL parameters.  
2. **Meso Tier: Chapter Classification (F011)**  
   * **Path Alignment:** /analytics/heatmap?subject={subject\_id}\&level=chapter  
   * **Visualization:** A dense, D3.js or Recharts-powered interactive grid. Each cell represents a distinct chapter. The cell's physical size correlates to the volume of historical questions attempted, while the color gradient (shifting from deep green to crimson red) denotes the accuracy percentage.  
   * **Action Flow:** Hovering triggers TanStack prefetching. Clicking a crimson cell signifying critical conceptual weakness pushes the router to the granular tier.  
3. **Micro Tier: Topic Classification (F012) & Recovery Integration**  
   * **Path Alignment:** /analytics/heatmap?chapter={chapter\_id}\&level=topic  
   * **Visualization:** A detailed breakdown cross-referencing specific topics against root-cause failures from the F044 Mistake Vault.  
   * **Action Flow:** The system dynamically renders a highly actionable Weak Topic Recommendation (F047) component. A single click dispatches a mutation to instantiate a localized, highly targeted Unit Test (F017) comprised exclusively of the problematic material.1

### **Defining the F045 Recovery Missions Interface**

The missing F045 UI is engineered as an interactive, Kanban-style orchestrator.1 When the background Celery task completes its synthesis, the frontend retrieves an array of generated Mission schemas. These are rendered within the /recovery route as prioritized interactive cards.  
Each MissionCard visually delineates the root cause (e.g., "Execution Failure in Thermodynamics") and the algorithmic priority weight. Clicking "Initiate Mission" triggers a backend mutation altering the mission state to ACTIVE, while simultaneously mounting a specialized instance of the Test Engine populated solely with targeted remedial questions. Upon successfully concluding the mission, the subsequent status polling resolves, triggering a massive cache invalidation. The kanban board instantly updates, removing the completed mission card and animating an increase in the global Performance Score metric.

## **FRONTEND\_BACKEND\_INTEGRATION\_SPEC.md: The Master Architecture Matrix**

To ensure absolute operational clarity and rapid execution for engineering teams, the 25 core MVP features are synthesized and explicitly mapped across the entire enterprise specification pipeline. This overarching matrix unifies the route structures, visual components, API interactions, caching strategies, and localized states.

| Feature Identifier | Route Topology Boundary | Core Rendered Component | Interaction API Contract | TanStack Cache Strategy | Localized Zustand State |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **F001/F002 (Auth)** | /login, /register | CredentialForm | useAuthMutation() | Set JWT credential; Invalidate \['user'\] keys | Clears sessionSlice artifacts |
| **F003 (Profile)** | /profile | SettingsConfigurator | useProfileQuery() | Retrieve via \['user', id, 'profile'\] | N/A |
| **F006-F012 (Q-Bank)** | /admin/questions | QuestionDataGrid | useInfiniteQuestions() | Paginated \['questions', 'list', filters\] | N/A |
| **F016-F018 (Tests)** | /tests | TestSelectionHub | useTestTemplates() | Cached \['tests', 'templates', type\] | N/A |
| **F023 (Timer)** | /tests/active/:id | PacingTimer | Buffered Sync | Tracked entirely on client-side | Mutates timerSlice |
| **F024 (OMR)** | /tests/active/:id | OMRSimulationPanel | Buffered Sync | Evaluates client-side state mapping | Reads answerSlice |
| **F026 (Attempts)** | /tests/active/:id | HeadlessEventTracker | useSubmitAttempt() | Triggers backend task generation | Flushes telemetrySlice |
| **F027 (Dashboard)** | /dashboard | PerformanceSynthesizer | useAnalyticsPolling() | Adaptive polling on \['task', taskId\] | N/A |
| **F028 (Heatmap)** | /analytics/heatmap | D3HeatmapCanvas | useWeaknessData() | Hierarchical \['analytics', 'heatmap', level\] | Route parameter binding |
| **F031 (Perf. Score)** | /dashboard | RadialMetricGauge | useScoreMetrics() | Invalidated upon task success | N/A |
| **F044 (Vault)** | /vault | CategorizedErrorList | useMistakeVault() | Fetches \['analytics', 'vault'\] | N/A |
| **F045 (Missions)** | /recovery | MissionKanbanBoard | useActiveMissions() | Fetches \['analytics', 'missions'\] | N/A |

### **Final Engineering Mandates**

This cohesive architectural specification successfully transforms the critically underspecified frontend implementation of the NEET Performance Operating System into a highly deterministic, implementation-ready framework. By imposing strict React Router v6 navigation boundaries, strategically isolating synchronous Test Engine interactions within optimized Zustand persistence structures, and delegating massive analytical payloads to TanStack Query orchestrated via mathematically rigorous exponential backoff polling, the system is engineered to handle massive data volumes flawlessly. The resolution of the previously undocumented interfaces for complex analytics guarantees that the product's core vision—transforming raw student failures into actionable, structured recovery paths—can be executed efficiently by engineering teams strictly adhering to these comprehensive models.

#### **Works cited**

1. NEET\_POS\_Engineering\_Blueprint.md  
2. Mastering React Query. Structuring Your Code for Scalability and Reusability \- Medium, accessed on June 19, 2026, [https://medium.com/@uramanovich/mastering-react-query-structuring-your-code-for-scalability-and-reusability-aba1cbe5a216](https://medium.com/@uramanovich/mastering-react-query-structuring-your-code-for-scalability-and-reusability-aba1cbe5a216)  
3. Best way to organize React Query for a team project? : r/reactjs \- Reddit, accessed on June 19, 2026, [https://www.reddit.com/r/reactjs/comments/1mqvj2k/best\_way\_to\_organize\_react\_query\_for\_a\_team/](https://www.reddit.com/r/reactjs/comments/1mqvj2k/best_way_to_organize_react_query_for_a_team/)  
4. Tasks — Celery 5.6.3 documentation, accessed on June 19, 2026, [https://docs.celeryq.dev/en/stable/userguide/tasks.html](https://docs.celeryq.dev/en/stable/userguide/tasks.html)  
5. A Guide to Async Patterns: Django, Celery, asyncio, React \- Bogdan Andrei, accessed on June 19, 2026, [https://bgdnandrew.com/blog/guide-to-async-patterns-django-celery-asyncio-react](https://bgdnandrew.com/blog/guide-to-async-patterns-django-celery-asyncio-react)  
6. React Authentication By Example: Using React Router 6 \- Developer Center, accessed on June 19, 2026, [https://developer.auth0.com/resources/guides/spa/react/basic-authentication](https://developer.auth0.com/resources/guides/spa/react/basic-authentication)  
7. React Protected Routes | Role-Based Authorization | React Router v6 \- YouTube, accessed on June 19, 2026, [https://www.youtube.com/watch?v=oUZjO00NkhY](https://www.youtube.com/watch?v=oUZjO00NkhY)  
8. How can i prevent certain type of user role to access other role route using React Router Dom V6 \[duplicate\] \- Stack Overflow, accessed on June 19, 2026, [https://stackoverflow.com/questions/78251380/how-can-i-prevent-certain-type-of-user-role-to-access-other-role-route-using-rea](https://stackoverflow.com/questions/78251380/how-can-i-prevent-certain-type-of-user-role-to-access-other-role-route-using-rea)  
9. Creating Protected Routes With React Router V6 | by Dennis Ivy \- Medium, accessed on June 19, 2026, [https://medium.com/@dennisivy/creating-protected-routes-with-react-router-v6-2c4bbaf7bc1c](https://medium.com/@dennisivy/creating-protected-routes-with-react-router-v6-2c4bbaf7bc1c)  
10. Implementing Role-Based Access Control in React 18 with React Router v6: A Step-by-Step Guide \- DEV Community, accessed on June 19, 2026, [https://dev.to/m\_yousaf/implementing-role-based-access-control-in-react-18-with-react-router-v6-a-step-by-step-guide-1p8b](https://dev.to/m_yousaf/implementing-role-based-access-control-in-react-18-with-react-router-v6-a-step-by-step-guide-1p8b)  
11. Effective React Query Keys \- TkDodo's blog, accessed on June 19, 2026, [https://tkdodo.eu/blog/effective-react-query-keys](https://tkdodo.eu/blog/effective-react-query-keys)  
12. React Query: How to organize your keys \- DEV Community, accessed on June 19, 2026, [https://dev.to/syeo66/react-query-how-to-organize-your-keys-4mg4](https://dev.to/syeo66/react-query-how-to-organize-your-keys-4mg4)  
13. Retry Celery tasks with exponential back off \- Stack Overflow, accessed on June 19, 2026, [https://stackoverflow.com/questions/9731435/retry-celery-tasks-with-exponential-back-off](https://stackoverflow.com/questions/9731435/retry-celery-tasks-with-exponential-back-off)  
14. Redis \+ Celery task.retry(...) leads to exponential task duplication and memory exhaustion \#9963 \- GitHub, accessed on June 19, 2026, [https://github.com/celery/celery/discussions/9963](https://github.com/celery/celery/discussions/9963)  
15. Advanced Celery: mastering idempotency, retries & error handling \- Vinta Software, accessed on June 19, 2026, [https://www.vintasoftware.com/blog/celery-wild-tips-and-tricks-run-async-tasks-real-world](https://www.vintasoftware.com/blog/celery-wild-tips-and-tricks-run-async-tasks-real-world)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAbCAYAAABIpm7EAAAA10lEQVR4Xu3RrQ9BURjH8bNhY/MS2EwQaDKaYmMjKJIiois2CknX/AMUTVA0RRU0xaYKApspvufec66zO0Ui+G2f3Z3nuffc8yLEP7+UMKpIqrEPOdQQ1y/pBDHFCCc0sUQbA1xQct4mFXSQxRVrRFQvgSN6amylhQzqeKBo9GT9jK5RczLBHjGj1sAdBaPm5KMPQthgAa+qyeccW/Hak5N3a00J+9SGCGCMqG7qDZu/lndwQx5l9I2eNctOGDOQNA5YYSZcy/IL+wLdkTcuD8Hjbvzz3TwBLFQieXz1O1wAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARMAAAAZCAYAAAASRcpqAAAK2ElEQVR4Xu2bCcym1xTH/xO72sdYgnRqqVoaREdRdDSmiF3VHp2Q0jBiLWmRjIqIpShGE1uJiKKxRC1phbchUTQtYowUMYRKCUJK0jaW8+t5juc897vP+z5f5ltmvtx/cvK9z92ee88953/PPc+M1NDQ0NDQ0NDQ0NDQ0LCBcHOTO5ncqKxoOCTBPrKf7Gtgk8lmk1ulso2Mm8h1wN81x2km15j8NwnPvzf5d/f7oyZ3jw5riPeaXKfh3P5k8tfu99Um7zS5TXSYCJT9M/kYvzW567B6Q2CryXPLwoT7mrzL5CMmzze5xbD6BlBGHW1oS58apoy1ksAWzzd5sZwswIfU28hTurJXpLI3dmWg1v9Qx2EmX5Gv9Z8mDx1Wry3O1HAjAvc2udLkbyYPK+rWAmz2Z+Rze2JRhxFfYvJnk2OKukVgXIhoI5HJ/UxebvJt+UHwqWH1/3GSyc9NHiw/sd9mcrHJbVMbflNGHW1oSx/6ZkwZa6WBjWIPMw0jjseaXN/VB+4jP4AymYz13wjYqYOATFB2jUzAC+R1nzW5cVG3FsApxhSE0X5LTniHF3WLwJo3Gpk83eSR8siyRib3MPmlfE8Dtzf5kcmuVIZuKKMuQJ99JnfunqeOtdLgFD7d5LiiHPvATrINs7fscSaTsf4bAax9zFfWDPPIZL2ZfB6ZgCeY/Ed+Ki4nbN1oZBIIB6qRCY5f6jKiv5l8f4MQyv7b5Nfep3bPU8ZaS0wlk42Mg5pMMA6clLrXFXUktp5h8laTk7vnEpwCXE/o+xi5QW5J9Yz/IJO3mJyiumMvIpN7mvzRZK/JHVM5d/cny+cH4ZR3+RqZkLhinm+QXxmO1JCgSO7RPoQ1U5/L1zupO49MPqC6LmmLDtElEc5furKMcNa3d89TxqrhdvIoElu7m1x327vnsCH0x7hEWlvV7wH7Q2TElXu7hpHyFDKZ159ICxt8mcnRJo8q6snNvVBuq9TV9pgx6I/N7dBSm2N9+AppBeabx4B8yeecKN8D5sr1HR0wbg34F+1ZM+uqkUnYND6IL+JvY3uzIggyeZF6p2BhZ5j8XR4W5gzxA+S5CvIOtKXf1SbPTG1QyPdMHp7a/E79QlHEeSZf6trWxgCLyAQl/trkX3KyAoz3Y/n872XyYZOfaHgVKsmEjf+qyQ/ld23ed7nJuerXTm4gchIIdTjDo+XvR4ffkDvMemEemYzpMpeHU5b9y/IpY9XwGnkODl1BTNgAyWLIieT6SfIE6UvldsdYr76hpxPLhXLdzzSMfqaQyVbV+58qv8ZjHwj28p1Uf4L8SoeNYlskO9nnyA1hH282+Y3cfo+SJ/kvko8BGdKXiG+7/B3vlueX7iIHpPEHuV5IZn9aHv29Sb4u9JLxJLm/oMNnmbzf5AoNdc/Bhr0STaILDlV8sAwaVhRBJiyehYR81+TLJsdqeEI/wuRak491z9SRUd8vP23Aa+Uhb+53lvqF8k7u9kd0zzEGTr+5KwOLjJPNmqmPrOI553ggnH0mZ3fPoCQTDONSOTHRHqB8DC9CexDzzHMHu02ek55reJ58M6fKZfIk+HIwRiahl5ous47jWlv2z2QydawxbJOT7zfVn94cXuj0KvVrZv8u0NDx0T92lcvAFDIBZX8ONfJu+RAjwuWgoD5yQ7tT/QPl0dtLumf2/Tq5vQDsFzsOWyZKgUA5dAIQ0OflB1ipA2w1bPDWcj/8mvrP3vjjP+SRUsZODXVPJHKJfIwAkdOakEn5EhRPyE9OgigknJPyO2gYrTBGXgiTxhE/KA8rY+Pow2bt1VBBgA0tDXGRcaJ0COB6efj5OPl8eX+gNCBQkgmgrmag2RgB7+F9u7pniIgTNgxgPTFGJuE0NV1mHWOAi8hk6lhjiLHyHsW8ywOI8WYa7kutbCqZgNwf+8MOuZpxtSUqvZncAZkHc8SesKtAODjjBLFiz/maHWPH+GU9YF5htyDmS5QWiPERfjMnbK12lSyvOcwZH+Rg5TcRc8xp1TBGJiAcn0iEiCQAi+6ROzKGdZmGC8HBviAfNwRCgkxi4wkLcySEnCMPRwOLjBOFotj98qgo1lJGWcjp6hVZIxNOCAyKKxJCSIwhlcYYUcxMvsGcSISjBwPGyASM6TKXZ9LIKMunjDWGeY5fvpfnmVaPTADXVyLBsFOu9pAqoC02wHW8tCcik3jHTMP5BOKwm2lpfdgqUTyozbckk3imXbZdUJIJvvYeDX2QK+RqfrqfSyYx+Vz/eHlmn39YFiFaGZmATXJiOEV+B2VTTlOf5LtAiz83LzJOHJlxuXrwPk4S5sp9cx5KMuHvD+T32q1dWRhoaYxgl5xgCV33yEPfRYDIeM9UwRBz9DcFYZClUwLu1zVd0pbwmgMiyLnsH7o4s3ueMtYY5jl++V6eZ1pdMgHomYQn66MPOUFyg0QJOXooEe+YaSlZgDiMsav8qR2E34Wt1uZ7IGQSwI5OVn+4k1/ZNGixgphHJkfIjeNaeWQSYds+DcP6IBMyx6+Xn9Q51xB3RDYSAuK+XFMw2eYt6Zn2NQWB+HcmV6m/Z+PU3E8x9gzef5x68irJJMLZuPeCTCZs+NGpLvRCguvjmhY6Hi5Plk2Vp8mvk8vBmFMC9oOwN4fssZ8Iv8NY4zlAH/IC0XfKWGOY5/jlvGuOXyubN+Y8MkHOU5/rA9gSNsVYcViVhxO2x/Ude+IaUbt2HCVPglJfI1hsFFuNg6g235JMAATHYcyhnFGSCc95LAiEr7Mz1YlvRTBGJnwO4w5LHSc/iguD2a9+A+JLCAvZYfI++Sc0yCNOVhbCGLE42sH4O7s6sFmeSecvoJz318gEZyarzgkCyQXoA/NiDGxmgAjijK4e1MiEdWYCJIqijLZInkOsh/p5/3R9rREGid5irQH0yteq3akMx8HQ8xpI7BH2o2MQRnip+hB56lg1bJMnYHPScx6Z7NUw30DZTCtHJkTNOZnJIfl9+Zhh2xx8W1IbyCUIBlKBFN6h/nMv+vmEnEweIv9Sld8R+stRAmSD/iL6AzUyIWLC7rM9M89PahhFoQveEf4EdsnJs7SNAwbOwj83xiFCWDSGFP8H5hcmz9bwmzh3zF/JP39xd/yi3AnJXtPvlfL8BNcGDJA2OD4Gnu9rx8sz5SSzON0vlo8NuELFHJBr5PNC2ZyIbN7ZWhrqAQiM98PehHafk4/Pu9lcDCWPix6oO18+LsZGHxS/Rx6VMU7J5pxarDlHaOsFIoTQTV7bTzWMqI6R56pIrBP94CSRywrw+1y5k/HJEiLBoWNvAlPGKsFBk+eIXtkr5hplV8odlb95LacWZeQiWBu2QtREGWOzd6/q+kRb9vz4Sv9j5baJ0/EXW8VmyZ2Fwx2mPhrANvjCSVSR18nY2PIVclv7uob6ur98Dhd29eiTdccY2GCsAWE+kE/2AX5HJAgh45sxHu9jjtGW3CNkwnwu79qg64u0NEJad6BoGA/nDKLhbyjnlukZZysdMVAbZ6UQ7yaLPRXME4LKYfpYyA6ZcJ071IBznKj5/yCKfTlSThJcXccIYspYBzNYJ2sA7D32MrZW7ADbOBBbxhbnvWM5iPch/GZ+eeybdr+ZC3Najh80rDJgdELeHfIrH1FL3HcbGhoaJoMQk2Qcn/JOkH92g1QaGhoalgVCxrPkd1+IJMLjhoaGhoaGhoaGhoaGhoaGhoaGhoYB/gcwlCgtr5K3WwAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHEAAAAZCAYAAAAG2cHnAAAEMklEQVR4Xu2YX8ieYxzHf0IRNX/WRtHeg1mbNPbHgVCLTck40LYmciJhbdPI30hIkixGRJMcGdYo1pQDbxwoHLIDJRGr0Sg1Yfnz/ex3/bqv59r9PO99v7a9vev61Lf3ea77uu/3un5/r/sxq1QqlUqlEtwn/dtB+6QF6Z7KaI6X1khjxfgouOca6UVpi3SVdOLAjA48aO6s64txHnSruRMvLq4dDk6TbpFOKi9MM06WrpWek36U9ktLBmYM51TpbWm9NEtaKn0j7ZJmZPMmJDKShZQcJ71g7df+L2Q3G2Aj0xmceLW0THrE+jlxufSP9JJ0Qhp7wtwft8WkLrQ5kSw8JX0mQ5lzuLlJ+simvxNzsFMfJy6T/pbesaYiRWW8K33vRJsTKZ/r0ucxaWVzyc6V1kqPmkdgOLuEQLjCPLIom3Ozazz/e+nTNH62HVpWz5RWm28Ko9A7AkrxHPM1nyPNM+8lw9ZytOjrRCod+4y9k9UfWL9nHKR0IsZ6KI2XrJD+NE91jPeA9IN5Lc+hVO6WXpHOkzaaR9x10kXSa9LPSXxmHuPAxm6WPjePVJz1tPShdFaas0naa77uN6SXzfvRe+aGmCr6OjEHuxPs3E+PxA6dCSf+ksRn1OZEMjBP9YiccWvKIg354zQeBmVx1H7+AnPHk8pySqD8Kl2ejZHVb9mgkzAUG6YUEc3012es6S0lZPwX5hWgq244eGd3JuvE283/H4H5sE2iopSZiMF4UJsTiRYMlpe216XvzEsikG1lY2b+6dZE1zAnUlZ2Sl9JM7NxYD0HpMvS93Bi2zqnisk6MSBAt5ufUHu91pVOBAy1Ifuec760zTxy3pW+tUEntj2vZJgTZ5tvoByHeG5UgWPRicBBkn32ag1tRs9Ppzl3mC/yTmuysczEtueVlE48Q1psnn1kIf2QzM2J596YvocTR/2fHNbLuxjr7KoykCairxOvlDabny+C2Fdu0wnpYnQIA+e9DsKJF0r3SJeYH344leYQFMyB0oks/HnzfsZBhcNSvjHgefTKC9L3vk7k//PLyKoe6lXSbLQTCaIxa06iYYPy/MF+GGtrKUOJ95KJylI4cdyaCCWyvzR34qXSU+ZZzGlzjzQ/zQMyKPokzqL2R8ZRvu9P1xaZH7B4jwzow59Jz1rTV8OJvd6njjDY8Hdr/4WLQx12JkjZP9oqfS0tTHPY2+Np3t1pbCSciH4yvyHEd/pdWykF3gvJhk+kV80XRORwH0d8Ih24n98Bf5PelHZIj9ngb4JLze/bZd5b52TX6Lu8Q75v/n8IHrI87qcE/WXNugkYfv2YCtgrNstP9rEm1hlgpz+ke60JRKoNJ3lO1gT5k+b7imQ4YkRvITtiMRFZJZSOUb2FhfKsYQvmpZ7DzrDrxwLYk7JN+cbR2LVSqVQqlUqlUqlUjjb/AcQtAQnhvokDAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABNklEQVR4Xu2UsStGURiHX0kRUZRicZWUQSkWyvalDMqilNliYKP8KTaDsiuZzCbFqOQj/gMGg3h+zjk597h9X/dmQPepp777nvd+v9s5p9es5i+S4XpabME0ruEwdmAfLuJG3BSYwi08xzc8zC+3RB/1nviAM3FTQEGruICPVi5oBW+9F7iD/bmOAkbw3soH7aXFdvz6IPWfmdu+O9zEzrgppWqQLtGgf54wd8675m5hIVWCur0B/fmRubDxqJ6jSlARel/XfDldCJQNmsQnPMGeqB6CtK2FtAsawFH72vtZfLF8UNg61bVeSAhSY3qQQ3iFrzjvawpWb+afhX7r9h1gV1T/pGHu8DR+whh5xmtzs0xohp3iDY75mpjDS9zHbWzisbmP+HF6ccncGMvs+27U1PxnPgCbPkHDJSL7vwAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,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>