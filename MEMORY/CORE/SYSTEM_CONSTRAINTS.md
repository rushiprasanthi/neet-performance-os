# SYSTEM_CONSTRAINTS.md

## Engineering Constraints

### Architecture

* Domain-Separated Monolith
* FastAPI Backend
* React + Vite Frontend
* PostgreSQL Primary Database
* Redis Cache
* Celery Background Workers
* Nginx Gateway

### Authentication

* JWT Access Tokens
* Access Token Lifetime = 15 Minutes
* Refresh Token Rotation
* Refresh Token Lifetime = 7 Days
* RBAC Required
* Audit Logging Required
* HTTPS Required

### Database

* PostgreSQL 16
* ACID Transactions
* Foreign Keys Required
* Soft Delete Only Where Needed
* Never Delete AttemptAnswer Records
* Index All Analytics Query Paths

### Assessment Constraints

* Attempt Submission Must Be Idempotent
* Timer State Must Be Recoverable
* Analytics Must Never Block Submission
* Background Processing Required For Aggregation

### Intelligence Constraints

* Performance Scores Must Be Versioned
* Historical Scores Must Remain Reproducible
* Weakness Detection Must Be Explainable

### Recovery Constraints

* Recovery Recommendations Must Be Traceable
* Recovery Missions Must Reference Actual Weakness Data

### Performance Constraints

* API Response Time <200ms p95
* Database Query Time <1s p95
* Dashboard Load Time <3s

### Infrastructure Constraints

Current MVP:

* Single FastAPI Instance
* Single PostgreSQL Instance
* Single Redis Instance
* 2 Celery Workers

Growth Path:

* PostgreSQL Read Replicas
* Prometheus
* Grafana
* Multiple FastAPI Workers

Scale Path:

* Redis Cluster
* CDN
* Analytics Cluster
* Worker Autoscaling

### Security Constraints

* Argon2id Password Hashing
* HTTPS Only
* Rate Limiting Required
* Audit Logging Required
* No Secrets In Repository

### Compliance Constraints

* User Data Protected
* Audit Logs Retained
* Attempt History Preserved
* Analytics History Preserved

### Explicitly Rejected Constraints

Do Not Use:

* In-Memory Message Queues
* Session-Based Authentication
* Hard Delete Attempt Data
* Synchronous Analytics Processing
* Microservices During MVP
