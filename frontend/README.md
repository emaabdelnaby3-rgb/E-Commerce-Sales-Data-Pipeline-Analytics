# Frontend (React + Vite)

This frontend implements all UI screens requested:

- Login Page
- Registration Page (Beneficiary / Donor / Admin / Government)
- Beneficiary Request Form
- Document Upload Page
- Donation Cases Listing Page
- Donation Page
- Beneficiary Dashboard
- Donor Dashboard
- Charity Admin Dashboard
- Government Admin Dashboard
- Case Review Page
- Analytics Dashboard

## Run

```bash
cd frontend
npm install
npm run dev
```

Set backend URL with `VITE_API_BASE_URL` if needed.

## API Mapping

- Login Page -> `POST /auth/login`
- Registration Page -> `POST /auth/register`
- Session Renewal -> `POST /auth/refresh`
- Beneficiary Request Form -> `POST /beneficiary/requests`
- Document Upload Page -> `POST /beneficiary/documents/upload`
- Beneficiary Case Timeline -> `GET /beneficiary/cases/{id}/history`
- Donation Cases Listing -> `GET /donor/cases?page=1&page_size=20`
- Donation Page (initiate) -> `POST /donor/donate`
- Donation Page (confirm) -> `POST /donor/donations/{id}/confirm`
- Beneficiary Dashboard -> `GET /beneficiary/status`
- Donor Dashboard -> `GET /donor/donations?page=1&page_size=20`
- Charity Admin Dashboard -> `GET /admin/stats`
- Government Admin Dashboard -> `GET /government/analytics/system`
- Case Review Page -> `POST /admin/cases/{id}/review`
- Analytics Dashboard -> `GET /analytics/kpis`, `GET /analytics/donation-trends`
