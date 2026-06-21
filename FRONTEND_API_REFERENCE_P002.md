# P-002 JWT Login - Frontend API Reference

## Overview
This guide shows how to integrate the new authentication endpoints in your frontend.

## Endpoints

### 1. Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Success Response (200)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**
- 401: Invalid credentials (wrong password or user not found)
- 403: Email not verified
- 429: Account locked (too many failed attempts)
- 500: Server error

**Important**: 
- Refresh token is automatically set as httpOnly cookie
- Store access_token in memory (not localStorage for security)
- Refresh cookie is managed automatically by browser

### 2. Get Current User
```
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

**Success Response (200)**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "status": "active",
  "email_verified": true,
  "first_name": "John",
  "last_name": "Doe",
  "avatar_url": null
}
```

**Error Responses:**
- 401: Missing or invalid token
- 500: Server error

### 3. Refresh Token
```
POST /api/v1/auth/refresh
(No body needed - refresh_token cookie is sent automatically)
```

**Success Response (200)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Notes:**
- New refresh token automatically set in httpOnly cookie
- Old refresh token is invalidated
- Access token TTL: 15 minutes

**Error Responses:**
- 401: Missing or invalid refresh token
- 500: Server error

### 4. Logout
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**Success Response (204)**
- No content returned
- Refresh token cookie is automatically cleared
- All user's refresh tokens are revoked

**Error Responses:**
- 401: Missing or invalid token
- 500: Server error

## Frontend Implementation Example

### TypeScript/React Implementation

```typescript
// authService.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/auth';

// Create axios instance with credentials support (for cookies)
const authClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important: allows cookies to be sent/received
});

// Store access token in memory
let accessToken: string | null = null;

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  status: string;
  email_verified: boolean;
  first_name?: string;
  last_name?: string;
  avatar_url?: string | null;
}

// Login
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  try {
    const response = await authClient.post<TokenResponse>('/login', credentials);
    accessToken = response.data.access_token;
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 429) {
        throw new Error('Account locked. Too many failed login attempts. Try again later.');
      }
      if (error.response?.status === 403) {
        throw new Error('Email not verified. Please check your email.');
      }
      if (error.response?.status === 401) {
        throw new Error('Invalid email or password.');
      }
    }
    throw error;
  }
}

// Get current user
export async function getCurrentUser(): Promise<User> {
  if (!accessToken) {
    throw new Error('Not authenticated');
  }
  try {
    const response = await authClient.get<User>('/me', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      accessToken = null;
      throw new Error('Session expired');
    }
    throw error;
  }
}

// Refresh token
export async function refreshToken(): Promise<TokenResponse> {
  try {
    const response = await authClient.post<TokenResponse>('/refresh');
    accessToken = response.data.access_token;
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      accessToken = null;
      throw new Error('Refresh token expired. Please login again.');
    }
    throw error;
  }
}

// Logout
export async function logout(): Promise<void> {
  if (!accessToken) return;
  try {
    await authClient.post('/logout', {}, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
  } finally {
    accessToken = null;
  }
}

// Get stored access token (for requests)
export function getAccessToken(): string | null {
  return accessToken;
}

// Set access token (for re-hydration)
export function setAccessToken(token: string | null): void {
  accessToken = token;
}
```

### React Hook Example

```typescript
// useAuth.ts
import { useState, useCallback, useEffect } from 'react';
import * as authService from './authService';

export function useAuth() {
  const [user, setUser] = useState<authService.User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load user on mount
  useEffect(() => {
    const token = authService.getAccessToken();
    if (token) {
      loadUser();
    }
  }, []);

  const loadUser = useCallback(async () => {
    try {
      setIsLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setError(null);
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : 'Failed to load user');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleLogin = useCallback(async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const tokens = await authService.login({ email, password });
      await loadUser();
      return tokens;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [loadUser]);

  const handleLogout = useCallback(async () => {
    try {
      setIsLoading(true);
      await authService.logout();
      setUser(null);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRefresh = useCallback(async () => {
    try {
      await authService.refreshToken();
      await loadUser();
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : 'Session expired');
      throw err;
    }
  }, [loadUser]);

  return {
    user,
    isLoading,
    error,
    login: handleLogin,
    logout: handleLogout,
    refresh: handleRefresh,
  };
}
```

### Login Component Example

```tsx
// LoginForm.tsx
import { useState } from 'react';
import { useAuth } from './useAuth';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      // Error is handled by useAuth hook and displayed via error state
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={isLoading}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        disabled={isLoading}
        required
      />
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### API Client Interceptor (Auto-Refresh)

```typescript
// apiClient.ts
import axios, { AxiosInstance } from 'axios';
import * as authService from './authService';

export function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    withCredentials: true,
  });

  // Add authorization header
  client.interceptors.request.use((config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Handle token refresh on 401
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          await authService.refreshToken();
          // Retry original request with new token
          const token = authService.getAccessToken();
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return client(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
}

export const apiClient = createApiClient();
```

## Security Best Practices

1. **Never Store Access Tokens in localStorage**
   - Keep them in memory only
   - They have short TTL anyway (15 minutes)

2. **Enable Credentials for Cookie Transport**
   - Use `withCredentials: true` in axios
   - Refresh token cookie automatically sent with requests

3. **Use HTTPS in Production**
   - Change `REFRESH_TOKEN_COOKIE_SECURE = True` in backend
   - Cookies won't work over HTTP (secure flag)

4. **Handle 401 Responses**
   - Implement automatic token refresh
   - If refresh fails, redirect to login

5. **Clear Tokens on Logout**
   - Call logout endpoint (revokes all tokens)
   - Clear memory state
   - Delete any session data

## Token Lifecycle

```
User Login
    ↓
Access Token: 15 minutes (in memory)
Refresh Token: 7 days (in httpOnly cookie)
    ↓
[Make API Requests with Bearer Token]
    ↓
Access Token Expires (401 response)
    ↓
Auto-Refresh using Cookie
    ↓
New Access Token: 15 minutes
New Refresh Token: 7 days (cookie updated)
    ↓
[Continue with new token]
    ↓
... repeat until refresh token expires
    ↓
Refresh Token Expires
    ↓
Redirect to Login
```

## Rate Limiting & Account Lockout

- After 5 failed login attempts
- Account locked for 15 minutes
- HTTP 429 Too Many Requests response
- Counter stored in Redis (auto-expires after 15 min)

Example error handling:
```typescript
try {
  await login(email, password);
} catch (error) {
  if (error.response?.status === 429) {
    showError('Too many failed attempts. Try again in 15 minutes.');
  }
}
```

## Troubleshooting

### "Missing refresh token" on /refresh
- Make sure cookies are enabled
- Check that `withCredentials: true` is set in axios
- Verify CORS settings allow credentials

### "Invalid or expired token" when refreshing
- 7-day refresh token TTL has expired
- User needs to login again
- This is expected behavior

### "Email not verified" on login
- User must verify email before first login
- Check for verification email endpoint (separate task)
- Admin can manually mark as verified in database

### Access token not in Authorization header
- Ensure `getAccessToken()` is called before request
- Check that token is actually stored in memory
- Verify interceptor is properly configured
