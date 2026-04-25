# ERD (Text)

- users (1) --- (N) user_roles
- organizations (1) --- (N) user_roles
- users (1) --- (1) identity_records
- users (1) --- (1) beneficiary_profiles
- beneficiary_profiles (1) --- (N) cases
- organizations (1) --- (N) cases
- cases (1) --- (N) case_reviews
- users (1) --- (N) case_reviews (reviewer)
- cases (1) --- (N) case_status_history
- users (1) --- (N) case_status_history (changed_by)
- users (1) --- (N) documents
- cases (1) --- (N) documents
- users (1) --- (N) donations (donor_user_id)
- cases (1) --- (N) donations
- donations (1) --- (1) payment_transactions
- users (1) --- (N) audit_logs

## Warehouse star schema mapping

- Fact tables: fact_donations, fact_cases
- Dimension tables: dim_date, dim_user, dim_org, dim_case_status, dim_case_category
