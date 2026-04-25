-- Star schema for analytics
CREATE TABLE IF NOT EXISTS dim_user (
  user_key BIGSERIAL PRIMARY KEY,
  user_id BIGINT UNIQUE NOT NULL,
  full_name TEXT,
  role TEXT,
  region TEXT
);

CREATE TABLE IF NOT EXISTS dim_org (
  org_key BIGSERIAL PRIMARY KEY,
  organization_id BIGINT UNIQUE NOT NULL,
  name TEXT,
  org_type TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
  date_key INTEGER PRIMARY KEY,
  full_date DATE NOT NULL,
  year INTEGER,
  month INTEGER,
  day INTEGER
);

CREATE TABLE IF NOT EXISTS fact_donations (
  donation_key BIGSERIAL PRIMARY KEY,
  donation_id BIGINT UNIQUE NOT NULL,
  donor_user_id BIGINT,
  case_id BIGINT,
  org_key BIGINT REFERENCES dim_org(org_key),
  date_key INTEGER REFERENCES dim_date(date_key),
  amount NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_cases (
  case_key BIGSERIAL PRIMARY KEY,
  case_id BIGINT UNIQUE NOT NULL,
  beneficiary_user_id BIGINT,
  org_key BIGINT REFERENCES dim_org(org_key),
  date_key INTEGER REFERENCES dim_date(date_key),
  requested_amount NUMERIC(12,2),
  funded_amount NUMERIC(12,2),
  status TEXT
);

-- KPI queries
-- Total donations
SELECT COALESCE(SUM(amount),0) AS total_donations FROM fact_donations;

-- Number of beneficiaries
SELECT COUNT(DISTINCT beneficiary_user_id) AS beneficiaries_count FROM fact_cases;

-- Case success rate
SELECT ROUND(
  100.0 * SUM(CASE WHEN status IN ('funded','closed') THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0),
  2
) AS case_success_rate
FROM fact_cases;

-- Donation trend by month
SELECT d.year, d.month, SUM(f.amount) AS donation_total
FROM fact_donations f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
