# System Design (Mapped to UI)

## 1. UI analysis summary
- Login/Registration pages map to auth + identity resolution APIs.
- Beneficiary form + upload map to case/document endpoints.
- Listing + donation pages map to discovery/payment endpoints.
- Role-specific dashboards map to filtered analytics endpoints.

## 2. Entity model
- Users, roles, organizations, beneficiary profiles, cases, case status history, donations, payment transactions, reviews, documents, logs, identity records.

## 3. Backend modules
- `app/api/auth.py`: register/login/refresh/JWT.
- `app/api/beneficiary.py`: submit request, upload docs, status, case history.
- `app/api/donor.py`: browse cases, donate(initiate), donation confirm, donation history.
- `app/api/admin.py`: case review, beneficiary management, stats.
- `app/api/government.py`: cross-org oversight.
- `app/api/analytics.py`: KPI and trends endpoints.

## 4. Identity resolution engine
- National ID normalization + SHA-256 hash for matching.
- AES-GCM encryption for sensitive value at rest.
- MPID generated from stable hash prefix.
- Golden record JSON attached to identity record.

## 5. Pipeline design
- Kafka topic `charity_events` ingests app events.
- Spark structured stream performs cleaning, dedupe, and daily aggregation.
- Curated outputs feed warehouse fact/dim model.

## 6. Analytics KPIs
- Total donations.
- Beneficiary count.
- Case success rate.
- Donation monthly trend.

## 7. Security and governance
- Bcrypt password hashing.
- JWT auth and role-based decorators.
- Encrypted national ID + hash-based duplicate prevention.
- Organization-scoped records for tenant isolation.
- Audit logging and case status history for traceability.
- Document ownership + mime validation and paginated listing APIs.


## 8. Operational reliability
- Health endpoint (`/health`) and readiness endpoint (`/health/ready`) for orchestration checks.
- Centralized JSON error handlers for consistent API responses.
