# API ENDPOINTS

## System Health
| Method | Path | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/health/live` | No | Liveness probe |
| `GET` | `/health/ready` | No | Readiness probe |
| `GET` | `/` | No | Root health check |
| `GET` | `/api/v1/auth/health` | No | Identity domain health check |

## Identity - Authentication (`/api/v1/auth`)
| Method | Path | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | No | Register new user. Auto-verifies email. |
| `POST` | `/api/v1/auth/login` | No | Authenticate. Returns JWT, sets Refresh Cookie. |
| `POST` | `/api/v1/auth/refresh` | Cookie | Rotates Refresh Cookie, returns new access JWT. |
| `POST` | `/api/v1/auth/logout` | Optional | Revokes tokens in Redis, clears Cookie. |
| `GET` | `/api/v1/auth/me` | Yes | Returns current user session details. |

## Identity - Profile (`/api/v1/profile`)
| Method | Path | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/profile` | Yes | Get currently authenticated user's profile. |
| `PATCH`| `/api/v1/profile` | Yes | Update target score, year, preferred subjects, etc. |

## Content - Subjects (`/api/v1/subjects`)
| Method | Path | RBAC Required | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/subjects` | `subject.read` | List active subjects (paginated). |
| `POST` | `/api/v1/subjects` | `subject.create` | Create a new subject (name, code, desc). |
| `GET` | `/api/v1/subjects/{id}` | `subject.read` | Retrieve a specific subject by UUID. |
| `PATCH`| `/api/v1/subjects/{id}` | `subject.update` | Update a subject's details. |
| `DELETE`|`/api/v1/subjects/{id}` | `subject.delete` | Soft-delete (deactivate) a subject. |