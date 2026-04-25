import { useEffect, useState } from 'react'
import api from '../services/api'

function GovernmentAdminDashboardPage() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/government/analytics/system').then(({ data }) => setStats(data)).catch(() => setStats(null))
  }, [])

  return (
    <section>
      <h1>Government Admin Dashboard</h1>
      {stats ? (
        <div className="cards-grid">
          <div className="card">Organizations: {stats.total_organizations}</div>
          <div className="card">Total cases: {stats.total_cases}</div>
          <div className="card">Total donations: {stats.total_donations}</div>
          <div className="card">Success rate: {stats.case_success_rate}%</div>
        </div>
      ) : <p>No data</p>}
    </section>
  )
}

export default GovernmentAdminDashboardPage
