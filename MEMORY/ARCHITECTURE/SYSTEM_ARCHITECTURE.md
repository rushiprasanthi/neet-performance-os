Architecture Pattern

Domain-Separated Monolith

Domains:
Identity
Content
Assessment
Intelligence
Recovery

Frontend:
React + Vite

Gateway:
Nginx

Backend:
FastAPI

Cache:
Redis

Workers:
Celery

Database:
PostgreSQL

Storage:
Cloudflare R2

Analytics:
Async Background Processing
Verification

Infrastructure provider not specified.
Implemented:

User
Profile
AuditLog

Repository Layer

Service Layer

Registration Endpoint

RBAC Foundation
Authentication Service Updates:

Components:

JWT Service
Auth Service
Redis Token Store
Authentication Dependency Layer

Authentication Data Flow:

Client
↓
Auth Routes
↓
Auth Service
↓
JWT Service
↓
Redis
↓
PostgreSQL

Responsibilities:

JWT generation
Token validation
Token rotation
Login rate limiting
Session management