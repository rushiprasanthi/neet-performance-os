# P-002 JWT Login - Comprehensive Test Plan

## Pre-requisites
1. Redis running on `localhost:6379` or configured in `.env`
2. PostgreSQL running with NEET database
3. Backend running on `http://localhost:8000`
4. Email verification already done or user has `email_verified=True` in database

## Test Scenarios

### Scenario 1: Valid Login Flow
**Objective**: User with verified email can login and receive tokens

**Setup**:
```sql
-- Create test user in database
INSERT INTO users (id, email, password_hash, email_verified, status, created_at, updated_at)
VALUES (
  'test-user-001'::uuid,
  'student@neet.com',
  -- Argon2 hash of 'SecurePassword123!'
  '$argon2id$v=19$m=65536,t=3,p=4$...',
  true,  -- Email verified
  'active',
  now(),
  now()
);
```

**Test Steps**:
1. Send POST request to `/api/v1/auth/login`
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@neet.com","password":"SecurePassword123!"}'
   ```

2. Verify response:
   - Status: 200 OK
   - Body contains `access_token` (non-empty string)
   - Body contains `token_type`: "bearer"
   - Body contains `expires_in`: 900 (seconds)
   - Response headers contain `set-cookie` for `refresh_token`

3. Extract tokens:
   - Access token from JSON body
   - Refresh token from Set-Cookie header

**Expected Result**: ✅ PASS
- Access token is valid JWT
- Refresh token cookie is httpOnly/Secure/Strict
- User can proceed to next requests

---

### Scenario 2: Rate Limiting - Account Lockout After 5 Failed Attempts

**Objective**: Account gets locked after 5 failed login attempts within 15 minutes

**Setup**: Use the same user from Scenario 1

**Test Steps**:

1. **Attempt 1-4**: Send 4 requests with wrong password
   ```bash
   for i in {1..4}; do
     curl -X POST http://localhost:8000/api/v1/auth/login \
       -H "Content-Type: application/json" \
       -d '{"email":"student@neet.com","password":"WrongPassword"}'
   done
   ```
   
   Expected: 401 Unauthorized (each time)

2. Check Redis counter:
   ```bash
   redis-cli get "failed_attempts:student@neet.com"
   # Output: "4"
   ```

3. **Attempt 5**: Send 5th request with wrong password
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@neet.com","password":"WrongPassword"}'
   ```
   
   Expected: 429 Too Many Requests
   Response body: "Account locked due to too many failed login attempts"

4. **Test Lockout**: Try with correct password
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@neet.com","password":"SecurePassword123!"}'
   ```
   
   Expected: 429 Too Many Requests (still locked)

5. **Test Auto-Expiry**: Wait 15 minutes (or simulate in Redis)
   ```bash
   redis-cli del "failed_attempts:student@neet.com"
   ```
   
   Try login again with correct password
   Expected: 200 OK (lock expired)

**Expected Result**: ✅ PASS
- 401 for each failed attempt (4 times)
- 429 on 5th attempt and while locked
- Account automatically unlocks after 15 minutes

---

### Scenario 3: Email Not Verified

**Objective**: Unverified user cannot login, gets 403

**Setup**:
```sql
INSERT INTO users (id, email, password_hash, email_verified, status, created_at, updated_at)
VALUES (
  'test-user-002'::uuid,
  'unverified@neet.com',
  '$argon2id$v=19$m=65536,t=3,p=4$...',
  false,  -- Email NOT verified
  'pending',
  now(),
  now()
);
```

**Test Steps**:
1. Send login request:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"unverified@neet.com","password":"SecurePassword123!"}'
   ```

2. Verify response:
   - Status: 403 Forbidden
   - Detail: "Email not verified. Please verify your email first."

**Expected Result**: ✅ PASS
- 403 response (not 401)
- Clear error message about email verification

---

### Scenario 4: Invalid Credentials

**Objective**: Wrong email or password returns 401

**Test Steps**:

1. **Non-existent email**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"nonexistent@neet.com","password":"AnyPassword"}'
   ```
   Expected: 401 Unauthorized

2. **Wrong password**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@neet.com","password":"WrongPassword123"}'
   ```
   Expected: 401 Unauthorized

3. **Empty password**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@neet.com","password":""}'
   ```
   Expected: 422 Unprocessable Entity (validation error)

**Expected Result**: ✅ PASS
- 401 for all invalid credentials
- 422 for missing/invalid fields

---

### Scenario 5: Get Current User (GET /me)

**Objective**: Authenticated user can retrieve their profile

**Setup**: Use valid access token from Scenario 1

**Test Steps**:
1. Use valid access token from login response:
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/me \
     -H "Authorization: Bearer {access_token}"
   ```

2. Verify response:
   - Status: 200 OK
   - Response contains user data:
     ```json
     {
       "id": "test-user-001",
       "email": "student@neet.com",
       "status": "active",
       "email_verified": true,
       "first_name": null,
       "last_name": null,
       "avatar_url": null
     }
     ```

3. **Without Bearer token**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/me
   ```
   Expected: 401 Unauthorized

4. **With invalid token**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/me \
     -H "Authorization: Bearer invalid.token.here"
   ```
   Expected: 401 Unauthorized

5. **With wrong auth scheme**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/me \
     -H "Authorization: Basic dXNlcjpwYXNz"
   ```
   Expected: 401 Unauthorized (or 422)

**Expected Result**: ✅ PASS
- 200 with user data for valid token
- 401 for missing, invalid, or wrong token type

---

### Scenario 6: Token Refresh

**Objective**: Client can refresh access token using httpOnly cookie

**Setup**: Have valid refresh_token cookie from login

**Test Steps**:

1. **Send refresh request** (with refresh_token cookie):
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -b "refresh_token={cookie_value}" \
     -H "Content-Type: application/json"
   ```

2. Verify response:
   - Status: 200 OK
   - New `access_token` in JSON body
   - New `refresh_token` in Set-Cookie header
   - Old refresh token is invalidated in Redis

3. **Verify old token is invalidated**:
   ```bash
   # Try to refresh again with OLD refresh_token
   curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -b "refresh_token={old_cookie_value}"
   ```
   Expected: 401 Unauthorized

4. **Without refresh cookie**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/refresh
   ```
   Expected: 401 Unauthorized

5. **With expired refresh token** (wait 7 days or delete from Redis):
   ```bash
   redis-cli del "refresh_token:{uuid}"
   curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -b "refresh_token={expired_uuid}"
   ```
   Expected: 401 Unauthorized

**Expected Result**: ✅ PASS
- 200 with new tokens
- Old token is revoked
- 401 for missing or invalid refresh token
- Can use new tokens immediately

---

### Scenario 7: Logout

**Objective**: Logout revokes all tokens for user

**Setup**: Use valid access token from login/refresh

**Test Steps**:

1. **Send logout request**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/logout \
     -H "Authorization: Bearer {access_token}" \
     -H "Content-Type: application/json"
   ```

2. Verify response:
   - Status: 204 No Content
   - Response has no body
   - Set-Cookie header clears `refresh_token`

3. **Try to use old access token**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/me \
     -H "Authorization: Bearer {old_access_token}"
   ```
   Expected: 401 Unauthorized

4. **Try to refresh with old token**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -b "refresh_token={old_refresh_token}"
   ```
   Expected: 401 Unauthorized

5. **Without Bearer token**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/logout
   ```
   Expected: 401 Unauthorized

**Expected Result**: ✅ PASS
- 204 response for valid token
- All tokens revoked
- Cannot reuse any old tokens
- 401 for missing token

---

### Scenario 8: Audit Logging

**Objective**: All auth events are logged

**Setup**: Have test user from Scenario 1

**Test Steps**:

1. Perform login (successful):
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@neet.com","password":"SecurePassword123!"}'
   ```

2. Check audit logs in database:
   ```sql
   SELECT * FROM audit_logs 
   WHERE user_id = 'test-user-001'::uuid 
   ORDER BY created_at DESC 
   LIMIT 5;
   ```

3. Verify LOGIN_SUCCESS event:
   - `event_type`: "LOGIN_SUCCESS"
   - `metadata` contains: `{"email": "student@neet.com", "timestamp": "now"}`

4. Perform logout:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/logout \
     -H "Authorization: Bearer {access_token}"
   ```

5. Check audit logs again:
   ```sql
   SELECT * FROM audit_logs 
   WHERE user_id = 'test-user-001'::uuid 
   AND event_type IN ('LOGIN_SUCCESS', 'LOGOUT')
   ORDER BY created_at DESC 
   LIMIT 5;
   ```

6. Verify LOGOUT event:
   - `event_type`: "LOGOUT"
   - `metadata` contains: `{"timestamp": "now"}`

**Expected Result**: ✅ PASS
- LOGIN_SUCCESS logged with email
- LOGOUT logged with user_id
- Timestamps are accurate
- All events persisted in AuditLog table

---

### Scenario 9: Token Expiration

**Objective**: Access token expires after 15 minutes

**Setup**: Valid access token from login

**Test Steps**:

1. **Immediately after login** (token should be valid):
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/me \
     -H "Authorization: Bearer {access_token}"
   ```
   Expected: 200 OK

2. **Simulate token expiration** (manually edit JWT payload or wait):
   - Option A: Wait 15 minutes
   - Option B: Create expired JWT manually for testing
   
   ```bash
   # With expired token:
   curl -X GET http://localhost:8000/api/v1/auth/me \
     -H "Authorization: Bearer {expired_token}"
   ```
   Expected: 401 Unauthorized

3. **Refresh should still work** (if refresh_token not expired):
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -b "refresh_token={refresh_token_cookie}"
   ```
   Expected: 200 OK (new access token)

**Expected Result**: ✅ PASS
- Access token accepted immediately after login
- Access token rejected after 15 minutes
- Refresh endpoint can issue new access token

---

### Scenario 10: CORS & Cookies

**Objective**: Frontend can send/receive cookies with CORS

**Setup**: Frontend on `http://localhost:5173`

**Test Steps**:

1. **From frontend**, send login with credentials:
   ```javascript
   fetch('http://localhost:8000/api/v1/auth/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     credentials: 'include',  // IMPORTANT: enables cookies
     body: JSON.stringify({
       email: 'student@neet.com',
       password: 'SecurePassword123!'
     })
   })
   ```

2. Verify:
   - Response status: 200
   - Access token in response body
   - `refresh_token` cookie set by browser
   - Cookie headers: HttpOnly, Secure (in production), SameSite=Strict

3. **Subsequent refresh request**:
   ```javascript
   fetch('http://localhost:8000/api/v1/auth/refresh', {
     method: 'POST',
     credentials: 'include',  // Cookie sent automatically
   })
   ```

4. Verify:
   - New access token returned
   - New refresh token cookie set
   - Browser automatically attaches cookie

**Expected Result**: ✅ PASS
- Cookies sent/received with `credentials: include`
- Frontend can use httpOnly cookies seamlessly
- No JavaScript access to refresh token (by design)

---

## Test Execution Checklist

- [ ] Scenario 1: Valid Login Flow
- [ ] Scenario 2: Rate Limiting (5 failed attempts → 429)
- [ ] Scenario 3: Email Not Verified (403)
- [ ] Scenario 4: Invalid Credentials (401)
- [ ] Scenario 5: Get Current User (/me)
- [ ] Scenario 6: Token Refresh
- [ ] Scenario 7: Logout
- [ ] Scenario 8: Audit Logging
- [ ] Scenario 9: Token Expiration
- [ ] Scenario 10: CORS & Cookies

## Acceptance Criteria Summary

| Criteria | Status | Scenario |
|----------|--------|----------|
| POST /login (valid) → 200, access in body, refresh in cookie | ✅ | 1 |
| POST /login (invalid x5) → 429 | ✅ | 2 |
| POST /login (unverified) → 403 | ✅ | 3 |
| GET /me (valid Bearer) → 200 + user data | ✅ | 5 |
| POST /refresh (valid cookie) → new tokens, old invalidated | ✅ | 6 |
| POST /logout → tokens deleted, cookie cleared | ✅ | 7 |

## Troubleshooting

### Issue: "Account locked" even after 15 minutes
- Check Redis connection
- Manually clear counter: `redis-cli del "failed_attempts:email@example.com"`
- Verify TTL: `redis-cli ttl "failed_attempts:email@example.com"`

### Issue: Cookies not being set
- For local development: Set `REFRESH_TOKEN_COOKIE_SECURE = False` in backend
- Enable CORS credentials in backend
- Use `credentials: 'include'` in frontend fetch/axios

### Issue: "Invalid or expired token" immediately after refresh
- Check that refresh_token is being sent as cookie
- Verify CORS allows credentials
- Check if Redis connection is working

### Issue: Audit logs not appearing
- Verify AuditLog table exists with correct schema
- Check database connection in auth_service
- Verify user exists in database before login

### Issue: JWT decode errors
- Verify `secret_key` in config matches
- Check algorithm is HS256
- Ensure token format is correct (3 parts separated by dots)
