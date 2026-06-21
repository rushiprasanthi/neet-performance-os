# Identity Domain - User Registration Implementation

## Overview

The Identity domain handles authentication, authorization, and user account management. This implementation provides:

- User registration with email validation
- Password hashing with Argon2id
- Automatic profile creation
- Audit logging
- RBAC infrastructure (roles, permissions)

## Architecture

### Directory Structure

```
backend/app/domains/identity/
├── models.py                # SQLAlchemy ORM models
├── schemas.py               # Pydantic request/response schemas
├── routes.py                # FastAPI endpoints
├── repositories/
│   ├── __init__.py
│   └── user_repository.py   # Data access layer
└── services/
    ├── __init__.py
    └── auth_service.py      # Business logic
```

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, active, suspended
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
```

#### Profiles Table
```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    target_score INTEGER,  -- 0-720 for NEET
    target_year INTEGER,
    avatar_url VARCHAR(500),
    notification_prefs JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL
);
```

#### RBAC Tables
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE user_roles (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE role_permissions (
    id UUID PRIMARY KEY,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE
);
```

## API Endpoints

### User Registration

**Endpoint**: `POST /api/v1/auth/register`

**Request**:
```json
{
    "email": "student@neet.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created)**:
```json
{
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "student@neet.com",
        "status": "pending",
        "email_verified": false,
        "profile": {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "first_name": "John",
            "last_name": "Doe",
            "target_score": null,
            "target_year": null,
            "avatar_url": null
        }
    },
    "message": "Registration successful. Please verify your email."
}
```

**Errors**:
- `409 Conflict`: Email already registered
- `422 Unprocessable Entity`: Invalid request (invalid email, weak password)
- `500 Internal Server Error`: Server error during registration

### Identity Health Check

**Endpoint**: `GET /api/v1/auth/health`

**Response (200 OK)**:
```json
{
    "status": "healthy",
    "domain": "identity"
}
```

## Models

### User Model

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: UUID            # Primary key
    email: str          # Unique email
    password_hash: str  # Argon2id hash
    email_verified: bool = False
    status: str = "pending"  # pending, active, suspended
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    profile: Profile    # One-to-one relationship
    user_roles: list[UserRole]
    audit_logs: list[AuditLog]
```

### Profile Model

```python
class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"
    
    id: UUID
    user_id: UUID       # Foreign key to users
    first_name: str
    last_name: str
    target_score: int   # 0-720 for NEET
    target_year: int    # Target admission year
    avatar_url: str
    notification_prefs: dict  # JSON preferences
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    user: User
```

### AuditLog Model

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: UUID
    user_id: UUID       # Optional, for system events
    event_type: str     # e.g., "USER_REGISTERED"
    metadata: dict      # JSON event details
    created_at: datetime
    
    # Relationships
    user: User
```

## Services

### AuthService

Handles authentication business logic:

```python
class AuthService:
    async def register(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Register a new user."""
        # Checks for duplicate email
        # Hashes password using Argon2id
        # Creates user and associated profile
        # Logs USER_REGISTERED audit event
        # Returns User object
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using Argon2id."""
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify password against hash."""
    
    async def log_audit_event(
        self,
        user_id: UUID | None,
        event_type: str,
        metadata: dict | None = None,
    ) -> AuditLog:
        """Log an audit event."""
```

## Repository

### UserRepository

Data access layer for User operations:

```python
class UserRepository:
    async def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Create user with profile."""
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
    
    async def update_user(self, user_id: UUID, **kwargs) -> User | None:
        """Update user fields."""
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user and associated data."""
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List users with pagination."""
```

## Schemas

### UserRegisterSchema

Request validation for registration:

```python
class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str | None = None
    last_name: str | None = None
```

### UserResponseSchema

Response format for user data:

```python
class UserResponseSchema(BaseModel):
    id: UUID
    email: str
    status: str
    email_verified: bool
    profile: ProfileResponseSchema | None = None
```

### AuthResponseSchema

Response format for auth endpoints:

```python
class AuthResponseSchema(BaseModel):
    user: UserResponseSchema
    message: str
```

## Database Migration

Migration file: `alembic/versions/001_initial_identity.py`

Creates all Identity domain tables with:
- Proper foreign keys with CASCADE delete
- Indexes on frequently queried columns
- Default values and constraints
- Timezone-aware timestamps

**Run migration**:
```bash
poetry run alembic upgrade head
```

**Rollback**:
```bash
poetry run alembic downgrade -1
```

## Password Security

### Argon2id Hashing

Password hashing uses **Argon2id**, a modern memory-hard algorithm resistant to GPU cracking:

- Memory cost: Default (19 MiB)
- Time cost: Default (2 iterations)
- Parallelism: Default (1 thread)

Configuration in `AuthService`:

```python
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

### Password Requirements

- Minimum 8 characters
- Validated by Pydantic EmailStr for emails
- Hashed before storage

## Usage Example

### In a Route Handler

```python
@router.post("/register", response_model=AuthResponseSchema)
async def register(
    request: UserRegisterSchema,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Register a new user."""
    auth_service = AuthService(db)
    user = await auth_service.register(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
    )
    return {
        "user": user,
        "message": "Registration successful. Please verify your email."
    }
```

### In a Service

```python
# Get user by email
user = await user_repo.get_by_email("student@neet.com")

# Create new user
new_user = await auth_service.register(
    email="new@neet.com",
    password="SecurePassword123!",
    first_name="Jane",
    last_name="Doe"
)

# Verify password
is_valid = AuthService.verify_password("plain_password", user.password_hash)
```

## Testing

Test file: `tests/test_identity.py`

Includes tests for:
- ✅ Successful user registration
- ✅ Duplicate email rejection
- ✅ Invalid email validation
- ✅ Weak password validation
- ✅ Password hashing with Argon2id
- ✅ Password verification
- ✅ Identity health check endpoint

**Run tests**:
```bash
poetry run pytest tests/test_identity.py -v

# With coverage
poetry run pytest tests/test_identity.py --cov=app.domains.identity -v
```

## Integration Points

### 1. Main Application (app/main.py)

Identity router registered at `/api/v1/auth`:

```python
from app.domains.identity.routes import router as identity_router

app.include_router(identity_router, prefix="/api/v1/auth", tags=["identity"])
```

### 2. Database Models (app/models.py)

Base model and TimestampMixin used by all domain models:

```python
from app.models import Base, TimestampMixin

class User(Base, TimestampMixin):
    pass
```

### 3. Alembic Configuration (alembic/env.py)

Models automatically detected for migrations:

```python
from app.models import Base
import app.domains.identity.models

target_metadata = Base.metadata
```

## Future Enhancements

### Short-term
- Email verification endpoint with token
- Password reset functionality
- Login endpoint with JWT tokens
- Refresh token mechanism
- Profile update endpoint

### Medium-term
- Social login (Google, GitHub)
- Two-factor authentication (2FA)
- Session management
- Account deletion/deactivation
- Email preferences management

### Long-term
- OAuth 2.0 authorization server
- API key generation for integrations
- Advanced RBAC implementation
- Audit log querying/filtering
- Activity timeline/dashboard

## Troubleshooting

### Migration fails: "table 'users' already exists"

Clear database and rerun:
```bash
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

### Password verification failing

Ensure password is hashed before comparison:
```python
# ✓ Correct
is_valid = AuthService.verify_password(plain, user.password_hash)

# ✗ Wrong
is_valid = AuthService.verify_password(plain, plain)
```

### Duplicate email registration not rejected

Ensure UserRepository checks for existing email:
```python
existing = await self.get_by_email(email)
if existing:
    raise ValueError(f"User with email {email} already exists")
```

## References

- [Argon2id Spec](https://github.com/P-H-C/phc-winner-argon2)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)

---

**Created**: June 14, 2026  
**Domain**: Identity (F001 - User Registration)  
**Status**: ✅ Complete
