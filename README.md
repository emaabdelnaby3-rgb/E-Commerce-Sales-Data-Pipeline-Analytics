# Unified Charity Integration Platform

Production-oriented reference implementation covering:
- Flask backend APIs with JWT + RBAC + tenant scoping
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
- Tenant-aware organization filtering in admin analytics endpoints
- National ID SHA-256 hash (dedupe) + AES-GCM encryption (confidentiality)
- Audit log records and case status history for traceability
- Beneficiary document ownership checks and mime/type validation

## Business workflows

- Case lifecycle: pending -> approved/rejected/needs_info -> funded -> closed
- Donation flow: initiate payment (`pending`) -> confirm payment (`succeeded`) -> distribute to case
- Admin review workflow with decision + notes tracking and explicit status history entries
- Donor/Case listings support pagination for production-scale UI grids
