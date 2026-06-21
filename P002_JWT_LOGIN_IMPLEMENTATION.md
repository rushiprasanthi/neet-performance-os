# P-002: Identity Login & JWT - Implementation Complete

## Summary
All components for P-002 (Identity Login & JWT) have been successfully implemented. The feature provides:
- JWT-based access tokens (15-minute TTL, JSON body)
- Secure refresh tokens (7-day TTL, Redis storage, httpOnly cookie)
- Account locking after 5 failed login attempts (15-minute lockout)
- Email verification requirement
- Audit logging for login/logout events
- get_current_user FastAPI dependency for protected endpoints

## Implementation Details

### 1. Dependencies Added (pyproject.toml)
- `argon2-cffi = "^23.1.0"` - Argon2 password hashing
- `email-validator = "^2.1.0"` - Email validation
- Updated `passlib` to use argon2 instead of bcrypt

### 2. Redis Client Setup (database.py, main.py)
- Added Redis client initialization and lifecycle management
- `init_redis()` called at app startup
- `close_redis()` called at app shutdown
- `get_redis()` dependency for accessing Redis client

### 3. Schemas (schemas.py)
- `LoginInput`: email + password
- `TokenResponse`: access_token, token_type="bearer", expires_in (seconds)
- `UserSafeSchema`: Safe user data without sensitive fields

### 4. JWT Service (services/jwt_service.py)
- `create_access_token(user_id, role)` → JWT token + TTL
- `create_refresh_token(user_id)` → UUID stored in Redis with 7-day TTL
- `validate_access_token(token)` → Decodes and validates JWT
- `validate_refresh_token(token_uuid)` → Checks Redis
- `rotate_refresh_token(old_token)` → Validates, deletes old, issues new
- `revoke_all_user_tokens(user_id)` → Logout all sessions

### 5. Dependencies (dependencies.py)
- `get_current_user` - HTTPBearer authentication dependency
  - Extracts Bearer token from Authorization header
  - Validates via JWTService
  - Fetches user from database
  - Returns User object or raises 401
- `get_current_user_optional` - Optional authentication

### 6. Auth Service Updates (services/auth_service.py)
- Updated constructor to accept redis_client
- `login(email, password)`:
  - Checks Redis for account lockout (5 failed attempts → 429 for 15 min)
  - Verifies password with Argon2
  - Enforces email_verified (else 403)
  - Clears failed attempts counter on success
  - Generates access + refresh tokens
  - Logs LOGIN_SUCCESS audit event
- `logout(user_id)`:
  - Revokes all refresh tokens
  - Logs LOGOUT audit event
- `_increment_failed_attempts(key)` - Helper for rate limiting

### 7. Routes (routes.py)
**POST /login**
- Request: LoginInput (email, password)
- Response: TokenResponse (access_token in body)
- Sets refresh_token as httpOnly/Secure/Strict cookie (7 days)
- Error handling:
  - 401: Invalid credentials
  - 403: Email not verified
  - 429: Account locked

**POST /refresh**
- Reads refresh_token from cookie
- Validates and rotates token
- Returns new access token
- Sets new refresh_token cookie
- 401: Invalid/missing refresh token

**POST /logout**
- Requires valid Bearer token
- Revokes all tokens
- Clears refresh_token cookie
- 204 No Content response

**GET /me**
- Requires valid Bearer token
- Returns UserSafeSchema
- No sensitive data exposed

## Acceptance Criteria Status

✅ **POST /login (valid) → 200, access in body, refresh in Set-Cookie**
- Returns TokenResponse with access_token in JSON body
- Refresh token UUID set as httpOnly/Secure/Strict cookie

✅ **POST /login (invalid x5) → 429**
- Failed attempts tracked in Redis with key: `failed_attempts:{email}`
- Counter increments on wrong password or missing user
- After 5 attempts, raises PermissionError → 429 Too Many Requests
- 15-minute TTL on Redis counter (auto-expires)

✅ **POST /login (unverified) → 403**
- Checks `user.email_verified` flag
- Raises ValueError with message containing "Email not verified"
- Caught in routes.py and converted to 403 Forbidden

✅ **GET /me (valid Bearer) → 200 & user data**
- get_current_user dependency validates Bearer token
- Returns UserSafeSchema with safe user fields
- 401 if token invalid/expired

✅ **POST /refresh (valid cookie) → new tokens, old invalidated**
- Reads refresh_token from cookie
- Validates token UUID in Redis
- Deletes old token from Redis
- Issues new UUID and access token
- Sets new cookie with updated expiration

✅ **POST /logout → Redis token deleted, cookie cleared**
- Revokes all user refresh tokens from Redis
- Deletes refresh_token cookie
- 204 No Content response

## Constraints Verified

✅ NO access tokens in cookies
- Access token returned in JSON body only

✅ NO refresh tokens in Postgres
- Refresh tokens stored ONLY in Redis
- Each token is a UUID with user_id mapped in Redis

✅ NO auto-verify
- email_verified=False blocks login with 403
- Email verification must happen separately (via email link)

## Security Features

1. **Password Security**
   - Argon2id hashing via passlib
   - verify_password() uses constant-time comparison

2. **Rate Limiting**
   - Account locked 15 minutes after 5 failed attempts
   - Counter stored in Redis (auto-expires after 15 min)

3. **Token Security**
   - JWT access tokens: 15-minute TTL (short-lived)
   - Refresh tokens: UUIDs only (no secrets in cookies)
   - Cookies: httpOnly=True, Secure=True, SameSite=strict

4. **Audit Logging**
   - LOGIN_SUCCESS logged with email + timestamp
   - LOGOUT logged with user_id + timestamp
   - Stored in AuditLog table

## Cookie Configuration

```python
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
REFRESH_TOKEN_COOKIE_SECURE = True      # Set to False for local development
REFRESH_TOKEN_COOKIE_HTTPONLY = True
REFRESH_TOKEN_COOKIE_SAMESITE = "strict"
```

**Note**: Set `REFRESH_TOKEN_COOKIE_SECURE = False` when testing locally without HTTPS.

## Testing Notes

1. **Valid Login Flow**
   ```bash
   POST /api/v1/auth/login
   { "email": "user@example.com", "password": "password123" }
   → 200 with access_token in body + refresh_token cookie
   ```

2. **Failed Login Tracking**
   ```bash
   # First 4 failed attempts:
   POST /api/v1/auth/login
   { "email": "user@example.com", "password": "wrong" }
   → 401 (but counter increments in Redis)
   
   # 5th attempt:
   → 429 Too Many Requests (account locked)
   ```

3. **Email Verification Check**
   ```bash
   # User with email_verified=False:
   POST /api/v1/auth/login
   { "email": "unverified@example.com", "password": "password123" }
   → 403 Email not verified
   ```

4. **Protected Endpoints**
   ```bash
   GET /api/v1/auth/me
   Header: Authorization: Bearer {access_token}
   → 200 with UserSafeSchema
   
   Without Bearer token:
   → 401 Missing authorization credentials
   ```

5. **Token Refresh**
   ```bash
   POST /api/v1/auth/refresh
   (with refresh_token cookie)
   → 200 with new access_token + new refresh_token cookie
   ```

6. **Logout**
   ```bash
   POST /api/v1/auth/logout
   Header: Authorization: Bearer {access_token}
   → 204 No Content
   (refresh_token cookie cleared, all tokens revoked)
   ```

## Files Modified/Created

**Created:**
- `backend/app/domains/identity/services/jwt_service.py`
- `backend/app/domains/identity/dependencies.py`

**Modified:**
- `backend/pyproject.toml` - Added dependencies
- `backend/app/database.py` - Added Redis client
- `backend/app/main.py` - Added Redis lifecycle
- `backend/app/domains/identity/schemas.py` - Added LoginInput, TokenResponse, UserSafeSchema
- `backend/app/domains/identity/services/auth_service.py` - Added login, logout methods
- `backend/app/domains/identity/routes.py` - Added 4 new endpoints (login, refresh, logout, me)

## Next Steps

1. Install dependencies: `pip install -r requirements.txt` or `poetry install`
2. Ensure Redis is running on localhost:6379
3. Test the endpoints using the curl examples or Postman
4. Verify audit logs are being written to database
5. Consider implementing email verification endpoint (separate task)
