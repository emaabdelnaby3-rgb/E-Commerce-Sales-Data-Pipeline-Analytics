# Unified Charity Integration Platform

Production-oriented reference implementation covering:
- Flask backend APIs with JWT + RBAC
- PostgreSQL OLTP schema
- Identity resolution (MPID + golden record)
- Kafka + Spark data pipeline skeleton
- Warehouse star schema and KPI SQL
- Dockerized local deployment

## Folder structure

- `backend/` Flask API implementation
- `database/` transactional schema and ERD notes
- `data_pipeline/` Kafka producer, Spark stream job, warehouse SQL
- `frontend/` UI-to-API mapping for dashboards and pages
- `docker-compose.yml` end-to-end local stack

## Quick start

```bash
cd /workspace/TRY
docker compose up --build
```

Backend health check: `GET http://localhost:5000/health`

## Security controls implemented

- Password hashing using bcrypt
- JWT access + refresh token authentication
- Role-based access control decorators
- National ID SHA-256 hash (dedupe) + AES-GCM encryption (confidentiality)
- Tenant-aware organization field for data isolation

## Business workflows

- Case lifecycle: pending -> approved/rejected/needs_info -> funded -> closed
- Donation distribution: each successful donation increments `amount_funded`; case becomes funded at target
- Admin review workflow with decision + notes tracking
