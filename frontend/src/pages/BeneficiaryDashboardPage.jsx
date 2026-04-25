import { useEffect, useState } from 'react'
import api from '../services/api'

function BeneficiaryDashboardPage() {
  const [cases, setCases] = useState([])

  useEffect(() => {
    api.get('/beneficiary/status').then(({ data }) => setCases(data)).catch(() => setCases([]))
  }, [])

  return (
    <section>
      <h1>Beneficiary Dashboard</h1>
      <ul>
        {cases.map((c) => (
          <li key={c.case_id}>{c.title} - {c.status} - {c.amount_funded}/{c.amount_requested}</li>
        ))}
      </ul>
    </section>
  )
}

export default BeneficiaryDashboardPage
