# AUTHENTICATION & SECURITY FLOW

## Technology Stack
- **Hashing:** `argon2-cffi` (Threadpool offloaded).
- **Access Tokens:** Short-lived JWTs (Bearer token in Authorization header).
- **Refresh Tokens:** UUIDs stored in Redis, issued to client via `HttpOnly`, `Secure`, `SameSite=strict` cookies (Valid 7 days).
- **Rate Limiting:** Redis pipeline tracking `failed_attempts:{email}`.

## Registration Flow
1. Client POSTs `UserRegisterSchema` to `/register`.
2. `AuthService` verifies email uniqueness.
3. Password hashed via Argon2. User record created.
4. **MVP Bypass:** `user.email_verified` is forced to `True`.
5. `RBACService.assign_role` defaults to `"student"`.
6. Audit log `USER_REGISTERED` is stored.

## Login Flow
1. Client POSTs `LoginInput` to `/login`.
2. Redis checks `failed_attempts`. Rejects if >= 5.
3. User fetched; Argon2 verifies hash.
4. If invalid: Fail counter incremented in Redis.
5. If valid: Fail counter deleted.
6. `JWTService` creates Access Token (contains `user_id`, `role`).
7. `JWTService` creates Refresh Token UUID and maps it in Redis.
8. Refresh token UUID injected into response `Set-Cookie`.

## Refresh Flow
1. Client POSTs to `/refresh` (no body).
2. Endpoint extracts `refresh_token` from cookies.
3. `JWTService` validates UUID against Redis.
4. Token rotated: Old UUID deleted, new UUID generated and set in Cookie.
5. New Access Token returned.

## RBAC Implementation
- Managed via `roles`, `permissions`, `role_permissions`, and `user_roles` database tables.
- Standard Roles: `admin`, `teacher`, `student`.
- Route security applied via `Depends(require_permission("resource", "action"))` which queries the DB directly ensuring current authorization state.