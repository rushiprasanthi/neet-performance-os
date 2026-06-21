# ARCHITECTURAL DECISIONS LOG

## 1. Authentication Token Delivery
**Decision:** Issue Access Tokens in JSON payload and Refresh Tokens in `HttpOnly` secure cookies.
**Reasoning:** Prevents XSS attacks from stealing long-lived refresh tokens while allowing the frontend app to easily use the short-lived access token in Axios Authorization headers.

## 2. Password Hashing Execution
**Decision:** Execute Argon2 hashing via `asyncio.to_thread`.
**Reasoning:** Password hashing is highly CPU-bound. Running it synchronously in FastAPI would block the async event loop, destroying concurrent request performance.

## 3. Rate Limiting via Redis Pipelines
**Decision:** Implement failed login tracking using Redis pipelines (incr + expire).
**Reasoning:** Ensures atomic operations for a sliding-window rate limit (5 attempts / 15 minutes) preventing brute-force attacks securely.

## 4. RBAC Resolution Strategy
**Decision:** Store Roles and Permissions in PostgreSQL and evaluate via a single complex JOIN query (`RBACService.has_permission`).
**Reasoning:** Avoids multiple round-trips to the database while maintaining granular control. Scales better than in-memory or purely token-based claims for dynamic permission updates.

## 5. MVP Email Verification Bypass
**Decision:** Hardcode `user.email_verified = True` during registration.
**Reasoning:** Removes SMTP infrastructure dependency during early Phase 1/Phase 2 development to allow seamless UI testing. Logged as technical debt.