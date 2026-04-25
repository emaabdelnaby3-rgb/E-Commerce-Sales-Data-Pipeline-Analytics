# Frontend Integration Contract

This folder contains API contracts and visualization mappings for the UI screens.

## Screen -> API Mapping

- Login Page -> `POST /auth/login`
- Registration Page -> `POST /auth/register`
- Session Renewal -> `POST /auth/refresh`
- Beneficiary Request Form -> `POST /beneficiary/requests`
- Document Upload Page -> `POST /beneficiary/documents/upload`
- Donation Cases Listing -> `GET /donor/cases`
- Donation Page -> `POST /donor/donate`
- Beneficiary Dashboard -> `GET /beneficiary/status`
- Donor Dashboard -> `GET /donor/donations`
- Charity Admin Dashboard -> `GET /admin/stats`
- Government Admin Dashboard -> `GET /government/analytics/system`
- Case Review Page -> `POST /admin/cases/{id}/review`
- Analytics Dashboard -> `GET /analytics/kpis`, `GET /analytics/donation-trends`

## Visualization logic

- KPI cards: total donations, beneficiaries count, case success rate (`/analytics/kpis`).
- Line chart: donation trends by month (`/analytics/donation-trends`).
- Pie chart: case status breakdown (`/analytics/case-breakdown`).
- Government table: organization performance (`/government/organizations/overview`).
