import { useEffect, useState } from 'react'
import api from '../services/api'

function AnalyticsDashboardPage() {
  const [kpis, setKpis] = useState(null)
  const [trends, setTrends] = useState([])

  useEffect(() => {
    api.get('/analytics/kpis').then(({ data }) => setKpis(data)).catch(() => setKpis(null))
    api.get('/analytics/donation-trends').then(({ data }) => setTrends(data)).catch(() => setTrends([]))
  }, [])

  return (
    <section>
      <h1>Analytics Dashboard</h1>
      {kpis && (
        <div className="cards-grid">
          <div className="card">Total Donations: {kpis.total_donations}</div>
          <div className="card">Beneficiaries: {kpis.number_of_beneficiaries}</div>
          <div className="card">Case Success Rate: {kpis.case_success_rate}%</div>
        </div>
      )}
      <h2>Donation Trends</h2>
      <ul>
        {trends.map((row) => (
          <li key={row.month}>{row.month}: {row.amount}</li>
        ))}
      </ul>
    </section>
  )
}

export default AnalyticsDashboardPage
