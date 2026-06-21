Primary Database:
PostgreSQL 16

Topology:

Phase 1:
FastAPI → PostgreSQL

Phase 2:
Read Replica for analytics

Phase 3:
Partition AttemptAnswer

Phase 4:
Analytics extraction to ClickHouse / BigQuery

Most Critical Table:
attempt_answers

Growth Risk:
50M+ rows

Partition Strategy:
attempt_answers_2025
attempt_answers_2026

Persistence Rules:
Never delete historical attempt data.
Verification

Storage sizing not specified.
Authentication Notes:

Refresh Tokens:

NOT stored in PostgreSQL
Stored in Redis only

Audit Logs:
New Events:

LOGIN_SUCCESS
LOGOUT

User Requirements:

email_verified must be TRUE before login