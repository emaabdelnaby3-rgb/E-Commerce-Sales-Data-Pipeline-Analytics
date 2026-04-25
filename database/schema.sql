-- Core OLTP schema for Unified Charity Integration Platform
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    org_type VARCHAR(50) NOT NULL CHECK (org_type IN ('charity', 'government')),
    registration_no VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(25) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TYPE role_type AS ENUM ('beneficiary', 'donor', 'charity_admin', 'government_admin', 'platform_admin');

CREATE TABLE user_roles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role role_type NOT NULL,
    organization_id BIGINT REFERENCES organizations(id),
    UNIQUE (user_id, role, organization_id)
);

CREATE TABLE identity_records (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mpid VARCHAR(64) NOT NULL UNIQUE,
    national_id_encrypted TEXT NOT NULL,
    national_id_hash VARCHAR(64) NOT NULL UNIQUE,
    golden_record_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE beneficiary_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    household_size INT,
    monthly_income NUMERIC(12,2),
    region VARCHAR(120)
);

CREATE TYPE case_status AS ENUM ('draft','pending','needs_info','approved','rejected','funded','closed');

CREATE TABLE cases (
    id BIGSERIAL PRIMARY KEY,
    beneficiary_id BIGINT NOT NULL REFERENCES beneficiary_profiles(id),
    organization_id BIGINT NOT NULL REFERENCES organizations(id),
    category VARCHAR(80) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    amount_requested NUMERIC(12,2) NOT NULL CHECK (amount_requested > 0),
    amount_funded NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (amount_funded >= 0),
    status case_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE case_status_history (
    id BIGSERIAL PRIMARY KEY,
    case_id BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    from_status case_status,
    to_status case_status NOT NULL,
    changed_by_user_id BIGINT REFERENCES users(id),
    reason TEXT,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE case_reviews (
    id BIGSERIAL PRIMARY KEY,
    case_id BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    reviewer_user_id BIGINT NOT NULL REFERENCES users(id),
    decision VARCHAR(20) NOT NULL CHECK(decision IN ('approved','rejected','needs_info')),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    case_id BIGINT REFERENCES cases(id),
    doc_type VARCHAR(80) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE donations (
    id BIGSERIAL PRIMARY KEY,
    donor_user_id BIGINT NOT NULL REFERENCES users(id),
    case_id BIGINT NOT NULL REFERENCES cases(id),
    amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    payment_status VARCHAR(30) NOT NULL,
    is_anonymous BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_user_id BIGINT REFERENCES users(id),
    action VARCHAR(80) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(80) NOT NULL,
    details JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_org ON cases(organization_id);
CREATE INDEX idx_case_status_history_case ON case_status_history(case_id);
CREATE INDEX idx_donations_case ON donations(case_id);
CREATE INDEX idx_identity_hash ON identity_records(national_id_hash);
